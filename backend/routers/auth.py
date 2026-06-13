from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Usuario
from schemas import LoginIn, LoginOut, UsuarioOut
from security import create_token, get_current_user, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(Usuario).where(Usuario.username == data.username.strip().lower()))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Usuário ou senha incorretos")
    if not user.ativo:
        raise HTTPException(403, "Usuário desativado")
    return LoginOut(token=create_token(user.id), usuario=UsuarioOut.model_validate(user))


@router.get("/me", response_model=UsuarioOut)
def me(user: Usuario = Depends(get_current_user)):
    return user
