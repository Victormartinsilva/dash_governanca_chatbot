# Importa os componentes do Dash necessários para criar elementos HTML e gráficos interativos
from dash import html, dcc

# Importa componentes do Dash Bootstrap para facilitar o layout com cards, linhas e colunas
import dash_bootstrap_components as dbc

# Função que retorna o layout da página "Overview" (Visão Geral)
def overview_layout():
    # Armazena dados filtrados para compartilhamento entre callbacks do Dash
    # 'dcc.Store' é usado para guardar dados no browser sem exibir
    data_store = dcc.Store(id='filtered-data-store')

    # Define o layout principal como um container HTML com estilo profissional
    layout = html.Div([
        # Inclui o armazenamento de dados
        data_store,

        # Título da página
        html.H4("Visão geral", className="mb-4", style={"fontWeight": "bold", "color": "#212529"}),

        # Primeira seção: 4 KPI Cards horizontais
        dbc.Row([
            # Card 1: Contagem de serviços
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='card-servicos', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("Contagem de serviço", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=3
            ),

            # Card 2: Contagem de fluxos
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='card-fluxos', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("Contagem de fluxo", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=3
            ),

            # Card 3: Contagem de formulários
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='card-formularios', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("Contagem de formulário", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=3
            ),

            # Card 4: Contagem de etapas
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H1(id='card-etapas', className="text-center mb-2", 
                               style={"fontSize": "48px", "fontWeight": "bold", "color": "#212529"}),
                        html.P("Contagem de etapa", className="text-center mb-0", 
                              style={"color": "#6c757d", "fontSize": "14px"})
                    ]),
                    className="shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#f8f9fa"}
                ), width=3
            ),
        ], className="mb-4"),

        # Segunda seção: Gráfico de linha - Contagem de fluxo por Mês
        dbc.Card(
            dbc.CardBody([
                html.H5("Contagem de fluxo por Mês", className="mb-3", 
                       style={"fontWeight": "600", "color": "#212529"}),
                dcc.Graph(id='fluxo-por-mes', style={"height": "350px"})
            ]),
            className="mb-4 shadow-sm",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff"}
        ),

        # Terceira seção: Dois gráficos lado a lado
        dbc.Row([
            # Gráfico de barras horizontais - Contagem de formulário por serviço (esquerda)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5(
                            "Contagem de Formulários por Serviço",
                            className="mb-3",
                            style={
                                "fontWeight": "600",
                                "color": "#1a1a1a",
                                "fontSize": "18px"
                            }
                        ),
                        dcc.Graph(
                            id='formulario-por-servico',
                            style={"height": "450px"},
                            config={"displayModeBar": False}  # Oculta barra de ferramentas do Plotly
                        )
                    ]),
                    className="mb-4 shadow-sm",
                    style={
                        "border": "1px solid #dee2e6",
                        "backgroundColor": "#f8f9fa",  # leve cinza para contraste com fundo branco
                        "borderRadius": "12px"
                    }
                )
            ], width=6),
            
            # Gráfico de barras horizontais - Contagem de serviço por fluxo (direita)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Contagem de serviço por fluxo", className="mb-3", 
                               style={"fontWeight": "600", "color": "#212529"}),
                        dcc.Graph(id='servico-por-fluxo', style={"height": "450px"})
                    ]),
                    className="mb-4 shadow-sm",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff"}
                )
            ], width=6),
        ], className="mb-4"),

        # Quinta seção: Tabela detalhada
        dbc.Card(
            dbc.CardBody([
                html.H5("Detalhamento de Fluxos e Serviços", className="mb-3", 
                       style={"fontWeight": "600", "color": "#212529"}),
                html.Div(id='tabela-detalhada')
            ]),
            className="mb-4 shadow-sm",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff"}
        ),
    ], style={"padding": "20px", "backgroundColor": "#ffffff"})
    
    # Retorna o layout completo para ser usado na aplicação
    return layout
