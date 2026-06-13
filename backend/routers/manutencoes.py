from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Bem, Manutencao
from schemas import ManutencaoConcluir, ManutencaoIn, ManutencaoOut
from security import get_current_user

router = APIRouter(prefix="/manutencoes", tags=["manutencoes"], dependencies=[Depends(get_current_user)])


def to_out(m: Manutencao) -> ManutencaoOut:
    out = ManutencaoOut.model_validate(m)
    out.bem_tombo = m.bem.tombo if m.bem else None
    out.bem_nome = m.bem.nome if m.bem else None
    return out


@router.get("", response_model=list[ManutencaoOut])
def listar(status: str | None = None, bem_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(Manutencao).options(joinedload(Manutencao.bem))
    if status:
        stmt = stmt.where(Manutencao.status == status)
    if bem_id:
        stmt = stmt.where(Manutencao.bem_id == bem_id)
    rows = db.scalars(stmt.order_by(Manutencao.data_inicio.desc())).all()
    return [to_out(m) for m in rows]


@router.post("", response_model=ManutencaoOut, status_code=201)
def abrir(data: ManutencaoIn, db: Session = Depends(get_db)):
    bem = db.get(Bem, data.bem_id)
    if bem is None:
        raise HTTPException(404, "Bem não encontrado")
    if bem.status == "baixado":
        raise HTTPException(409, "Bem baixado não pode entrar em manutenção")
    if bem.status == "manutencao":
        raise HTTPException(409, "Este bem já possui manutenção em aberto")

    man = Manutencao(**data.model_dump())
    bem.status = "manutencao"
    db.add(man)
    db.commit()
    db.refresh(man)
    return to_out(man)


@router.post("/{man_id}/concluir", response_model=ManutencaoOut)
def concluir(man_id: int, data: ManutencaoConcluir, db: Session = Depends(get_db)):
    man = db.get(Manutencao, man_id)
    if man is None:
        raise HTTPException(404, "Manutenção não encontrada")
    if man.status == "concluida":
        raise HTTPException(409, "Manutenção já concluída")

    man.status = "concluida"
    man.data_fim = datetime.now()
    if data.custo is not None:
        man.custo = data.custo
    if man.bem and man.bem.status == "manutencao":
        man.bem.status = "ativo"
    db.commit()
    db.refresh(man)
    return to_out(man)
