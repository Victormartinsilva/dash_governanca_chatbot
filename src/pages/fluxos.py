# Importa os componentes do Dash necessários para criar elementos HTML e gráficos interativos
from dash import html, dcc

# Importa componentes do Dash Bootstrap para facilitar o layout com cards, linhas e colunas
import dash_bootstrap_components as dbc

# Função que retorna o layout da página "Fluxos/Serviços" (Análise de Fluxos)
def fluxos_layout():
    # Armazena dados filtrados para compartilhamento entre callbacks do Dash
    # 'dcc.Store' é usado para guardar dados no browser sem exibir
    data_store = dcc.Store(id='filtered-data-store')

    # Define o layout principal como um container HTML com estilo profissional
    layout = html.Div([
        # Inclui o armazenamento de dados
        data_store,

        # Título da página
        html.H4("Análise de Fluxos", className="mb-4", style={"fontWeight": "bold", "color": "#212529"}),

        # Primeira seção: 4 KPI Cards horizontais
        dbc.Row([
            # Card 1: Fluxos
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='card-fluxos-fluxo', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("Fluxos", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=3
            ),

            # Card 2: Contagem de serviço
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='card-servicos-fluxo', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("Contagem de serviço", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=3
            ),

            # Card 3: Média Campos por fluxo
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='media-campos-fluxo', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("Média Campos por fluxo", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=3
            ),

            # Card 4: % Fluxo Padronizados
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='pct-fluxo-padronizado', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("% Fluxo Padronizados", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=3
            ),
        ], className="mb-4"),

        # Segunda seção: Gráfico de barras horizontais - Percentual de Padronização por Fluxo
        dbc.Card(
            dbc.CardBody([
                html.H5("Percentual de Padronização por Fluxo", className="mb-3", 
                       style={"fontWeight": "600", "color": "#212529"}),
                dcc.Graph(id='percentual-padronizacao-fluxo', style={"height": "450px"},
                         config={"displayModeBar": False})
            ]),
            className="mb-4 shadow-sm",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff"}
        ),

        # Terceira seção: Dois gráficos lado a lado
        dbc.Row([
            # Gráfico de barras horizontais - Análise de Fluxos por Serviços (esquerda)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5(
                            "Análise de Fluxos por Serviços",
                            className="mb-2",
                            style={
                                "fontWeight": "600",
                                "color": "#1a1a1a",
                                "fontSize": "18px"
                            }
                        ),
                        html.P(
                            "Contagem de serviço por fluxo",
                            className="mb-3",
                            style={
                                "color": "#6c757d",
                                "fontSize": "14px",
                                "marginBottom": "1rem"
                            }
                        ),
                        html.Div(
                            dcc.Graph(
                                id='contagem-servico-por-fluxo',
                                style={"height": "820px"},
                                config={"displayModeBar": False}
                            ),
                            style={"height": "820px", "overflow": "hidden", "width": "100%"}
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
            
            # Tabela - Padronização por Fluxo (direita)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Padronização por Fluxo", className="mb-3", 
                               style={"fontWeight": "600", "color": "#212529"}),
                        html.Div(
                            id='padronizacao-por-fluxo-tabela',
                            style={"width": "100%", "overflow": "hidden"}
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
        
        # Quarta seção: Diagrama Hierárquico - Estrutura de Fluxos
        dbc.Card(
            dbc.CardBody([
                html.H5("Análise de Fluxos", className="mb-3", 
                       style={"fontWeight": "600", "color": "#212529"}),
                html.P(
                    "Estrutura Hierárquica: Fluxo > Serviço > Formulário > Campos",
                    className="mb-3",
                    style={"color": "#6c757d", "fontSize": "14px"}
                ),
                dcc.Graph(id='fluxos-hierarquia-tree', style={"height": "600px"},
                         config={"displayModeBar": False})
            ]),
            className="mb-4 shadow-sm",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff"}
        ),
    ], style={"padding": "20px", "backgroundColor": "#ffffff"})
    
    # Retorna o layout completo para ser usado na aplicação
    return layout
