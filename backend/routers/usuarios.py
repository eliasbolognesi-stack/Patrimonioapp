from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Usuario
from schemas import UsuarioIn, UsuarioOut, UsuarioUpdate
from security import hash_password, require_admin

router = APIRouter(prefix="/usuarios", tags=["usuarios"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[UsuarioOut])
def listar(db: Session = Depends(get_db)):
    return db.scalars(select(Usuario).order_by(Usuario.nome)).all()


@router.post("", response_model=UsuarioOut, status_code=201)
def criar(data: UsuarioIn, db: Session = Depends(get_db)):
    username = data.username.strip().lower()
    if db.scalar(select(Usuario).where(Usuario.username == username)):
        raise HTTPException(409, "Nome de usuário já existe")
    if data.role not in ("admin", "operador"):
        raise HTTPException(422, "Perfil inválido")
    user = Usuario(
        nome=data.nome.strip(),
        username=username,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UsuarioOut)
def atualizar(
    user_id: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    user = db.get(Usuario, user_id)
    if user is None:
        raise HTTPException(404, "Usuário não encontrado")
    if data.nome is not None:
        user.nome = data.nome.strip()
    if data.password:
        user.password_hash = hash_password(data.password)
    if data.role is not None:
        if data.role not in ("admin", "operador"):
            raise HTTPException(422, "Perfil inválido")
        if user.id == admin.id and data.role != "admin":
            raise HTTPException(409, "Você não pode remover seu próprio acesso de administrador")
        user.role = data.role
    if data.ativo is not None:
        if user.id == admin.id and not data.ativo:
            raise HTTPException(409, "Você não pode desativar a si mesmo")
        user.ativo = data.ativo
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def excluir(user_id: int, db: Session = Depends(get_db), admin: Usuario = Depends(require_admin)):
    if user_id == admin.id:
        raise HTTPException(409, "Você não pode excluir a si mesmo")
    user = db.get(Usuario, user_id)
    if user is None:
        raise HTTPException(404, "Usuário não encontrado")
    db.delete(user)
    db.commit()
