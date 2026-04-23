from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from config import DevelopmentConfig, DatabaseConfig
from database import (
    init_database, test_connection, init_connection_pool,
    get_patrimonios_from_db, get_patrimonio_by_id,
    insert_patrimonio, update_patrimonio, delete_patrimonio,
    dar_baixa_patrimonio, get_relatorio_ativos, get_relatorio_inativos,
    get_relatorio_geral, search_patrimonios
)
from pydantic import BaseModel
import json
import os

app = FastAPI(
    title="API de Patrimônio",
    description="Sistema de gerenciamento de bens e patrimônios com MySQL",
    version="2.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== PYDANTIC MODELS =====

class PatrimonioBase(BaseModel):
    descricao: str
    categoria: str = "Geral"
    valor: float = 0.0
    data_aquisicao: str = None
    localizacao: str = "Não informado"
    responsavel: str = "Não informado"
    observacoes: str = ""

class PatrimonioCreate(PatrimonioBase):
    pass

class PatrimonioUpdate(BaseModel):
    descricao: str = None
    categoria: str = None
    valor: float = None
    localizacao: str = None
    responsavel: str = None
    observacoes: str = None

class BaixaRequest(BaseModel):
    motivo: str = "Não especificado"

# ===== UTILITÁRIOS =====

def format_patrimonio(patrimonio):
    """Formata um patrimônio para JSON response"""
    if not patrimonio:
        return None
    
    if isinstance(patrimonio, dict):
        p = patrimonio.copy()
        if 'valor' in p and p['valor']:
            p['valor'] = float(p['valor'])
        for date_field in ['data_aquisicao', 'data_cadastro', 'data_baixa']:
            if date_field in p and p[date_field]:
                p[date_field] = p[date_field].isoformat() if hasattr(p[date_field], 'isoformat') else str(p[date_field])
        return p
    return patrimonio

def format_patrimonios(patrimonios):
    """Formata uma lista de patrimônios"""
    return [format_patrimonio(p) for p in (patrimonios or [])]


# ===== ROTAS DA API =====

@app.get("/api/saude")
def saude():
    """Endpoint de saúde da API - verifica se está operacional"""
    try:
        test_connection()
        return {
            'status': 'sucesso',
            'mensagem': 'API de Patrimônio está operacional (FastAPI + MySQL)',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'banco_dados': 'MySQL',
            'framework': 'FastAPI'
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"API indisponível: {str(e)}"
        )


@app.get("/api/patrimonios")
def listar_patrimonios():
    """Lista todos os patrimônios do banco de dados"""
    try:
        patrimonios = get_patrimonios_from_db()
        return {
            'status': 'sucesso',
            'total': len(patrimonios),
            'patrimonios': format_patrimonios(patrimonios)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar patrimônios: {str(e)}"
        )


@app.post("/api/patrimonios", status_code=201)
def adicionar_patrimonio(patrimonio: PatrimonioCreate):
    """Adiciona um novo patrimônio ao banco de dados"""
    try:
        if not patrimonio.descricao:
            raise HTTPException(
                status_code=400,
                detail="Campo 'descricao' é obrigatório"
            )
        
        novo_patrimonio = {
            'descricao': patrimonio.descricao,
            'categoria': patrimonio.categoria or 'Geral',
            'valor': patrimonio.valor or 0.0,
            'data_aquisicao': patrimonio.data_aquisicao or datetime.now().strftime('%Y-%m-%d'),
            'localizacao': patrimonio.localizacao or 'Não informado',
            'responsavel': patrimonio.responsavel or 'Não informado',
            'status': 'Ativo',
            'observacoes': patrimonio.observacoes or ''
        }
        
        patrimonio_id = insert_patrimonio(novo_patrimonio)
        novo_patrimonio['id'] = patrimonio_id
        
        return {
            'status': 'sucesso',
            'mensagem': 'Patrimônio adicionado com sucesso',
            'patrimonio': format_patrimonio(novo_patrimonio)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao adicionar patrimônio: {str(e)}"
        )


@app.get("/api/patrimonios/{patrimonio_id}")
def obter_patrimonio(patrimonio_id: int):
    """Obtém informações de um patrimônio específico"""
    try:
        patrimonio = get_patrimonio_by_id(patrimonio_id)
        
        if not patrimonio:
            raise HTTPException(
                status_code=404,
                detail=f"Patrimônio com ID {patrimonio_id} não encontrado"
            )
        
        return {
            'status': 'sucesso',
            'patrimonio': format_patrimonio(patrimonio)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter patrimônio: {str(e)}"
        )


@app.put("/api/patrimonios/{patrimonio_id}")
def atualizar_patrimonio(patrimonio_id: int, patrimonio: PatrimonioUpdate):
    """Atualiza informações de um patrimônio"""
    try:
        patrimonio_existente = get_patrimonio_by_id(patrimonio_id)
        
        if not patrimonio_existente:
            raise HTTPException(
                status_code=404,
                detail=f"Patrimônio com ID {patrimonio_id} não encontrado"
            )
        
        dados_atualizacao = {}
        
        # Mapear campos que podem ser atualizados
        if patrimonio.descricao is not None:
            dados_atualizacao['descricao'] = patrimonio.descricao
        if patrimonio.categoria is not None:
            dados_atualizacao['categoria'] = patrimonio.categoria
        if patrimonio.valor is not None:
            dados_atualizacao['valor'] = float(patrimonio.valor)
        if patrimonio.localizacao is not None:
            dados_atualizacao['localizacao'] = patrimonio.localizacao
        if patrimonio.responsavel is not None:
            dados_atualizacao['responsavel'] = patrimonio.responsavel
        if patrimonio.observacoes is not None:
            dados_atualizacao['observacoes'] = patrimonio.observacoes
        
        update_patrimonio(patrimonio_id, dados_atualizacao)
        
        # Buscar dados atualizados
        patrimonio_atualizado = get_patrimonio_by_id(patrimonio_id)
        
        return {
            'status': 'sucesso',
            'mensagem': 'Patrimônio atualizado com sucesso',
            'patrimonio': format_patrimonio(patrimonio_atualizado)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar patrimônio: {str(e)}"
        )


@app.delete("/api/patrimonios/{patrimonio_id}")
def deletar_patrimonio(patrimonio_id: int):
    """Deleta um patrimônio permanentemente do banco de dados"""
    try:
        patrimonio_existente = get_patrimonio_by_id(patrimonio_id)
        
        if not patrimonio_existente:
            raise HTTPException(
                status_code=404,
                detail=f"Patrimônio com ID {patrimonio_id} não encontrado"
            )
        
        delete_patrimonio(patrimonio_id)
        
        return {
            'status': 'sucesso',
            'mensagem': 'Patrimônio deletado permanentemente',
            'patrimonio': format_patrimonio(patrimonio_existente)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar patrimônio: {str(e)}"
        )


@app.post("/api/patrimonios/{patrimonio_id}/baixa")
def dar_baixa_endpoint(patrimonio_id: int, dados: BaixaRequest):
    """Dar baixa em um patrimônio (desativar)"""
    try:
        patrimonio_existente = get_patrimonio_by_id(patrimonio_id)
        
        if not patrimonio_existente:
            raise HTTPException(
                status_code=404,
                detail=f"Patrimônio com ID {patrimonio_id} não encontrado"
            )
        
        if patrimonio_existente.get('status') == 'Inativo':
            raise HTTPException(
                status_code=400,
                detail="Este patrimônio já está inativo"
            )
        
        motivo = dados.motivo or 'Não especificado'
        
        dar_baixa_patrimonio(patrimonio_id, motivo)
        
        # Buscar dados atualizados
        patrimonio_atualizado = get_patrimonio_by_id(patrimonio_id)
        
        return {
            'status': 'sucesso',
            'mensagem': 'Patrimônio desativado com sucesso',
            'patrimonio': format_patrimonio(patrimonio_atualizado)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao dar baixa: {str(e)}"
        )


@app.get("/api/relatorios/ativos")
def relatorio_ativos():
    """Relatório de patrimônios ativos"""
    try:
        resultado = get_relatorio_ativos()
        return {
            'status': 'sucesso',
            'total_ativos': resultado.get('total_ativos', 0),
            'valor_total': resultado.get('valor_total', 0),
            'valor_medio': resultado.get('valor_medio', 0),
            'patrimonios': format_patrimonios(resultado.get('patrimonios', []))
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório de ativos: {str(e)}"
        )


@app.get("/api/relatorios/inativos")
def relatorio_inativos():
    """Relatório de patrimônios inativos"""
    try:
        resultado = get_relatorio_inativos()
        return {
            'status': 'sucesso',
            'total_inativos': resultado.get('total_inativos', 0),
            'valor_total': resultado.get('valor_total', 0),
            'valor_medio': resultado.get('valor_medio', 0),
            'patrimonios': format_patrimonios(resultado.get('patrimonios', []))
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório de inativos: {str(e)}"
        )


@app.get("/api/relatorios/geral")
def relatorio_geral_endpoint():
    """Relatório geral de patrimônios"""
    try:
        resultado = get_relatorio_geral()
        return {
            'status': 'sucesso',
            'resumo': resultado
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar relatório geral: {str(e)}"
        )


@app.get("/api/patrimonios/buscar")
def buscar_patrimonios(q: str = Query(..., min_length=2)):
    """Busca patrimônios por descrição"""
    try:
        if not q or len(q) < 2:
            raise HTTPException(
                status_code=400,
                detail="Termo de busca deve ter no mínimo 2 caracteres"
            )
        
        resultados = search_patrimonios(q)
        
        return {
            'status': 'sucesso',
            'total': len(resultados),
            'patrimonios': format_patrimonios(resultados)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar patrimônios: {str(e)}"
        )


# ===== INICIALIZAÇÃO =====

if __name__ == '__main__':
    print("=" * 60)
    print("Inicializando API de Patrimônio com MySQL")
    print("=" * 60)
    
    try:
        print("\n[1/3] Inicializando pool de conexões...")
        init_connection_pool()
        print("✓ Pool de conexões inicializado")
        
        print("\n[2/3] Testando conexão com banco de dados...")
        test_connection()
        print("✓ Conexão com banco de dados bem-sucedida")
        
        print("\n[3/3] Inicializando banco de dados...")
        init_database()
        print("✓ Banco de dados inicializado")
        
        print("\n" + "=" * 60)
        print("API pronta para receber requisições")
        print("URL: http://localhost:8000")
        print("Docs: http://localhost:8000/docs")
        print("Redoc: http://localhost:8000/redoc")
        print("=" * 60 + "\n")
        
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
        
    except Exception as e:
        print(f"\n✗ Erro ao iniciar API: {e}")
        print("\nVerifique:")
        print("1. MySQL está rodando?")
        print("2. Arquivo .env foi criado?")
        print("3. Banco de dados 'patrimonio_db' existe?")
        exit(1)
