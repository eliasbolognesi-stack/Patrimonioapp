from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Baixa, Bem, Usuario
from schemas import BaixaIn, BaixaOut
from security import get_current_user

router = APIRouter(prefix="/baixas", tags=["baixas"])


def to_out(b: Baixa) -> BaixaOut:
    out = BaixaOut.model_validate(b)
    out.bem_tombo = b.bem.tombo if b.bem else None
    out.bem_nome = b.bem.nome if b.bem else None
    out.usuario_nome = b.usuario.nome if b.usuario else None
    return out


@router.get("", response_model=list[BaixaOut], dependencies=[Depends(get_current_user)])
def listar(db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Baixa)
        .options(joinedload(Baixa.bem), joinedload(Baixa.usuario))
        .order_by(Baixa.data.desc())
    ).all()
    return [to_out(b) for b in rows]


@router.post("", response_model=BaixaOut, status_code=201)
def criar(data: BaixaIn, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    bem = db.get(Bem, data.bem_id)
    if bem is None:
        raise HTTPException(404, "Bem não encontrado")
    if bem.status == "baixado":
        raise HTTPException(409, "Este bem já foi baixado")

    baixa = Baixa(bem_id=bem.id, motivo=data.motivo, observacao=data.observacao, usuario_id=user.id)
    bem.status = "baixado"
    db.add(baixa)
    db.commit()
    db.refresh(baixa)
    return to_out(baixa)
