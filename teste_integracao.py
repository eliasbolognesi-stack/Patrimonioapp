#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para validar integração MySQL da API de Patrimônio
Execute após iniciar main.py em outro terminal
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000/api"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def print_header(title):
    """Imprime cabeçalho de seção"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def print_test(num, desc, status, details=""):
    """Imprime resultado de teste"""
    icon = "✅" if status else "❌"
    print(f"\n{icon} Teste {num}: {desc}")
    if details:
        print(f"   → {details}")

def test_saude():
    """Testa endpoint de saúde"""
    print_header("1. Verificando Saúde da API (MySQL)")
    
    try:
        response = requests.get(f"{BASE_URL}/saude")
        data = response.json()
        
        sucesso = response.status_code == 200 and data['status'] == 'sucesso'
        print_test(1, "Saúde da API", sucesso, 
                  f"Status: {data.get('mensagem')} | Banco: {data.get('banco_dados')}")
        
        return sucesso
    except Exception as e:
        print_test(1, "Saúde da API", False, f"Erro: {str(e)}")
        return False

def test_listar_patrimonios():
    """Testa listagem de patrimônios"""
    print_header("2. Listando Patrimônios")
    
    try:
        response = requests.get(f"{BASE_URL}/patrimonios")
        data = response.json()
        
        sucesso = response.status_code == 200 and data['status'] == 'sucesso'
        total = data.get('total', 0)
        print_test(2, "Listar patrimônios", sucesso, 
                  f"Total encontrado: {total} patrimônios")
        
        return sucesso, data.get('patrimonios', [])
    except Exception as e:
        print_test(2, "Listar patrimônios", False, f"Erro: {str(e)}")
        return False, []

def test_adicionar_patrimonio():
    """Testa adição de patrimônio"""
    print_header("3. Adicionando Novo Patrimônio")
    
    novo_bem = {
        "descricao": f"Computador Dell - {datetime.now().strftime('%H:%M:%S')}",
        "categoria": "Informática",
        "valor": 2500.00,
        "data_aquisicao": "2024-01-10",
        "localizacao": "Sala 101",
        "responsavel": "João Silva",
        "observacoes": "Estado: Bom funcionamento"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/patrimonios", 
                               json=novo_bem, headers=HEADERS)
        data = response.json()
        
        sucesso = response.status_code == 201 and data['status'] == 'sucesso'
        patrimonio_id = data.get('patrimonio', {}).get('id')
        print_test(3, "Adicionar patrimônio", sucesso,
                  f"ID criado: {patrimonio_id} | Descrição: {novo_bem['descricao']}")
        
        return sucesso, patrimonio_id
    except Exception as e:
        print_test(3, "Adicionar patrimônio", False, f"Erro: {str(e)}")
        return False, None

def test_obter_patrimonio(patrimonio_id):
    """Testa obtenção de um patrimônio específico"""
    print_header("4. Obtendo Patrimônio Específico")
    
    if not patrimonio_id:
        print_test(4, "Obter patrimônio", False, "ID não disponível do teste anterior")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/patrimonios/{patrimonio_id}")
        data = response.json()
        
        sucesso = response.status_code == 200 and data['status'] == 'sucesso'
        descricao = data.get('patrimonio', {}).get('descricao', 'N/A')
        print_test(4, "Obter patrimônio", sucesso,
                  f"Descrição: {descricao}")
        
        return sucesso
    except Exception as e:
        print_test(4, "Obter patrimônio", False, f"Erro: {str(e)}")
        return False

def test_atualizar_patrimonio(patrimonio_id):
    """Testa atualização de patrimônio"""
    print_header("5. Atualizando Patrimônio")
    
    if not patrimonio_id:
        print_test(5, "Atualizar patrimônio", False, "ID não disponível do teste anterior")
        return False
    
    atualizacao = {
        "localizacao": "Sala 102 (Transferido)",
        "observacoes": "Transferido para nova sala em 15/01/2024"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/patrimonios/{patrimonio_id}",
                              json=atualizacao, headers=HEADERS)
        data = response.json()
        
        sucesso = response.status_code == 200 and data['status'] == 'sucesso'
        print_test(5, "Atualizar patrimônio", sucesso,
                  f"Localização atualizada para: {atualizacao['localizacao']}")
        
        return sucesso
    except Exception as e:
        print_test(5, "Atualizar patrimônio", False, f"Erro: {str(e)}")
        return False

def test_dar_baixa(patrimonio_id):
    """Testa dar baixa em patrimônio"""
    print_header("6. Dando Baixa em Patrimônio")
    
    if not patrimonio_id:
        print_test(6, "Dar baixa", False, "ID não disponível do teste anterior")
        return False
    
    baixa = {
        "motivo": "Equipamento obsoleto - substituído por versão nova"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/patrimonios/{patrimonio_id}/baixa",
                               json=baixa, headers=HEADERS)
        data = response.json()
        
        sucesso = response.status_code == 200 and data['status'] == 'sucesso'
        status = data.get('patrimonio', {}).get('status', 'N/A')
        print_test(6, "Dar baixa", sucesso,
                  f"Status do bem: {status}")
        
        return sucesso
    except Exception as e:
        print_test(6, "Dar baixa", False, f"Erro: {str(e)}")
        return False

def test_relatorios():
    """Testa endpoints de relatórios"""
    print_header("7. Gerando Relatórios")
    
    relatorios = [
        ("ativos", "Patrimônios Ativos"),
        ("inativos", "Patrimônios Inativos"),
        ("geral", "Relatório Geral")
    ]
    
    todos_ok = True
    
    for tipo, descricao in relatorios:
        try:
            if tipo == "geral":
                response = requests.get(f"{BASE_URL}/relatorios/{tipo}")
                data = response.json()
                sucesso = response.status_code == 200 and data['status'] == 'sucesso'
                resumo = data.get('resumo', {})
                detalhes = f"Total: {resumo.get('total_patrimonios')}, Ativos: {resumo.get('total_ativos')}, Inativos: {resumo.get('total_inativos')}"
            else:
                response = requests.get(f"{BASE_URL}/relatorios/{tipo}")
                data = response.json()
                sucesso = response.status_code == 200 and data['status'] == 'sucesso'
                total_key = f'total_{tipo}'
                count = data.get(total_key, 0)
                valor = data.get('valor_total', 0)
                detalhes = f"Quantidade: {count}, Valor Total: R$ {valor:.2f}"
            
            print_test(f"7.{relatorios.index((tipo, descricao))+1}", 
                      descricao, sucesso, detalhes)
            
            todos_ok = todos_ok and sucesso
        except Exception as e:
            print_test(f"7.{relatorios.index((tipo, descricao))+1}", 
                      descricao, False, f"Erro: {str(e)}")
            todos_ok = False
    
    return todos_ok

def test_busca():
    """Testa busca de patrimônios"""
    print_header("8. Testando Busca")
    
    try:
        response = requests.get(f"{BASE_URL}/patrimonios/buscar?q=dell")
        data = response.json()
        
        sucesso = response.status_code == 200 and data['status'] == 'sucesso'
        total = data.get('total', 0)
        print_test(8, "Busca por termo", sucesso,
                  f"Resultados encontrados: {total}")
        
        return sucesso
    except Exception as e:
        print_test(8, "Busca por termo", False, f"Erro: {str(e)}")
        return False

def main():
    """Função principal"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  🧪 TESTES DE INTEGRAÇÃO MYSQL - API DE PATRIMÔNIO".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    print("\n⏳ Aguardando 2 segundos para garantir API pronta...")
    time.sleep(2)
    
    resultados = []
    
    # Teste 1: Saúde
    if not test_saude():
        print("\n" + "=" * 70)
        print("❌ API não está respondendo!")
        print("   Certifique-se de que:")
        print("   1. main.py está rodando em outro terminal")
        print("   2. MySQL está iniciado")
        print("   3. Arquivo .env está corretamente configurado")
        print("=" * 70 + "\n")
        return
    
    resultados.append(("Saúde da API", True))
    
    # Teste 2: Listar
    sucesso, patrimonios = test_listar_patrimonios()
    resultados.append(("Listar patrimônios", sucesso))
    
    # Teste 3: Adicionar
    sucesso, patrimonio_id = test_adicionar_patrimonio()
    resultados.append(("Adicionar patrimônio", sucesso))
    
    # Teste 4: Obter
    sucesso = test_obter_patrimonio(patrimonio_id)
    resultados.append(("Obter patrimônio", sucesso))
    
    # Teste 5: Atualizar
    sucesso = test_atualizar_patrimonio(patrimonio_id)
    resultados.append(("Atualizar patrimônio", sucesso))
    
    # Teste 6: Dar baixa
    sucesso = test_dar_baixa(patrimonio_id)
    resultados.append(("Dar baixa", sucesso))
    
    # Teste 7: Relatórios
    sucesso = test_relatorios()
    resultados.append(("Relatórios", sucesso))
    
    # Teste 8: Busca
    sucesso = test_busca()
    resultados.append(("Busca", sucesso))
    
    # Relatório final
    print_header("📊 RESUMO DOS TESTES")
    
    total_testes = len(resultados)
    testes_ok = sum(1 for _, ok in resultados if ok)
    
    for i, (teste, ok) in enumerate(resultados, 1):
        icon = "✅" if ok else "❌"
        print(f"  {icon} {teste}")
    
    print("\n" + "-" * 70)
    print(f"\n📈 Resultado: {testes_ok}/{total_testes} testes passaram")
    
    if testes_ok == total_testes:
        print("\n🎉 PARABÉNS! Toda a integração MySQL está funcionando perfeitamente!")
        print("\n✅ Você pode:\n")
        print("   1. Acessar http://localhost:5000 no navegador")
        print("   2. Fazer login com: admin@patrimonio.com / admin123")
        print("   3. Começar a gerenciar seus patrimônios!")
    else:
        print(f"\n⚠️  {total_testes - testes_ok} teste(s) falharam")
        print("   Verifique os erros acima e a documentação SETUP_MYSQL.md")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == '__main__':
    main()
