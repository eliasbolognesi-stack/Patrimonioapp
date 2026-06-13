from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from models import Bem, Setor
from schemas import SetorIn, SetorOut
from security import get_current_user

router = APIRouter(prefix="/setores", tags=["setores"], dependencies=[Depends(get_current_user)])


def to_out(s: Setor, total: int) -> SetorOut:
    out = SetorOut.model_validate(s)
    out.total_bens = total
    return out


@router.get("", response_model=list[SetorOut])
def listar(db: Session = Depends(get_db)):
    counts = dict(db.execute(select(Bem.setor_id, func.count()).group_by(Bem.setor_id)).all())
    rows = db.scalars(select(Setor).order_by(Setor.nome)).all()
    return [to_out(s, counts.get(s.id, 0)) for s in rows]


@router.post("", response_model=SetorOut, status_code=201)
def criar(data: SetorIn, db: Session = Depends(get_db)):
    if db.scalar(select(Setor).where(Setor.nome == data.nome.strip())):
        raise HTTPException(409, "Setor já existe")
    setor = Setor(nome=data.nome.strip(), responsavel=data.responsavel, localizacao=data.localizacao)
    db.add(setor)
    db.commit()
    db.refresh(setor)
    return to_out(setor, 0)


@router.put("/{setor_id}", response_model=SetorOut)
def atualizar(setor_id: int, data: SetorIn, db: Session = Depends(get_db)):
    setor = db.get(Setor, setor_id)
    if setor is None:
        raise HTTPException(404, "Setor não encontrado")
    setor.nome = data.nome.strip()
    setor.responsavel = data.responsavel
    setor.localizacao = data.localizacao
    db.commit()
    total = db.scalar(select(func.count()).where(Bem.setor_id == setor.id)) or 0
    return to_out(setor, total)


@router.delete("/{setor_id}", status_code=204)
def excluir(setor_id: int, db: Session = Depends(get_db)):
    setor = db.get(Setor, setor_id)
    if setor is None:
        raise HTTPException(404, "Setor não encontrado")
    em_uso = db.scalar(select(func.count()).where(Bem.setor_id == setor_id)) or 0
    if em_uso:
        raise HTTPException(409, f"Setor em uso por {em_uso} bem(ns)")
    db.delete(setor)
    db.commit()
