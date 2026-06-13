from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Bem, Categoria, Manutencao, Movimentacao, Setor
from security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_user)])


@router.get("")
def resumo(db: Session = Depends(get_db)):
    total_bens = db.scalar(select(func.count(Bem.id))) or 0
    valor_total = db.scalar(select(func.sum(Bem.valor_aquisicao)).where(Bem.status != "baixado")) or 0.0

    por_status = dict(db.execute(select(Bem.status, func.count()).group_by(Bem.status)).all())
    por_estado = dict(
        db.execute(
            select(Bem.estado, func.count()).where(Bem.status != "baixado").group_by(Bem.estado)
        ).all()
    )

    por_categoria = [
        {"nome": nome or "Sem categoria", "total": total, "valor": valor or 0.0}
        for nome, total, valor in db.execute(
            select(Categoria.nome, func.count(Bem.id), func.sum(Bem.valor_aquisicao))
            .join(Categoria, Bem.categoria_id == Categoria.id, isouter=True)
            .where(Bem.status != "baixado")
            .group_by(Categoria.nome)
            .order_by(func.count(Bem.id).desc())
        ).all()
    ]

    por_setor = [
        {"nome": nome or "Sem setor", "total": total, "valor": valor or 0.0}
        for nome, total, valor in db.execute(
            select(Setor.nome, func.count(Bem.id), func.sum(Bem.valor_aquisicao))
            .join(Setor, Bem.setor_id == Setor.id, isouter=True)
            .where(Bem.status != "baixado")
            .group_by(Setor.nome)
            .order_by(func.count(Bem.id).desc())
        ).all()
    ]

    manutencoes_abertas = db.scalar(
        select(func.count(Manutencao.id)).where(Manutencao.status == "aberta")
    ) or 0
    custo_manutencoes = db.scalar(select(func.sum(Manutencao.custo))) or 0.0

    ultimas_movs = db.scalars(
        select(Movimentacao)
        .options(
            joinedload(Movimentacao.bem),
            joinedload(Movimentacao.setor_origem),
            joinedload(Movimentacao.setor_destino),
        )
        .order_by(Movimentacao.data.desc())
        .limit(6)
    ).all()

    return {
        "total_bens": total_bens,
        "bens_ativos": por_status.get("ativo", 0),
        "em_manutencao": por_status.get("manutencao", 0),
        "baixados": por_status.get("baixado", 0),
        "valor_total": round(valor_total, 2),
        "manutencoes_abertas": manutencoes_abertas,
        "custo_manutencoes": round(custo_manutencoes, 2),
        "por_estado": por_estado,
        "por_categoria": por_categoria,
        "por_setor": por_setor,
        "ultimas_movimentacoes": [
            {
                "bem": f"{m.bem.tombo} — {m.bem.nome}" if m.bem else "?",
                "origem": m.setor_origem.nome if m.setor_origem else "—",
                "destino": m.setor_destino.nome if m.setor_destino else "—",
                "data": m.data.isoformat(),
            }
            for m in ultimas_movs
        ],
    }
