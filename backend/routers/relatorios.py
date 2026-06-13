import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Baixa, Bem, Manutencao, Movimentacao
from security import get_current_user

router = APIRouter(prefix="/relatorios", tags=["relatorios"], dependencies=[Depends(get_current_user)])

STATUS_LABEL = {"ativo": "Ativo", "manutencao": "Em manutenção", "baixado": "Baixado"}


def _csv_response(filename: str, header: list[str], rows: list[list]) -> StreamingResponse:
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";", lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    # BOM para o Excel reconhecer UTF-8
    data = "﻿" + buf.getvalue()
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    return StreamingResponse(
        io.BytesIO(data.encode("utf-8")),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}_{stamp}.csv"'},
    )


@router.get("/bens.csv")
def bens_csv(status: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Bem).options(joinedload(Bem.categoria), joinedload(Bem.setor))
    if status:
        stmt = stmt.where(Bem.status == status)
    rows = []
    for b in db.scalars(stmt.order_by(Bem.tombo)).all():
        rows.append([
            b.tombo,
            b.nome,
            b.categoria.nome if b.categoria else "",
            b.setor.nome if b.setor else "",
            b.fornecedor,
            b.num_serie,
            f"{b.valor_aquisicao:.2f}".replace(".", ","),
            b.data_aquisicao.strftime("%d/%m/%Y") if b.data_aquisicao else "",
            b.estado.capitalize(),
            STATUS_LABEL.get(b.status, b.status),
        ])
    header = ["Tombo", "Nome", "Categoria", "Setor", "Fornecedor", "Nº Série",
              "Valor (R$)", "Aquisição", "Estado", "Status"]
    return _csv_response("bens", header, rows)


@router.get("/movimentacoes.csv")
def movimentacoes_csv(db: Session = Depends(get_db)):
    rows = []
    movs = db.scalars(
        select(Movimentacao)
        .options(
            joinedload(Movimentacao.bem),
            joinedload(Movimentacao.setor_origem),
            joinedload(Movimentacao.setor_destino),
            joinedload(Movimentacao.usuario),
        )
        .order_by(Movimentacao.data.desc())
    ).all()
    for m in movs:
        rows.append([
            m.data.strftime("%d/%m/%Y %H:%M"),
            m.bem.tombo if m.bem else "",
            m.bem.nome if m.bem else "",
            m.setor_origem.nome if m.setor_origem else "—",
            m.setor_destino.nome if m.setor_destino else "",
            m.motivo,
            m.usuario.nome if m.usuario else "",
        ])
    header = ["Data", "Tombo", "Bem", "Origem", "Destino", "Motivo", "Usuário"]
    return _csv_response("movimentacoes", header, rows)


@router.get("/manutencoes.csv")
def manutencoes_csv(db: Session = Depends(get_db)):
    rows = []
    for m in db.scalars(
        select(Manutencao).options(joinedload(Manutencao.bem)).order_by(Manutencao.data_inicio.desc())
    ).all():
        rows.append([
            m.data_inicio.strftime("%d/%m/%Y"),
            m.data_fim.strftime("%d/%m/%Y") if m.data_fim else "",
            m.bem.tombo if m.bem else "",
            m.bem.nome if m.bem else "",
            m.tipo.capitalize(),
            "Concluída" if m.status == "concluida" else "Aberta",
            m.responsavel,
            f"{m.custo:.2f}".replace(".", ","),
            m.descricao,
        ])
    header = ["Início", "Fim", "Tombo", "Bem", "Tipo", "Status", "Responsável", "Custo (R$)", "Descrição"]
    return _csv_response("manutencoes", header, rows)


@router.get("/baixas.csv")
def baixas_csv(db: Session = Depends(get_db)):
    rows = []
    for b in db.scalars(
        select(Baixa).options(joinedload(Baixa.bem), joinedload(Baixa.usuario)).order_by(Baixa.data.desc())
    ).all():
        rows.append([
            b.data.strftime("%d/%m/%Y %H:%M"),
            b.bem.tombo if b.bem else "",
            b.bem.nome if b.bem else "",
            b.motivo.capitalize(),
            b.observacao,
            b.usuario.nome if b.usuario else "",
        ])
    header = ["Data", "Tombo", "Bem", "Motivo", "Observação", "Usuário"]
    return _csv_response("baixas", header, rows)
