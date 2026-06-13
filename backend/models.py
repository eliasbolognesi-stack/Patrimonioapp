from datetime import datetime, date

from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    username: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(20), default="operador")  # admin | operador
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True)
    descricao: Mapped[str] = mapped_column(Text, default="")

    bens: Mapped[list["Bem"]] = relationship(back_populates="categoria")


class Setor(Base):
    __tablename__ = "setores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True)
    responsavel: Mapped[str] = mapped_column(String(120), default="")
    localizacao: Mapped[str] = mapped_column(String(160), default="")

    bens: Mapped[list["Bem"]] = relationship(back_populates="setor")


class Bem(Base):
    __tablename__ = "bens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tombo: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(160))
    descricao: Mapped[str] = mapped_column(Text, default="")
    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id"), nullable=True)
    setor_id: Mapped[int | None] = mapped_column(ForeignKey("setores.id"), nullable=True)
    fornecedor: Mapped[str] = mapped_column(String(160), default="")
    num_serie: Mapped[str] = mapped_column(String(80), default="")
    valor_aquisicao: Mapped[float] = mapped_column(Float, default=0.0)
    data_aquisicao: Mapped[date | None] = mapped_column(Date, nullable=True)
    # otimo | bom | regular | ruim | inservivel
    estado: Mapped[str] = mapped_column(String(20), default="bom")
    # ativo | manutencao | baixado
    status: Mapped[str] = mapped_column(String(20), default="ativo")
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    categoria: Mapped[Categoria | None] = relationship(back_populates="bens")
    setor: Mapped[Setor | None] = relationship(back_populates="bens")
    movimentacoes: Mapped[list["Movimentacao"]] = relationship(back_populates="bem")
    manutencoes: Mapped[list["Manutencao"]] = relationship(back_populates="bem")


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bem_id: Mapped[int] = mapped_column(ForeignKey("bens.id"))
    setor_origem_id: Mapped[int | None] = mapped_column(ForeignKey("setores.id"), nullable=True)
    setor_destino_id: Mapped[int] = mapped_column(ForeignKey("setores.id"))
    motivo: Mapped[str] = mapped_column(Text, default="")
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    bem: Mapped[Bem] = relationship(back_populates="movimentacoes")
    setor_origem: Mapped[Setor | None] = relationship(foreign_keys=[setor_origem_id])
    setor_destino: Mapped[Setor] = relationship(foreign_keys=[setor_destino_id])
    usuario: Mapped[Usuario | None] = relationship()


class Manutencao(Base):
    __tablename__ = "manutencoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bem_id: Mapped[int] = mapped_column(ForeignKey("bens.id"))
    tipo: Mapped[str] = mapped_column(String(20), default="corretiva")  # preventiva | corretiva
    descricao: Mapped[str] = mapped_column(Text, default="")
    responsavel: Mapped[str] = mapped_column(String(160), default="")
    custo: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="aberta")  # aberta | concluida
    data_inicio: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    data_fim: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    bem: Mapped[Bem] = relationship(back_populates="manutencoes")


class Baixa(Base):
    __tablename__ = "baixas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bem_id: Mapped[int] = mapped_column(ForeignKey("bens.id"))
    motivo: Mapped[str] = mapped_column(String(40), default="inservivel")  # inservivel | extravio | doacao | venda | outro
    observacao: Mapped[str] = mapped_column(Text, default="")
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    bem: Mapped[Bem] = relationship()
    usuario: Mapped[Usuario | None] = relationship()
