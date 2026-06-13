import math

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Bem, Usuario
from schemas import BemIn, BemOut, BemUpdate, BensPage
from security import get_current_user

router = APIRouter(prefix="/bens", tags=["bens"], dependencies=[Depends(get_current_user)])

PAGE_SIZE = 12


def to_out(b: Bem) -> BemOut:
    out = BemOut.model_validate(b)
    out.categoria_nome = b.categoria.nome if b.categoria else None
    out.setor_nome = b.setor.nome if b.setor else None
    return out


@router.get("", response_model=BensPage)
def listar(
    q: str = "",
    categoria_id: int | None = None,
    setor_id: int | None = None,
    status: str | None = None,
    estado: str | None = None,
    page: int = 1,
    db: Session = Depends(get_db),
):
    stmt = select(Bem).options(joinedload(Bem.categoria), joinedload(Bem.setor))
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Bem.nome.ilike(like), Bem.tombo.ilike(like), Bem.num_serie.ilike(like)))
    if categoria_id:
        stmt = stmt.where(Bem.categoria_id == categoria_id)
    if setor_id:
        stmt = stmt.where(Bem.setor_id == setor_id)
    if status:
        stmt = stmt.where(Bem.status == status)
    if estado:
        stmt = stmt.where(Bem.estado == estado)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    pages = max(1, math.ceil(total / PAGE_SIZE))
    page = max(1, min(page, pages))
    rows = db.scalars(stmt.order_by(Bem.id.desc()).offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)).all()
    return BensPage(items=[to_out(b) for b in rows], total=total, page=page, pages=pages)


@router.get("/todos", response_model=list[BemOut])
def listar_todos(apenas_ativos: bool = True, db: Session = Depends(get_db)):
    """Lista enxuta para selects (movimentação/manutenção/baixa)."""
    stmt = select(Bem).options(joinedload(Bem.categoria), joinedload(Bem.setor))
    if apenas_ativos:
        stmt = stmt.where(Bem.status != "baixado")
    rows = db.scalars(stmt.order_by(Bem.nome)).all()
    return [to_out(b) for b in rows]


@router.get("/{bem_id}", response_model=BemOut)
def obter(bem_id: int, db: Session = Depends(get_db)):
    bem = db.get(Bem, bem_id)
    if bem is None:
        raise HTTPException(404, "Bem não encontrado")
    return to_out(bem)


@router.post("", response_model=BemOut, status_code=201)
def criar(data: BemIn, db: Session = Depends(get_db)):
    if db.scalar(select(Bem).where(Bem.tombo == data.tombo.strip())):
        raise HTTPException(409, f"Já existe um bem com o tombo '{data.tombo}'")
    bem = Bem(**data.model_dump())
    bem.tombo = bem.tombo.strip()
    db.add(bem)
    db.commit()
    db.refresh(bem)
    return to_out(bem)


@router.put("/{bem_id}", response_model=BemOut)
def atualizar(bem_id: int, data: BemUpdate, db: Session = Depends(get_db)):
    bem = db.get(Bem, bem_id)
    if bem is None:
        raise HTTPException(404, "Bem não encontrado")
    if bem.status == "baixado":
        raise HTTPException(409, "Bem baixado não pode ser editado")
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(bem, campo, valor)
    db.commit()
    db.refresh(bem)
    return to_out(bem)


@router.delete("/{bem_id}", status_code=204)
def excluir(bem_id: int, db: Session = Depends(get_db), user: Usuario = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Apenas administradores podem excluir bens")
    bem = db.get(Bem, bem_id)
    if bem is None:
        raise HTTPException(404, "Bem não encontrado")
    for mov in bem.movimentacoes:
        db.delete(mov)
    for man in bem.manutencoes:
        db.delete(man)
    db.delete(bem)
    db.commit()
