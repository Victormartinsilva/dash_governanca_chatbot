# app.py - Entrypoint unificado do Dash + Flask Chatbot

from dash import Dash
import dash_bootstrap_components as dbc
from flask import Flask, render_template, request, jsonify
import os
from src.chatbot import gerar_resposta  # pyright: ignore[reportMissingImports]
from config import DESIGN_CONFIG  # pyright: ignore[reportMissingImports]
from src.layouts.main_layout import create_layout
from src.utils.data_loader import load_metadata
from src.callbacks import register_all
from src.chatbot_interface import register_chatbot_callbacks
from src.utils.data_cache import clear_cache

# -----------------------------------------------------------------------------
# 🔧 Configuração base do servidor Flask e do app Dash
# -----------------------------------------------------------------------------
server = Flask(__name__)

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "/assets/custom.css",  # CSS customizado
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"  # Font Awesome para ícones
]

app = Dash(
    __name__,
    server=server,  # <-- Usa o mesmo servidor Flask
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
    title="Painel de Governança - Santos"
)

# -----------------------------------------------------------------------------
# 🤖 Rotas Flask (Chatbot)
# -----------------------------------------------------------------------------
@server.route("/chatbot_index")
def chatbot_index():
    return render_template("index.html")

@server.route("/chatbot_responder", methods=["POST"])
def chatbot_responder():
    """
    Rota Flask para receber mensagens do chatbot e retornar respostas.
    
    Esta rota:
    - Recebe mensagem e session_id do frontend
    - Chama função gerar_resposta com contexto
    - Retorna resposta em formato JSON
    
    Request JSON:
        {
            "mensagem": "texto da pergunta",
            "session_id": "id_da_sessao" (opcional)
        }
    
    Response JSON:
        {
            "resposta": "texto da resposta"
        }
    """
    try:
        # Obtém dados do request JSON
        dados = request.get_json()
        mensagem = dados.get("mensagem", "")
        session_id = dados.get("session_id", "default")
        
        # Valida se há mensagem
        if not mensagem:
            return jsonify({"resposta": "Por favor, envie uma mensagem válida."}), 400
        
        # Gera resposta usando o chatbot
        from src.chatbot import gerar_resposta
        resposta = gerar_resposta(mensagem, session_id)
        
        # Retorna resposta em formato JSON
        return jsonify({"resposta": resposta})
        
    except Exception as e:
        # Log do erro e retorno de erro genérico
        import logging
        logging.error(f"Erro no chatbot_responder: {e}")
        return jsonify({"resposta": f"Erro interno: {str(e)}"}), 500

@server.route("/clear_cache", methods=["POST"])
def clear_cache_endpoint():
    """Endpoint para limpar o cache de dados via API"""
    try:
        from src.utils.data_cache import clear_cache, get_cache_info
        info_antes = get_cache_info()
        clear_cache()
        info_depois = get_cache_info()
        return jsonify({
            "status": "success",
            "message": "Cache limpo com sucesso",
            "antes": {
                "arquivos_em_cache": info_antes['data_files_cached'],
                "memoria_mb": round(info_antes['total_memory_usage'], 2)
            },
            "depois": {
                "arquivos_em_cache": info_depois['data_files_cached'],
                "memoria_mb": round(info_depois['total_memory_usage'], 2)
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# -----------------------------------------------------------------------------
# 🧩 Carregamento de dados e layout
# -----------------------------------------------------------------------------
# Limpa o cache para garantir dados atualizados
clear_cache()

# Carrega metadados ao iniciar (usando caminho relativo - será convertido internamente)
meta = load_metadata("data/meu_arquivo.csv")

# Define o layout principal
app.layout = create_layout(meta)

# -----------------------------------------------------------------------------
# 🔄 Callbacks
# -----------------------------------------------------------------------------
register_all(app)
register_chatbot_callbacks(app)

# -----------------------------------------------------------------------------
# 🚀 Inicialização
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=port)
