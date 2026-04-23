# 🗄️ Setup MySQL - API de Patrimônio

## 1. Pré-requisitos

Você precisa ter instalado:
- **MySQL Server** 5.7+ ou 8.0+
- **Python** 3.7+
- **pip** (gerenciador de pacotes Python)

## 2. Instalação do MySQL

### Windows (usando instalador)
1. Baixe em: https://dev.mysql.com/downloads/mysql/
2. Execute o instalador
3. Configure root user com senha
4. Anote a senha fornecida no setup

### macOS (usando Homebrew)
```bash
brew install mysql
brew services start mysql
```

### Linux (Debian/Ubuntu)
```bash
sudo apt-get install mysql-server
sudo systemctl start mysql
```

## 3. Criar Banco de Dados

Abra o MySQL Command Line Client (Windows) ou terminal:

```bash
mysql -u root -p
```

Cole os comandos:
```sql
CREATE DATABASE patrimonio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

## 4. Instalar Dependências Python

```bash
cd patrimonio/backend
pip install -r requirements.txt
```

## 5. Configurar Arquivo .env

O arquivo `.env` já foi criado, mas você precisa ajustar as credenciais:

```properties
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua-senha-aqui  # 👈 COLOQUE SUA SENHA
DB_NAME=patrimonio_db
DB_PORT=3306
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-aqui
USE_JSON_FILE=false
```

**Importante**: Se a senha do root estiver vazia (comum em desenvolvimento), deixe assim:
```properties
DB_PASSWORD=
```

## 6. Iniciar a API

### Via main.py (recomendado)
```bash
cd patrimonio
python main.py
```

Saída esperada:
```
============================================================================
                    🏛️  API DE PATRIMÔNIO - MySQL 🏛️
============================================================================

🔧 Configuração:
  Banco de Dados: localhost:3306/patrimonio_db
  Usuário: root
  Ambiente: development

⏳ Inicializando conexão com banco de dados...

  [1/3] Criando pool de conexões...
        ✓ Pool criado com sucesso
  [2/3] Testando conexão com MySQL...
        ✓ Conexão testada com sucesso
  [3/3] Inicializando banco de dados...
        ✓ Banco de dados inicializado

📍 Localhost URL: http://localhost:5000
✅ API Status: http://localhost:5000/api/saude

[... endpoints listados ...]

============================================================================
```

### Via app.py (alternativa)
```bash
cd patrimonio/backend
python app.py
```

## 7. Testar a API

### Em outro terminal, verifique a saúde:
```bash
curl http://localhost:5000/api/saude
```

Resposta esperada:
```json
{
  "status": "sucesso",
  "mensagem": "API de Patrimônio está operacional (MySQL)",
  "timestamp": "2024-01-15 10:30:45",
  "banco_dados": "MySQL"
}
```

### Listar patrimônios:
```bash
curl http://localhost:5000/api/patrimonios
```

## 8. Acessar o Dashboard Web

1. Abra o navegador
2. Acesse: **http://localhost:5000** (você será redirecionado para login)
3. Credenciais demo:
   - Email: `admin@patrimonio.com`
   - Senha: `admin123`

## 9. Visualizar Banco de Dados (MySQL Workbench)

### Instalar MySQL Workbench
- Download: https://dev.mysql.com/downloads/workbench/

### Conectar
1. Abra MySQL Workbench
2. Clique em "+" para nova conexão
3. Configure:
   - Connection Name: `Patrimonio Dev`
   - Hostname: `127.0.0.1`
   - Username: `root`
   - Password: [sua senha]
4. Test Connection
5. Clique na conexão para abrir

### Ver dados
```sql
USE patrimonio_db;
SELECT * FROM patrimonios;
SELECT * FROM usuarios;
SELECT * FROM categorias;
SELECT * FROM auditoria;
```

## 10. Solução de Problemas

### "Access denied for user 'root'"
```
❌ Problema: Senha incorreta ou MySQL não iniciado

✅ Solução:
1. Verifique se MySQL está rodando
2. Corrija DB_PASSWORD no .env
3. Reinicie a API
```

### "Can't connect to MySQL server on 'localhost'"
```
❌ Problema: MySQL não está rodando

✅ Solução Windows:
- Abra Services (services.msc)
- Procure "MySQL80" ou "MySQL"
- Clique direito → Start

✅ Solução macOS:
brew services start mysql

✅ Solução Linux:
sudo systemctl start mysql
```

### "Unknown database 'patrimonio_db'"
```
❌ Problema: Banco de dados não foi criado

✅ Solução:
1. mysql -u root -p
2. CREATE DATABASE patrimonio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
3. EXIT;
```

### "Table 'patrimonio_db.patrimonios' doesn't exist"
```
❌ Problema: Tabelas não foram criadas

✅ Solução:
A API cria tabelas automaticamente ao iniciar.
Se não funcionar:
1. Certifique-se que patrimonio_db existe
2. Reinicie a API
3. Verifique permissões de usuário MySQL
```

## 11. Parar a API

Pressione **CTRL+C** no terminal onde a API está rodando.

## 12. Arquitetura MySQL

### Tabelas criadas automaticamente:

**patrimonios** - Patrimônios/bens
```
id (AUTO_INCREMENT), descricao, categoria, valor, 
data_aquisicao, localizacao, responsavel, status,
observacoes, data_baixa, motivo_baixa
```

**usuarios** - Usuários do sistema
```
id, nome, email, senha, departamento, role,
ativo, data_criacao, ultimo_acesso
```

**categorias** - Categorias de patrimônios
```
id, nome, descricao, cor
```

**auditoria** - Log de alterações
```
id, tabela, operacao, usuario, dados_antigos,
dados_novos, timestamp
```

## 13. Pool de Conexões

A API usa **MySQLConnectionPool** com:
- **pool_size**: 5 conexões simultâneas
- **pool_name**: `patrimonio_pool`
- **reset_session**: True (segurança)
- **autocommit**: True (transações automáticas)

Seguro para requisições concorrentes.

---

**Pronto!** 🎉 Sua API está conectada ao MySQL e totalmente funcional.
