from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import models  # noqa: F401 — registra as tabelas
import seed
from database import Base, SessionLocal, engine
from routers import (
    auth,
    baixas,
    bens,
    categorias,
    dashboard,
    manutencoes,
    movimentacoes,
    relatorios,
    setores,
    usuarios,
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed.run(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Sistema de Patrimônio", version="1.0.0", lifespan=lifespan)

for router in (
    auth.router,
    dashboard.router,
    bens.router,
    categorias.router,
    setores.router,
    movimentacoes.router,
    manutencoes.router,
    baixas.router,
    relatorios.router,
    usuarios.router,
):
    app.include_router(router, prefix="/api")

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
