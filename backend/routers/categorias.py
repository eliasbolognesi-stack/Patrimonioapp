from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from models import Bem, Categoria
from schemas import CategoriaIn, CategoriaOut
from security import get_current_user

router = APIRouter(prefix="/categorias", tags=["categorias"], dependencies=[Depends(get_current_user)])


def to_out(c: Categoria, total: int) -> CategoriaOut:
    out = CategoriaOut.model_validate(c)
    out.total_bens = total
    return out


@router.get("", response_model=list[CategoriaOut])
def listar(db: Session = Depends(get_db)):
    counts = dict(
        db.execute(select(Bem.categoria_id, func.count()).group_by(Bem.categoria_id)).all()
    )
    rows = db.scalars(select(Categoria).order_by(Categoria.nome)).all()
    return [to_out(c, counts.get(c.id, 0)) for c in rows]


@router.post("", response_model=CategoriaOut, status_code=201)
def criar(data: CategoriaIn, db: Session = Depends(get_db)):
    if db.scalar(select(Categoria).where(Categoria.nome == data.nome.strip())):
        raise HTTPException(409, "Categoria já existe")
    cat = Categoria(nome=data.nome.strip(), descricao=data.descricao)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return to_out(cat, 0)


@router.put("/{cat_id}", response_model=CategoriaOut)
def atualizar(cat_id: int, data: CategoriaIn, db: Session = Depends(get_db)):
    cat = db.get(Categoria, cat_id)
    if cat is None:
        raise HTTPException(404, "Categoria não encontrada")
    cat.nome = data.nome.strip()
    cat.descricao = data.descricao
    db.commit()
    total = db.scalar(select(func.count()).where(Bem.categoria_id == cat.id)) or 0
    return to_out(cat, total)


@router.delete("/{cat_id}", status_code=204)
def excluir(cat_id: int, db: Session = Depends(get_db)):
    cat = db.get(Categoria, cat_id)
    if cat is None:
        raise HTTPException(404, "Categoria não encontrada")
    em_uso = db.scalar(select(func.count()).where(Bem.categoria_id == cat_id)) or 0
    if em_uso:
        raise HTTPException(409, f"Categoria em uso por {em_uso} bem(ns)")
    db.delete(cat)
    db.commit()
