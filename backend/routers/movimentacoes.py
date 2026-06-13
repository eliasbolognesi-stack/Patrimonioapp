from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Bem, Movimentacao, Setor, Usuario
from schemas import MovimentacaoIn, MovimentacaoOut
from security import get_current_user

router = APIRouter(prefix="/movimentacoes", tags=["movimentacoes"])


def to_out(m: Movimentacao) -> MovimentacaoOut:
    out = MovimentacaoOut.model_validate(m)
    out.bem_tombo = m.bem.tombo if m.bem else None
    out.bem_nome = m.bem.nome if m.bem else None
    out.setor_origem_nome = m.setor_origem.nome if m.setor_origem else None
    out.setor_destino_nome = m.setor_destino.nome if m.setor_destino else None
    out.usuario_nome = m.usuario.nome if m.usuario else None
    return out


@router.get("", response_model=list[MovimentacaoOut], dependencies=[Depends(get_current_user)])
def listar(bem_id: int | None = None, limit: int = 100, db: Session = Depends(get_db)):
    stmt = select(Movimentacao).options(
        joinedload(Movimentacao.bem),
        joinedload(Movimentacao.setor_origem),
        joinedload(Movimentacao.setor_destino),
        joinedload(Movimentacao.usuario),
    )
    if bem_id:
        stmt = stmt.where(Movimentacao.bem_id == bem_id)
    rows = db.scalars(stmt.order_by(Movimentacao.data.desc()).limit(limit)).all()
    return [to_out(m) for m in rows]


@router.post("", response_model=MovimentacaoOut, status_code=201)
def criar(data: MovimentacaoIn, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    bem = db.get(Bem, data.bem_id)
    if bem is None:
        raise HTTPException(404, "Bem não encontrado")
    if bem.status == "baixado":
        raise HTTPException(409, "Bem baixado não pode ser movimentado")
    destino = db.get(Setor, data.setor_destino_id)
    if destino is None:
        raise HTTPException(404, "Setor de destino não encontrado")
    if bem.setor_id == destino.id:
        raise HTTPException(409, "O bem já está neste setor")

    mov = Movimentacao(
        bem_id=bem.id,
        setor_origem_id=bem.setor_id,
        setor_destino_id=destino.id,
        motivo=data.motivo,
        usuario_id=user.id,
    )
    bem.setor_id = destino.id
    db.add(mov)
    db.commit()
    db.refresh(mov)
    return to_out(mov)
