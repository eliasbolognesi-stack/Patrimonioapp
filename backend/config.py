# -*- coding: utf-8 -*-
"""
Configurações da Aplicação e Banco de Dados
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    """Configuração base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'sua-chave-secreta-aqui')
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

class DatabaseConfig:
    """Configurações do banco de dados MySQL"""
    
    # Configurações padrão (podem ser sobrescritas por variáveis de ambiente)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'patrimonio_db')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_CHARSET = 'utf8mb4'
    DB_COLLATION = 'utf8mb4_unicode_ci'
    
    # Connection Pool
    DB_POOL_NAME = 'patrimonio_pool'
    DB_POOL_SIZE = 5
    DB_AUTOCOMMIT = True
    
    # Modo desenvolvimento
    USE_JSON_FILE = os.getenv('USE_JSON_FILE', 'false').lower() == 'true'
    
    @classmethod
    def get_connection_config(cls):
        """Retorna a configuração de conexão formatada"""
        return {
            'host': cls.DB_HOST,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'port': cls.DB_PORT,
            'charset': cls.DB_CHARSET,
            'autocommit': cls.DB_AUTOCOMMIT
        }
    
    @classmethod
    def get_pool_config(cls):
        """Retorna a configuração do connection pool"""
        return {
            'pool_name': cls.DB_POOL_NAME,
            'pool_size': cls.DB_POOL_SIZE,
            'pool_reset_session': True,
            **cls.get_connection_config()
        }

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Configuração para testes"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Selecionar configuração ativa
env = os.getenv('FLASK_ENV', 'development')
if env == 'production':
    app_config = ProductionConfig
elif env == 'testing':
    app_config = TestingConfig
else:
    app_config = DevelopmentConfig
