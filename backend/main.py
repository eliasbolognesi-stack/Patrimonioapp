#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal para rodar a API de Patrimônio com FastAPI + MySQL
Pode ser executado tanto no terminal quanto no bash
"""

import sys
import os
import uvicorn
from backend.app import app
from backend.database import init_connection_pool, test_connection, init_database
from backend.config import DevelopmentConfig

def print_header():
    """Imprime o cabeçalho de inicialização"""
    print("\n" + "=" * 70)
    print(" " * 10 + "🏛️  API DE PATRIMÔNIO - FastAPI + MySQL 🏛️")
    print("=" * 70)

def print_endpoints():
    """Imprime os endpoints disponíveis"""
    print("\n📚 ENDPOINTS DISPONÍVEIS:\n")
    endpoints = [
        ("✅ GET",    "/api/saude",                  "Verificar status da API"),
        ("📋 GET",    "/api/patrimonios",             "Listar todos os patrimônios"),
        ("📋 GET",    "/api/patrimonios/buscar",      "Buscar patrimônios por termo"),
        ("➕ POST",   "/api/patrimonios",             "Adicionar novo patrimônio"),
        ("🔍 GET",    "/api/patrimonios/{id}",        "Obter patrimônio específico"),
        ("✏️  PUT",    "/api/patrimonios/{id}",        "Atualizar patrimônio"),
        ("❌ DELETE", "/api/patrimonios/{id}",        "Deletar patrimônio"),
        ("📉 POST",   "/api/patrimonios/{id}/baixa",  "Dar baixa em patrimônio"),
        ("📊 GET",    "/api/relatorios/ativos",       "Relatório de patrimônios ativos"),
        ("📊 GET",    "/api/relatorios/inativos",     "Relatório de patrimônios inativos"),
        ("📊 GET",    "/api/relatorios/geral",        "Relatório geral"),
    ]
    
    for method, path, desc in endpoints:
        print(f"  {method:<12} {path:<40} - {desc}")

def main():
    """Função principal"""
    print_header()
    
    print("\n🔧 Configuração:")
    config = DevelopmentConfig
    print(f"  Banco de Dados: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
    print(f"  Usuário: {config.DB_USER}")
    print(f"  Ambiente: {config.FLASK_ENV}")
    print(f"  Framework: FastAPI + Uvicorn")
    
    print("\n" + "-" * 70)
    print("\n⏳ Inicializando conexão com banco de dados...\n")
    
    try:
        # Etapa 1: Inicializar pool de conexões
        print("  [1/3] Criando pool de conexões...")
        init_connection_pool()
        print("        ✓ Pool criado com sucesso")
        
        # Etapa 2: Testar conexão
        print("  [2/3] Testando conexão com MySQL...")
        test_connection()
        print("        ✓ Conexão testada com sucesso")
        
        # Etapa 3: Inicializar banco de dados
        print("  [3/3] Inicializando banco de dados...")
        init_database()
        print("        ✓ Banco de dados inicializado")
        
        print("\n" + "-" * 70)
        print("\n📍 Localhost URL: http://localhost:8000")
        print("🌐 Rede Local: http://0.0.0.0:8000")
        print("📚 Documentação Interativa: http://localhost:8000/docs")
        print("📖 ReDoc: http://localhost:8000/redoc")
        print("✅ API Status: http://localhost:8000/api/saude")
        
        print_endpoints()
        
        print("\n" + "-" * 70)
        print("\n💾 Armazenamento: MySQL")
        print("🔐 Autenticação: SessionStorage (desenvolvimento)")
        print("⚡ Performance: FastAPI + Uvicorn + Connection Pool")
        print("\nPressione CTRL+C para encerrar o servidor\n")
        print("=" * 70 + "\n")
        
        # Iniciar servidor Uvicorn
        uvicorn.run(
            "backend.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("⛔ Servidor encerrado pelo usuário")
        print("=" * 70 + "\n")
        sys.exit(0)
        
    except ConnectionError as e:
        print("\n" + "=" * 70)
        print("❌ ERRO: Não foi possível conectar ao MySQL")
        print("=" * 70)
        print("\n⚠️  Verifique:")
        print("  1. O servidor MySQL está rodando?")
        print("  2. O arquivo .env foi criado em backend/?")
        print("  3. As credenciais de banco de dados estão corretas?")
        print("  4. O banco 'patrimonio_db' existe?")
        print(f"\nDetalhes do erro: {e}\n")
        sys.exit(1)
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ ERRO ao iniciar a API de Patrimônio")
        print("=" * 70)
        print(f"\nDetalhes: {e}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
