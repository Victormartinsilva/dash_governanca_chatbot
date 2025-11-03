# Importa os componentes do Dash necessários para criar elementos HTML e gráficos interativos
from dash import html, dcc

# Importa componentes do Dash Bootstrap para facilitar o layout com cards, linhas e colunas
import dash_bootstrap_components as dbc

# Função que retorna o layout da página "Formulários" (Análise de Formulários)
def formularios_layout():
    # Armazena dados filtrados para compartilhamento entre callbacks do Dash
    # 'dcc.Store' é usado para guardar dados no browser sem exibir
    data_store = dcc.Store(id='filtered-data-store')

    # Define o layout principal como um container HTML com estilo profissional
    layout = html.Div([
        # Inclui o armazenamento de dados
        data_store,

        # Título da página
        html.H4("Análise de Formulários", className="mb-4", style={"fontWeight": "bold", "color": "#212529"}),

        # Primeira seção: 4 KPI Cards horizontais
        dbc.Row([
            # Card 1: Formulários
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='card-formularios-form', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("Formulários", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=3
            ),

            # Card 2: Campos
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='card-campos-form', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("Campos", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=3
            ),

            # Card 3: Média Campos por Formulário
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='media-campos-formulario', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("Média Campos por Formulário", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=3
            ),

            # Card 4: Campos Padrão
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='pct-formularios-padrao', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("Campos Padrão", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=3
            ),
        ], className="mb-4"),

        # Segunda seção: Dois gráficos lado a lado
        dbc.Row([
            # Gráfico de barras horizontais - Formulários Mais Utilizados em Fluxos de Trabalho (esquerda)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5(
                            "Formulários Mais Utilizados em Fluxos de Trabalho",
                            className="mb-2",
                            style={
                                "fontWeight": "600",
                                "color": "#1a1a1a",
                                "fontSize": "18px"
                            }
                        ),
                        html.P(
                            "Formulários por Fluxo",
                            className="mb-3",
                            style={
                                "color": "#6c757d",
                                "fontSize": "14px",
                                "marginBottom": "1rem"
                            }
                        ),
                        dcc.Graph(
                            id='formularios-mais-usados',
                            style={"height": "450px"},
                            config={"displayModeBar": False}
                        )
                    ]),
                    className="mb-4 shadow-sm",
                    style={
                        "border": "1px solid #dee2e6",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "12px",
                        "height": "100%"
                    }
                )
            ], width=6, style={"paddingLeft": "10px", "paddingRight": "5px"}),
            
            # Gráfico de barras horizontais - Formulários que Utilizados Mais Campos (direita)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5(
                            "Formulários que Utilizados Mais Campos",
                            className="mb-2",
                            style={
                                "fontWeight": "600",
                                "color": "#1a1a1a",
                                "fontSize": "18px"
                            }
                        ),
                        html.P(
                            "Qnt Campos",
                            className="mb-3",
                            style={
                                "color": "#6c757d",
                                "fontSize": "14px",
                                "marginBottom": "1rem"
                            }
                        ),
                        dcc.Graph(
                            id='complexidade-formularios-form',
                            style={"height": "450px"},
                            config={"displayModeBar": False}
                        )
                    ]),
                    className="mb-4 shadow-sm",
                    style={
                        "border": "1px solid #dee2e6",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "12px",
                        "height": "100%"
                    }
                )
            ], width=6, style={"paddingLeft": "5px", "paddingRight": "10px"}),
        ], className="mb-4"),

        # Terceira seção: Tabela - Ranking Formulários por uso Fluxos x Qnt. Campos
        dbc.Card(
            dbc.CardBody([
                html.H5("Ranking Formulários por uso Fluxos x Qnt. Campos", className="mb-3", 
                       style={"fontWeight": "600", "color": "#212529"}),
                html.Div(
                    id='formularios-utilizados-table',
                    style={"width": "100%", "overflow": "auto"}
                )
            ]),
            className="mb-4 shadow-sm",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff"}
        ),

        # Quarta seção: Análise de Risco vs. Complexidade dos Fluxos
        dbc.Card(
            dbc.CardBody([
                html.H5("Análise de Risco vs. Complexidade dos Fluxos", className="mb-3", 
                       style={"fontWeight": "600", "color": "#212529"}),
                html.P(
                    "Análise de risco e complexidade dos fluxos baseada em campos e padronização",
                    className="mb-3",
                    style={"color": "#6c757d", "fontSize": "14px"}
                ),
                dcc.Graph(
                    id='analise-fluxo-complexidade',
                    style={"height": "600px"},
                    config={"displayModeBar": False}
                )
            ]),
            className="mb-4 shadow-sm",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff"}
        ),
    ], style={"padding": "20px", "backgroundColor": "#ffffff"})
    
    # Retorna o layout completo para ser usado na aplicação
    return layout
