# -*- coding: utf-8 -*-
"""
Módulo de Banco de Dados - Conexão e Inicialização MySQL
"""

import mysql.connector
from mysql.connector import Error, pooling
from config import DatabaseConfig
import json
import os

# Pool de conexões
db_pool = None

def init_connection_pool():
    """Inicializa o pool de conexões MySQL"""
    global db_pool
    try:
        db_pool = pooling.MySQLConnectionPool(
            **DatabaseConfig.get_pool_config()
        )
        print("✅ Pool de conexões MySQL inicializado com sucesso")
        return True
    except Error as err:
        print(f"❌ Erro ao inicializar pool de conexões: {err}")
        return False

def get_connection():
    """Obtém uma conexão do pool"""
    global db_pool
    if db_pool is None:
        if not init_connection_pool():
            raise Exception("Falha ao obter conexão do pool")
    try:
        return db_pool.get_connection()
    except Error as err:
        print(f"❌ Erro ao obter conexão: {err}")
        raise

def close_connection(connection):
    """Fecha uma conexão"""
    if connection.is_connected():
        connection.close()

def init_database():
    """Inicializa o banco de dados e cria as tabelas se não existirem"""
    try:
        # Conectar ao servidor MySQL (sem especificar banco de dados)
        connection = mysql.connector.connect(
            host=DatabaseConfig.DB_HOST,
            user=DatabaseConfig.DB_USER,
            password=DatabaseConfig.DB_PASSWORD,
            port=DatabaseConfig.DB_PORT
        )
        
        cursor = connection.cursor()
        
        # Criar banco de dados
        print(f"📝 Criando banco de dados '{DatabaseConfig.DB_NAME}' se não existir...")
        cursor.execute(f"""
            CREATE DATABASE IF NOT EXISTS {DatabaseConfig.DB_NAME}
            CHARACTER SET {DatabaseConfig.DB_CHARSET}
            COLLATE {DatabaseConfig.DB_COLLATION}
        """)
        
        # Usar o banco de dados
        cursor.execute(f"USE {DatabaseConfig.DB_NAME}")
        
        # Criar tabela de patrimônios
        print("📝 Criando tabela de patrimônios...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patrimonios (
                id INT PRIMARY KEY AUTO_INCREMENT,
                descricao VARCHAR(255) NOT NULL,
                categoria VARCHAR(100) DEFAULT 'Geral',
                valor DECIMAL(12, 2) DEFAULT 0.00,
                data_aquisicao DATE,
                localizacao VARCHAR(255),
                responsavel VARCHAR(255),
                status ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                observacoes TEXT,
                data_baixa DATETIME,
                motivo_baixa VARCHAR(255),
                
                INDEX idx_status (status),
                INDEX idx_categoria (categoria),
                INDEX idx_data_cadastro (data_cadastro),
                FULLTEXT idx_descricao (descricao)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Criar tabela de usuários
        print("📝 Criando tabela de usuários...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                senha VARCHAR(255) NOT NULL,
                departamento VARCHAR(100),
                role ENUM('Admin', 'Gerente', 'Usuário') DEFAULT 'Usuário',
                ativo BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_acesso DATETIME,
                
                INDEX idx_email (email),
                INDEX idx_ativo (ativo)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Criar tabela de categorias
        print("📝 Criando tabela de categorias...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nome VARCHAR(100) UNIQUE NOT NULL,
                descricao TEXT,
                cor VARCHAR(7) DEFAULT '#8b0000',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                INDEX idx_nome (nome)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Criar tabela de auditoria
        print("📝 Criando tabela de auditoria...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoria (
                id INT PRIMARY KEY AUTO_INCREMENT,
                usuario_id INT,
                acao VARCHAR(50),
                tabela VARCHAR(100),
                registro_id INT,
                dados_antes JSON,
                dados_depois JSON,
                data_acao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip VARCHAR(45),
                
                INDEX idx_usuario (usuario_id),
                INDEX idx_acao (acao),
                INDEX idx_tabela (tabela),
                INDEX idx_data (data_acao),
                
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Inserir categorias padrão
        print("📝 Inserindo categorias padrão...")
        categorias_padrao = [
            ('Informática', 'Computadores, notebooks, periféricos', '#8b0000'),
            ('Móveis', 'Mesas, cadeiras, estantes', '#b91c1c'),
            ('Periféricos', 'Impressoras, scanners, monitores', '#d32f2f'),
            ('Veículos', 'Carros, motos, bicicletas', '#ef5350'),
            ('Equipamentos', 'Máquinas e equipamentos diversos', '#e53935'),
            ('Outro', 'Outros bens não categorizados', '#c62828'),
        ]
        
        for nome, descricao, cor in categorias_padrao:
            cursor.execute("""
                INSERT IGNORE INTO categorias (nome, descricao, cor)
                VALUES (%s, %s, %s)
            """, (nome, descricao, cor))
        
        # Inserir usuário admin padrão (se não existir)
        print("📝 Criando usuário admin padrão...")
        cursor.execute("""
            INSERT IGNORE INTO usuarios (nome, email, senha, departamento, role, ativo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            'Administrador',
            'admin@patrimonio.com',
            'admin123',  # Em produção, use hash de senha!
            'Administrativo',
            'Admin',
            True
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ Banco de dados inicializado com sucesso!")
        return True
        
    except Error as err:
        print(f"❌ Erro ao inicializar banco de dados: {err}")
        return False

def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        cursor.close()
        close_connection(connection)
        print(f"✅ Conexão bem-sucedida! MySQL Versão: {version[0]}")
        return True
    except Exception as err:
        print(f"❌ Erro ao testar conexão: {err}")
        return False

def execute_query(query, params=None, fetchone=False, fetchall=False):
    """
    Executa uma query no banco de dados
    
    Args:
        query: String com a query SQL
        params: Tupla/lista de parâmetros
        fetchone: Se True, retorna apenas um resultado
        fetchall: Se True, retorna todos os resultados
    
    Returns:
        Resultado da query ou None em operações de INSERT/UPDATE/DELETE
    """
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        else:
            result = cursor.rowcount
        
        connection.commit()
        cursor.close()
        return result
        
    except Error as err:
        print(f"❌ Erro ao executar query: {err}")
        if connection:
            connection.rollback()
        return None
    finally:
        if connection and connection.is_connected():
            close_connection(connection)

def get_patrimonios_from_db():
    """Obtém todos os patrimônios do banco de dados"""
    query = "SELECT * FROM patrimonios ORDER BY id DESC"
    return execute_query(query, fetchall=True) or []

def get_patrimonio_by_id(patrimonio_id):
    """Obtém um patrimônio específico"""
    query = "SELECT * FROM patrimonios WHERE id = %s"
    return execute_query(query, (patrimonio_id,), fetchone=True)

def insert_patrimonio(data):
    """Insere um novo patrimônio"""
    query = """
        INSERT INTO patrimonios 
        (descricao, categoria, valor, data_aquisicao, localizacao, responsavel, observacoes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        data.get('descricao'),
        data.get('categoria', 'Geral'),
        data.get('valor', 0),
        data.get('data_aquisicao'),
        data.get('localizacao'),
        data.get('responsavel'),
        data.get('observacoes')
    )
    result = execute_query(query, params)
    if result:
        return get_patrimonio_by_id(result)
    return None

def update_patrimonio(patrimonio_id, data):
    """Atualiza um patrimônio"""
    query = """
        UPDATE patrimonios SET
        descricao = %s,
        categoria = %s,
        valor = %s,
        data_aquisicao = %s,
        localizacao = %s,
        responsavel = %s,
        observacoes = %s
        WHERE id = %s
    """
    params = (
        data.get('descricao'),
        data.get('categoria'),
        data.get('valor'),
        data.get('data_aquisicao'),
        data.get('localizacao'),
        data.get('responsavel'),
        data.get('observacoes'),
        patrimonio_id
    )
    execute_query(query, params)
    return get_patrimonio_by_id(patrimonio_id)

def delete_patrimonio(patrimonio_id):
    """Deleta um patrimônio"""
    query = "DELETE FROM patrimonios WHERE id = %s"
    return execute_query(query, (patrimonio_id,))

def dar_baixa_patrimonio(patrimonio_id, motivo):
    """Marca um patrimônio como inativo (dar baixa)"""
    query = """
        UPDATE patrimonios SET
        status = 'Inativo',
        data_baixa = NOW(),
        motivo_baixa = %s
        WHERE id = %s
    """
    execute_query(query, (motivo, patrimonio_id))
    return get_patrimonio_by_id(patrimonio_id)

def get_relatorio_ativos():
    """Obtém relatório de patrimônios ativos"""
    query = """
        SELECT 
            COUNT(*) as total,
            SUM(valor) as valor_total,
            AVG(valor) as valor_medio
        FROM patrimonios
        WHERE status = 'Ativo'
    """
    resultado = execute_query(query, fetchone=True)
    
    query_lista = "SELECT * FROM patrimonios WHERE status = 'Ativo' ORDER BY id DESC"
    patrimonios = execute_query(query_lista, fetchall=True) or []
    
    return {
        'total_ativos': resultado['total'] or 0,
        'valor_total': float(resultado['valor_total'] or 0),
        'valor_medio': float(resultado['valor_medio'] or 0),
        'patrimonios': patrimonios
    }

def get_relatorio_inativos():
    """Obtém relatório de patrimônios inativos"""
    query = """
        SELECT 
            COUNT(*) as total,
            SUM(valor) as valor_total,
            AVG(valor) as valor_medio
        FROM patrimonios
        WHERE status = 'Inativo'
    """
    resultado = execute_query(query, fetchone=True)
    
    query_lista = "SELECT * FROM patrimonios WHERE status = 'Inativo' ORDER BY id DESC"
    patrimonios = execute_query(query_lista, fetchall=True) or []
    
    return {
        'total_inativos': resultado['total'] or 0,
        'valor_total': float(resultado['valor_total'] or 0),
        'valor_medio': float(resultado['valor_medio'] or 0),
        'patrimonios': patrimonios
    }

def get_relatorio_geral():
    """Obtém relatório geral"""
    query = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Ativo' THEN 1 ELSE 0 END) as ativos,
            SUM(CASE WHEN status = 'Inativo' THEN 1 ELSE 0 END) as inativos,
            SUM(CASE WHEN status = 'Ativo' THEN valor ELSE 0 END) as valor_ativos,
            SUM(CASE WHEN status = 'Inativo' THEN valor ELSE 0 END) as valor_inativos,
            SUM(valor) as valor_total
        FROM patrimonios
    """
    resultado = execute_query(query, fetchone=True)
    
    return {
        'total_patrimonios': resultado['total'] or 0,
        'total_ativos': resultado['ativos'] or 0,
        'total_inativos': resultado['inativos'] or 0,
        'valor_total_ativos': float(resultado['valor_ativos'] or 0),
        'valor_total_inativos': float(resultado['valor_inativos'] or 0),
        'valor_total_geral': float(resultado['valor_total'] or 0)
    }

def search_patrimonios(termo):
    """Busca patrimônios por termo"""
    query = """
        SELECT * FROM patrimonios 
        WHERE MATCH(descricao) AGAINST(%s IN BOOLEAN MODE)
        OR categoria LIKE %s
        OR localizacao LIKE %s
        OR responsavel LIKE %s
        ORDER BY id DESC
    """
    termo_percent = f"%{termo}%"
    return execute_query(query, (termo, termo_percent, termo_percent, termo_percent), fetchall=True) or []
