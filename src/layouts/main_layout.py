from dash import html, dcc
from src.chatbot_interface import create_chatbot_interface
import dash_bootstrap_components as dbc
from config import DESIGN_CONFIG

def create_layout(meta):
    header = html.Div(
        html.H1("Painel de Governança - Santos", style={
            "color": DESIGN_CONFIG["title_color"],
            "textAlign": "center",
            "marginBottom": "0"
        }),
        style={
            "backgroundColor": DESIGN_CONFIG["card_background_color"],
            "padding": "15px",
            "borderBottom": f"1px solid {DESIGN_CONFIG['border_color']}",
            "marginBottom": "15px"
        }
    )

    filtros = dbc.Row(
        [
            dbc.Col(
                dcc.Dropdown(
                    id="ano-dropdown",
                    options=[{"label": y, "value": y} for y in meta["anos"]],
                    placeholder="Ano",
                    className="dash-dropdown"
                ),
                md=3
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="fluxo-dropdown",
                    options=[{"label": f, "value": f} for f in meta["fluxos"]],
                    placeholder="Fluxo",
                    className="dash-dropdown"
                ),
                md=3
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="servico-dropdown",
                    options=[{"label": s, "value": s} for s in meta["servicos"]],
                    placeholder="Serviço",
                    className="dash-dropdown"
                ),
                md=3
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="formulario-dropdown",
                    options=[{"label": f, "value": f} for f in meta["formularios"]],
                    placeholder="Formulário",
                    className="dash-dropdown"
                ),
                md=3
            ),
        ],
        className="mb-4"
    )

    tabs = dbc.Tabs(
        [
            dbc.Tab(label="Visão Geral", tab_id="visao-geral", className="custom-tab", active_tab_class_name="custom-tab--selected"),
            dbc.Tab(label="Fluxos/Serviços", tab_id="fluxos-servicos", className="custom-tab", active_tab_class_name="custom-tab--selected"),
            dbc.Tab(label="Formulários", tab_id="formularios", className="custom-tab", active_tab_class_name="custom-tab--selected"),
            dbc.Tab(label="Campos", tab_id="campos", className="custom-tab", active_tab_class_name="custom-tab--selected"),
        ],
        id="main-tabs",
        active_tab="visao-geral",
        className="mb-4 custom-tabs-container"
    )

    content = html.Div(id="page-content", style={"padding": "10px"})

    return dbc.Container(
        [
            dcc.Location(id="url", refresh=False),
            header,
            filtros,
            dbc.Button("Limpar Filtros", id="limpar-filtros", color="primary", className="mb-4"),
            tabs,
            content,
            create_chatbot_interface() # Adiciona a interface do chatbot
        ],
        fluid=True,
        style={
            "backgroundColor": DESIGN_CONFIG["background_color"],
            "minHeight": "100vh",
            "paddingTop": "15px"
        }
    )