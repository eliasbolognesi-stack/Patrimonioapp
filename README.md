# Sistema de Patrimônio

Sistema completo de gestão de bens patrimoniais com backend FastAPI + SQLite e frontend SPA (HTML/CSS/JS puro) em tema dark red.

## Como iniciar

Dê dois cliques em **`start.bat`** (requer Python instalado). Na primeira execução ele cria o ambiente virtual e instala as dependências automaticamente; depois abre o navegador em `http://localhost:8000`.

**Acesso padrão:** usuário `admin` / senha `admin123`
(Troque a senha em *Usuários* após o primeiro acesso.)

## Funcionalidades

- **Dashboard** — totais, valor do patrimônio, gráficos por setor/categoria/estado de conservação e últimas movimentações
- **Bens** — CRUD com tombo único, busca, filtros, paginação e histórico por bem
- **Movimentações** — transferência de bens entre setores com trilha de auditoria
- **Manutenções** — abertura/conclusão com custos (o bem fica "Em manutenção" automaticamente)
- **Baixas** — retirada de bens do acervo com motivo e responsável
- **Categorias e Setores** — cadastros de apoio
- **Relatórios** — exportação CSV (Excel) de bens, movimentações, manutenções e baixas
- **Usuários** — perfis Administrador e Operador (somente admin gerencia)

## Estrutura

```
patrimonio/
├── backend/            FastAPI + SQLAlchemy + SQLite
│   ├── main.py         app, rotas e arquivos estáticos
│   ├── models.py       tabelas do banco
│   ├── schemas.py      validação (Pydantic)
│   ├── security.py     senhas (PBKDF2) e tokens
│   ├── seed.py         dados iniciais
│   └── routers/        endpoints por módulo
├── frontend/           SPA dark red (sem dependências)
│   ├── index.html
│   ├── css/style.css
│   └── js/             api, ui, páginas e roteador
└── start.bat           inicialização em um clique
```

A API fica documentada em `http://localhost:8000/docs` (Swagger).
