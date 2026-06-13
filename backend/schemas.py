from datetime import datetime, date

from pydantic import BaseModel, ConfigDict, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- auth ----------

class LoginIn(BaseModel):
    username: str
    password: str


class UsuarioOut(ORM):
    id: int
    nome: str
    username: str
    role: str
    ativo: bool
    criado_em: datetime


class LoginOut(BaseModel):
    token: str
    usuario: UsuarioOut


class UsuarioIn(BaseModel):
    nome: str = Field(min_length=2)
    username: str = Field(min_length=3)
    password: str = Field(min_length=4)
    role: str = "operador"


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    password: str | None = None
    role: str | None = None
    ativo: bool | None = None


# ---------- categorias / setores ----------

class CategoriaIn(BaseModel):
    nome: str = Field(min_length=2)
    descricao: str = ""


class CategoriaOut(ORM):
    id: int
    nome: str
    descricao: str
    total_bens: int = 0


class SetorIn(BaseModel):
    nome: str = Field(min_length=2)
    responsavel: str = ""
    localizacao: str = ""


class SetorOut(ORM):
    id: int
    nome: str
    responsavel: str
    localizacao: str
    total_bens: int = 0


# ---------- bens ----------

class BemIn(BaseModel):
    tombo: str = Field(min_length=1)
    nome: str = Field(min_length=2)
    descricao: str = ""
    categoria_id: int | None = None
    setor_id: int | None = None
    fornecedor: str = ""
    num_serie: str = ""
    valor_aquisicao: float = 0.0
    data_aquisicao: date | None = None
    estado: str = "bom"


class BemUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    categoria_id: int | None = None
    fornecedor: str | None = None
    num_serie: str | None = None
    valor_aquisicao: float | None = None
    data_aquisicao: date | None = None
    estado: str | None = None


class BemOut(ORM):
    id: int
    tombo: str
    nome: str
    descricao: str
    categoria_id: int | None
    setor_id: int | None
    categoria_nome: str | None = None
    setor_nome: str | None = None
    fornecedor: str
    num_serie: str
    valor_aquisicao: float
    data_aquisicao: date | None
    estado: str
    status: str
    criado_em: datetime


class BensPage(BaseModel):
    items: list[BemOut]
    total: int
    page: int
    pages: int


# ---------- movimentações ----------

class MovimentacaoIn(BaseModel):
    bem_id: int
    setor_destino_id: int
    motivo: str = ""


class MovimentacaoOut(ORM):
    id: int
    bem_id: int
    bem_tombo: str | None = None
    bem_nome: str | None = None
    setor_origem_nome: str | None = None
    setor_destino_nome: str | None = None
    motivo: str
    usuario_nome: str | None = None
    data: datetime


# ---------- manutenções ----------

class ManutencaoIn(BaseModel):
    bem_id: int
    tipo: str = "corretiva"
    descricao: str = ""
    responsavel: str = ""
    custo: float = 0.0


class ManutencaoConcluir(BaseModel):
    custo: float | None = None


class ManutencaoOut(ORM):
    id: int
    bem_id: int
    bem_tombo: str | None = None
    bem_nome: str | None = None
    tipo: str
    descricao: str
    responsavel: str
    custo: float
    status: str
    data_inicio: datetime
    data_fim: datetime | None


# ---------- baixas ----------

class BaixaIn(BaseModel):
    bem_id: int
    motivo: str = "inservivel"
    observacao: str = ""


class BaixaOut(ORM):
    id: int
    bem_id: int
    bem_tombo: str | None = None
    bem_nome: str | None = None
    motivo: str
    observacao: str
    usuario_nome: str | None = None
    data: datetime
