from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import dash
import requests
import os

def create_chatbot_interface():
    return html.Div(
        [
            html.Div(
                id="chatbot-window",
                children=[
                    html.Div(
                        id="chatbot-header",
                        children=[
                            html.H5("Chatbot de Governança", className="mb-0"),
                            dbc.Button("X", id="chatbot-close-button", color="light", size="sm", className="ml-auto"),
                        ],
                        className="d-flex justify-content-between align-items-center p-2 bg-primary text-white rounded-top"
                    ),
                    html.Div(
                        id="chatbot-body",
                        children=[
                            html.Div(className="chatbot-message-container", id="chatbot-messages"),
                            dcc.Loading(
                                id="loading-chatbot-response",
                                type="dot",
                                children=html.Div(id="loading-output-chatbot", style={
                                    "display": "none",
                                    "textAlign": "center",
                                    "padding": "10px"
                                })
                            )
                        ],
                        className="p-3",
                        style={
                            "height": "300px",
                            "overflowY": "auto",
                            "backgroundColor": "#f8f9fa",
                            "borderLeft": "1px solid #dee2e6",
                            "borderRight": "1px solid #dee2e6"
                        }
                    ),
                    html.Div(
                        id="chatbot-input-area",
                        children=[
                            dbc.Input(
                                id="chatbot-input",
                                type="text",
                                placeholder="Digite sua mensagem...",
                                className="flex-grow-1 mr-2"
                            ),
                            dbc.Button(
                                "Enviar",
                                id="chatbot-send-button",
                                color="primary"
                            ),
                        ],
                        className="d-flex p-2 bg-light rounded-bottom"
                    ),
                ],
                style={
                    "position": "fixed",
                    "bottom": "20px",
                    "right": "20px",
                    "width": "350px",
                    "zIndex": "1000",
                    "boxShadow": "0 4px 8px rgba(0,0,0,0.1)",
                    "borderRadius": "8px",
                    "display": "none" # Inicialmente oculto
                }
            ),
            dbc.Button(
                "Abrir Chat",
                id="chatbot-open-button",
                color="primary",
                className="fixed-bottom-right",
                style={
                    "position": "fixed",
                    "bottom": "20px",
                    "right": "20px",
                    "zIndex": "1001",
                    "borderRadius": "50%",
                    "width": "60px",
                    "height": "60px",
                    "fontSize": "1rem",
                    "padding": "0",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center"
                }
            )
        ]
    )

def register_chatbot_callbacks(app):
    @app.callback(
        Output("chatbot-window", "style"),
        Output("chatbot-open-button", "style"),
        Input("chatbot-open-button", "n_clicks"),
        Input("chatbot-close-button", "n_clicks"),
        prevent_initial_call=True
    )
    def toggle_chatbot_window(open_clicks, close_clicks):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        current_window_style = {
            "position": "fixed",
            "bottom": "20px",
            "right": "20px",
            "width": "350px",
            "zIndex": "1000",
            "boxShadow": "0 4px 8px rgba(0,0,0,0.1)",
            "borderRadius": "8px",
        }
        current_open_button_style = {
            "position": "fixed",
            "bottom": "20px",
            "right": "20px",
            "zIndex": "1001",
            "borderRadius": "50%",
            "width": "60px",
            "height": "60px",
            "fontSize": "1rem",
            "padding": "0",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center"
        }

        if button_id == "chatbot-open-button":
            current_window_style["display"] = "block"
            current_open_button_style["display"] = "none"
        elif button_id == "chatbot-close-button":
            current_window_style["display"] = "none"
            current_open_button_style["display"] = "flex"

        return current_window_style, current_open_button_style

    @app.callback(
        Output("chatbot-messages", "children"),
        Output("chatbot-input", "value"),
        Output("loading-output-chatbot", "style"),
        Input("chatbot-send-button", "n_clicks"),
        Input("chatbot-input", "n_submit"),
        State("chatbot-input", "value"),
        State("chatbot-messages", "children"),
        prevent_initial_call=True
    )
    def send_message(send_clicks, submit_clicks, message, current_messages):
        if not message:
            return current_messages, "", {"display": "none"}

        if current_messages is None:
            current_messages = []

        user_message_div = html.Div(message, className="user-message")
        updated_messages = current_messages + [user_message_div]

        loading_style = {"display": "block", "textAlign": "center", "padding": "10px"}

        try:
            # Detectar se está rodando no Render ou localmente
            if os.environ.get('RENDER'):
                # Rodando no Render - usar URL do serviço
                base_url = "https://dash-governanca-chatbot.onrender.com"
            else:
                # Rodando localmente
                base_url = "http://127.0.0.1:8050"
            
            response = requests.post(f"{base_url}/chatbot_responder", json={"mensagem": message})
            response.raise_for_status()
            bot_response = response.json()["resposta"]
        except requests.exceptions.RequestException as e:
            bot_response = f"Erro ao conectar com o chatbot: {e}"
        
        bot_message_div = html.Div(bot_response, className="bot-message")
        updated_messages.append(bot_message_div)

        return updated_messages, "", {"display": "none"}

