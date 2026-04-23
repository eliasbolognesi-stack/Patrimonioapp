#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Instalação e Configuração da API de Patrimônio
Executa automaticamente a instalação de dependências
"""

import subprocess
import sys
import os

def print_section(title):
    """Printa uma seção formatada"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def executar_comando(comando, descricao):
    """Executa um comando e mostra o progresso"""
    print(f"\n🔄 {descricao}...")
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if resultado.returncode == 0:
            print(f"✅ {descricao} - SUCESSO")
            return True
        else:
            print(f"❌ {descricao} - FALHA")
            print(f"Erro: {resultado.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")
        return False

def main():
    """Função principal de instalação"""
    
    print_section("🚀 INSTALAÇÃO - API DE PATRIMÔNIO")
    
    print("\n📋 Verificando ambiente...")
    
    # Verificar se Python está instalado
    try:
        resultado = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✅ Python encontrado: {resultado.stdout.strip()}")
    except:
        print("❌ Python não encontrado. Instale Python 3.7+")
        sys.exit(1)
    
    # Instalando pip (se necessário)
    print("\n📦 Verificando pip...")
    executar_comando(f"{sys.executable} -m pip --version", "Verificando pip")
    
    # Atualizando pip
    print("\n⬆️  Atualizando pip...")
    executar_comando(f"{sys.executable} -m pip install --upgrade pip", "Atualizando pip")
    
    # Instalando dependências
    print("\n📚 Instalando dependências do projeto...")
    if os.path.exists('requirements.txt'):
        sucesso = executar_comando(
            f"{sys.executable} -m pip install -r requirements.txt",
            "Instalando pacotes do requirements.txt"
        )
        if not sucesso:
            print("\n⚠️  Tentando instalar manualmente...")
            executar_comando(f"{sys.executable} -m pip install Flask==2.3.0 Werkzeug==2.3.0", "Instalação manual")
    else:
        print("⚠️  arquivo requirements.txt não encontrado")
        print("   Instalando Flask manualmente...")
        executar_comando(f"{sys.executable} -m pip install Flask==2.3.0 Werkzeug==2.3.0", "Instalação manual do Flask")
    
    # Verificar arquivos
    print("\n📁 Verificando arquivos necessários...")
    arquivos = ['main.py', 'app.py', 'requirements.txt', 'README.md']
    todos_existem = True
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo} - NÃO ENCONTRADO")
            todos_existem = False
    
    if not todos_existem:
        print("\n⚠️  Alguns arquivos não foram encontrados!")
        return False
    
    # Resumo final
    print_section("✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO")
    
    print("\n🚀 Para iniciar a API, execute em um terminal:")
    print("   python main.py")
    print("\n📍 A API estará disponível em: http://localhost:5000")
    
    print("\n🧪 Para testar a API (em outro terminal):")
    print("   python teste_api.py")
    
    print("\n📚 Para mais informações, consulte README.md")
    
    print("\n" + "=" * 60)
    print(" Pressione ENTER para sair")
    print("=" * 60)
    
    input()
    return True

if __name__ == '__main__':
    try:
        sucesso = main()
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\n⛔ Instalação cancelada pelo usuário")
        sys.exit(1)
