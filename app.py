# app.py - Entrypoint unificado do Dash + Flask Chatbot

from dash import Dash
import dash_bootstrap_components as dbc
from flask import Flask, render_template, request, jsonify
from src.chatbot import gerar_resposta  # pyright: ignore[reportMissingImports]
from config import DESIGN_CONFIG  # pyright: ignore[reportMissingImports]
from src.layouts.main_layout import create_layout
from src.utils.data_loader import load_metadata
from src.callbacks import register_all
from src.chatbot_interface import register_chatbot_callbacks
from src.utils.data_cache import load_data_once

# -----------------------------------------------------------------------------
# 🔧 Configuração base do servidor Flask e do app Dash
# -----------------------------------------------------------------------------
server = Flask(__name__)

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "/assets/custom.css"  # CSS customizado
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
    try:
        dados = request.get_json()
        mensagem = dados.get("mensagem", "")
        resposta = gerar_resposta(mensagem)
        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"resposta": f"Erro interno: {str(e)}"}), 500

# -----------------------------------------------------------------------------
# 🧩 Carregamento de dados e layout
# -----------------------------------------------------------------------------
# Carrega o DataFrame e metadados ao iniciar
df_full = load_data_once("data/meu_arquivo.csv")
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
    import os
    port = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=port)
