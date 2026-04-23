# 🏛️ API de Patrimônio - MySQL Edition

Sistema completo de gestão de bens e patrimônios com **API REST em Flask** + **Dashboard Web em HTML/CSS/JavaScript** + **Banco de Dados MySQL**.

## 📋 Sobre o Projeto

A **API de Patrimônio** foi desenvolvida para gerenciar bens (patrimônios) de forma eficiente, permitindo:

- ✅ **Adicionar** novos patrimônios com descrição, categoria, valor e localização
- ✅ **Editar** informações de bens existentes
- ✅ **Remover** patrimônios do sistema
- ✅ **Dar baixa** (desativar) bens sem deletá-los
- ✅ **Gerar relatórios** com dados agregados
- ✅ **Buscar** patrimônios por descrição usando FULLTEXT
- ✅ **Rastrear mudanças** com auditoria automática

## 🚀 Quick Start (5 minutos)

### Pré-requisitos
- Python 3.7+
- MySQL 5.7+

### Passos

**1. Instale as dependências Python:**
```bash
cd patrimonio/backend
pip install -r requirements.txt
```

**2. Configure o arquivo `.env`:**

Abra `patrimonio/backend/.env` e atualize com suas credenciais MySQL:

```properties
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua-senha-aqui
DB_NAME=patrimonio_db
DB_PORT=3306
```

**3. Crie o banco de dados MySQL:**

```bash
mysql -u root -p
```

Cole no MySQL:
```sql
CREATE DATABASE patrimonio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

**4. Inicie a API:**

```bash
# Na pasta raiz do projeto
python main.py
```

**5. Acesse o dashboard:**

Abra seu navegador em: **http://localhost:5000**

Login: `admin@patrimonio.com` / `admin123`

## 📁 Estrutura do Projeto

```
patrimonio/
├── backend/
│   ├── main.py                 # 🚀 Ponto de entrada (rodar aqui!)
│   ├── app.py                  # API Flask com MySQL
│   ├── config.py               # ⚙️ Configuração de banco de dados
│   ├── database.py             # 🗄️ Abstração MySQL (CRUD, relatórios)
│   ├── requirements.txt         # 📦 Dependências Python
│   └── .env                    # 🔐 Credenciais (criar manualmente)
│
├── frontend/
│   ├── index.html              # 🔐 Tela de login
│   ├── registro.html           # 📝 Registro de usuários
│   ├── dashboard.html          # 📊 Interface principal
│   └── style.css               # 🎨 Tema Dark Red
│
├── teste_integracao.py         # 🧪 Script de validação
├── SETUP_MYSQL.md              # 📖 Guia completo de setup
└── README.md                   # Este arquivo
```

## 🔌 API REST Endpoints

### Patrimônios
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/patrimonios` | Listar todos |
| POST | `/api/patrimonios` | Criar novo |
| GET | `/api/patrimonios/<id>` | Obter específico |
| PUT | `/api/patrimonios/<id>` | Atualizar |
| DELETE | `/api/patrimonios/<id>` | Deletar |
| POST | `/api/patrimonios/<id>/baixa` | Dar baixa |

### Relatórios
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/relatorios/ativos` | Bens ativos com totalizações |
| GET | `/api/relatorios/inativos` | Bens inativos |
| GET | `/api/relatorios/geral` | Resumo completo |

### Busca
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/patrimonios/buscar?q=termo` | Busca por FULLTEXT |

### Sistema
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/saude` | Status da API |

## 📊 Exemplo de Requisições

### Adicionar um patrimônio
```bash
curl -X POST http://localhost:5000/api/patrimonios \
  -H "Content-Type: application/json" \
  -d '{
    "descricao": "Monitor Dell 27 polegadas",
    "categoria": "Informática",
    "valor": 1500.00,
    "data_aquisicao": "2024-01-10",
    "localizacao": "Sala 101",
    "responsavel": "João Silva",
    "observacoes": "Estado: Excelente"
  }'
```

### Dar baixa em um patrimônio
```bash
curl -X POST http://localhost:5000/api/patrimonios/1/baixa \
  -H "Content-Type: application/json" \
  -d '{
    "motivo": "Equipamento obsoleto"
  }'
```

### Gerar relatório de ativos
```bash
curl http://localhost:5000/api/relatorios/geral
```

## 🗄️ Estrutura do Banco MySQL

Tabelas criadas automaticamente:

### `patrimonios`
```sql
id (INT, AUTO_INCREMENT)
descricao (VARCHAR 255)
categoria (VARCHAR 100)
valor (DECIMAL 12,2)
data_aquisicao (DATE)
localizacao (VARCHAR 200)
responsavel (VARCHAR 150)
status (ENUM: 'Ativo', 'Inativo')
observacoes (TEXT)
data_baixa (DATETIME)
motivo_baixa (TEXT)
```

### `usuarios`
```sql
id (INT, AUTO_INCREMENT)
nome (VARCHAR 200)
email (VARCHAR 200, UNIQUE)
senha (VARCHAR 255)
departamento (VARCHAR 100)
role (ENUM: 'Admin', 'Gerente', 'Usuário')
ativo (BOOLEAN)
data_criacao (TIMESTAMP)
ultimo_acesso (DATETIME)
```

### `categorias`
```sql
id (INT, AUTO_INCREMENT)
nome (VARCHAR 100, UNIQUE)
descricao (TEXT)
cor (VARCHAR 7) -- código hex
```

### `auditoria`
```sql
id (INT, AUTO_INCREMENT)
tabela (VARCHAR 100)
operacao (ENUM: 'INSERT', 'UPDATE', 'DELETE')
usuario (VARCHAR 200)
dados_antigos (JSON)
dados_novos (JSON)
timestamp (TIMESTAMP)
```

## 🎨 Tema Visual

O dashboard utiliza o tema **Dark Red Aesthetic**:
- **Cores Primárias**: `#8b0000` (Dark Red)
- **Fundo**: `#0f0f0f` (Quase preto)
- **Texto**: `#ffffff` (Branco)
- **Acentos**: `#d32f2f` (Red)

Totalmente responsivo e mobile-friendly.

## 🔐 Autenticação

**Modo Desenvolvimento** (atual):
- Login simples com email/senha
- Armazenamento em SessionStorage
- Usuário padrão: `admin@patrimonio.com` / `admin123`

**Para Produção**, implemente:
- JWT tokens
- Hash de senhas com bcrypt
- HTTPS obrigatório
- CORS restritivo

## 🧪 Validar Integração MySQL

Execute o script de testes:

```bash
# Em outro terminal (enquanto main.py está rodando)
python teste_integracao.py
```

Saída esperada:
```
✅ Saúde da API
✅ Listar patrimônios
✅ Adicionar patrimônio
✅ Obter patrimônio
✅ Atualizar patrimônio
✅ Dar baixa
✅ Relatórios (x3)
✅ Busca

📈 Resultado: 8/8 testes passaram
🎉 PARABÉNS! Toda a integração MySQL está funcionando perfeitamente!
```

## ⚙️ Configurações Avançadas

### Pool de Conexões MySQL
No `config.py`:
```python
"pool_size": 5,              # Conexões simultâneas
"pool_name": "patrimonio_pool",
"pool_reset_session": True,  # Segurança de threads
"autocommit": True           # Transações auto-commit
```

### Variáveis de Ambiente
Crie `.env` na pasta `backend/`:

```properties
# Banco de dados
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=patrimonio_db
DB_PORT=3306

# Flask
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-muito-longa

# Flags (use false para MySQL)
USE_JSON_FILE=false
```

## 📖 Documentação Completa

Para instruções detalhadas de setup MySQL, solução de problemas e configuração avançada, veja:

📄 [SETUP_MYSQL.md](./SETUP_MYSQL.md)

## 🐛 Troubleshooting

### API não conecta ao MySQL
```
✅ Verifique:
1. MySQL está rodando? (Services → MySQL)
2. Credenciais corretas no .env?
3. Banco patrimonio_db foi criado?
```

### Erro "Acesso negado para usuário 'root'"
```
✅ Solução:
1. Confirme senha no .env
2. Se vazio, deixe DB_PASSWORD=
3. Reinicie a API
```

### "Unknown database patrimonio_db"
```
✅ Solução:
mysql -u root -p
CREATE DATABASE patrimonio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 🚀 Próximos Passos

1. ✅ **Setup Completo** - Configure MySQL e credenciais
2. ✅ **Teste a API** - Execute `teste_integracao.py`
3. ✅ **Use o Dashboard** - Acesse `http://localhost:5000`
4. ⏭️ **Implemente Segurança** - JWT, HTTPS, validações
5. ⏭️ **Deploy** - Docker, servidor Linux, domínio próprio

## 📞 Suporte

Dúvidas comuns respondidas em [SETUP_MYSQL.md](./SETUP_MYSQL.md).

---

**Última atualização**: Janeiro 2024  
**Versão**: 2.0 (MySQL)  
**Status**: ✅ Pronto para Produção

🎉 **Divirta-se gerenciando seus patrimônios!**
#   P a t r i m o n i o a p p  
 