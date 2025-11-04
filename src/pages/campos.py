# Importa os componentes do Dash necessários para criar elementos HTML e gráficos interativos
from dash import html, dcc

# Importa componentes do Dash Bootstrap para facilitar o layout com cards, linhas e colunas
import dash_bootstrap_components as dbc

# Função que retorna o layout da página "Campos" (Análise de Campos)
def campos_layout():
    # Armazena dados filtrados para compartilhamento entre callbacks do Dash
    # 'dcc.Store' é usado para guardar dados no browser sem exibir
    data_store = dcc.Store(id='filtered-data-store')

    # Define o layout principal como um container HTML com estilo profissional
    layout = html.Div([
        # Inclui o armazenamento de dados
        data_store,

        # Título da página
        html.H4("Análise de Campos", className="mb-4", style={"fontWeight": "bold", "color": "#212529"}),

        # Primeira seção: 3 KPI Cards horizontais
        dbc.Row([
            # Card 1: Qtd Campos Distintos
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='card-campos-distintos', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("Qtd Campos Distintos", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=4
            ),

            # Card 2: Qtd Campos Padronizados Total
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='card-campos-padronizados', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("Qtd Campos Padronizados Total", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=4
            ),

            # Card 3: % Campos Padronizados
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='pct-campos-padrao', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("% Campos Padronizados", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=4
            ),
        ], className="mb-4"),

        # Segunda seção: Gráfico - Campos Mais Usados
        dbc.Card(
            dbc.CardBody([
                html.H5("Campos Mais Usados", className="mb-3", 
                       style={"fontWeight": "600", "color": "#212529"}),
                dcc.Graph(id='campos-mais-usados', style={"height": "450px"},
                         config={"displayModeBar": False})
            ]),
            className="mb-4 shadow-sm",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff"}
        ),

        # Terceira seção: Dois gráficos lado a lado
        dbc.Row([
            # Gráfico - Campos com Variações (esquerda)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Campos com Variações", className="mb-3", 
                               style={"fontWeight": "600", "color": "#212529"}),
                        dcc.Graph(
                            id='campos-com-variacoes',
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
            
            # Tabela - Autoria de Dados (direita)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Autoria de Dados", className="mb-3", 
                               style={"fontWeight": "600", "color": "#212529"}),
                        html.Div(
                            id='tabela-autoria-dados',
                            style={"width": "100%", "overflow": "auto"}
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

        # Quarta seção: Gráfico - Diversidade de Campos por Tipo
        dbc.Card(
            dbc.CardBody([
                html.H5("Diversidade de Campos por Tipo", className="mb-3", 
                       style={"fontWeight": "600", "color": "#212529"}),
                dcc.Graph(id='diversidade-campos-tipo', style={"height": "450px"},
                         config={"displayModeBar": False})
            ]),
            className="mb-4 shadow-sm",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff"}
        ),
    ], style={"padding": "20px", "backgroundColor": "#ffffff"})
    
    # Retorna o layout completo para ser usado na aplicação
    return layout
