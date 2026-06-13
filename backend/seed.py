"""Dados iniciais: usuário admin e cadastros básicos (roda no startup, idempotente)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Categoria, Setor, Usuario
from security import hash_password

CATEGORIAS = [
    ("Informática", "Computadores, notebooks, impressoras e periféricos"),
    ("Mobiliário", "Mesas, cadeiras, armários e estantes"),
    ("Eletrodomésticos", "Geladeiras, micro-ondas, cafeteiras"),
    ("Veículos", "Carros, motos e utilitários"),
    ("Ferramentas", "Ferramentas e equipamentos de manutenção"),
]

SETORES = [
    ("Administração", "", "Prédio principal — 1º andar"),
    ("Financeiro", "", "Prédio principal — 2º andar"),
    ("TI", "", "Prédio principal — térreo"),
    ("Almoxarifado", "", "Galpão B"),
    ("Recepção", "", "Prédio principal — entrada"),
]


def run(db: Session) -> None:
    if db.scalar(select(Usuario).limit(1)) is None:
        db.add(Usuario(
            nome="Administrador",
            username="admin",
            password_hash=hash_password("admin123"),
            role="admin",
        ))

    if db.scalar(select(Categoria).limit(1)) is None:
        for nome, desc in CATEGORIAS:
            db.add(Categoria(nome=nome, descricao=desc))

    if db.scalar(select(Setor).limit(1)) is None:
        for nome, resp, loc in SETORES:
            db.add(Setor(nome=nome, responsavel=resp, localizacao=loc))

    db.commit()
