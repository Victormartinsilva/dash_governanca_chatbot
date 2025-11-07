# Importa os componentes do Dash necessários para criar elementos HTML e gráficos interativos
from dash import html, dcc

# Importa componentes do Dash Bootstrap para facilitar o layout com cards, linhas e colunas
import dash_bootstrap_components as dbc

def create_title_with_tooltip(title_text, tooltip_id, tooltip_content):
    """
    Cria um título com ícone de informação e tooltip.
    
    Args:
        title_text: Texto do título
        tooltip_id: ID único para o tooltip
        tooltip_content: Conteúdo do tooltip (pode ser HTML)
    
    Returns:
        Componente HTML com título e tooltip
    """
    return html.Div([
        html.H5(
            [
                title_text,
                html.Span(
                    html.I(
                        className="fas fa-info-circle",
                        style={
                            "marginLeft": "8px",
                            "color": "#6c757d",
                            "cursor": "pointer",
                            "fontSize": "14px"
                        },
                        id=tooltip_id
                    )
                )
            ],
            className="mb-1",
            style={"fontWeight": "600", "color": "#495057", "display": "flex", "alignItems": "center"}
        ),
        dbc.Tooltip(
            tooltip_content,
            target=tooltip_id,
            placement="right",
            style={
                "maxWidth": "400px", 
                "fontSize": "13px",
                "backgroundColor": "#343a40",
                "color": "#ffffff",
                "border": "1px solid #495057",
                "borderRadius": "8px",
                "padding": "14px",
                "boxShadow": "0 4px 12px rgba(0,0,0,0.3)",
                "zIndex": 1000
            }
        )
    ])

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

        # Segunda seção: Dois gráficos lado a lado (maior importância - topo)
        dbc.Row([
            # Gráfico de barras horizontais - Contagem de fluxo (esquerda)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        create_title_with_tooltip(
                            "Contagem de Fluxo por Quantidade",
                            "tooltip-fluxo-quantidade",
                            html.Div([
                                html.Strong("Nome: ", style={"color": "#ffffff"}),
                                html.Span("Contagem de Fluxo por Quantidade", style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Conceito: ", style={"color": "#ffffff"}),
                                html.Span("Quantidade total de registros por fluxo no período de referência, ordenados do maior para o menor.", 
                                         style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Método de cálculo: ", style={"color": "#ffffff"}),
                                html.Span("Agrupamento e contagem de registros únicos por fluxo.", 
                                         style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Periodicidade de atualização: ", style={"color": "#ffffff"}),
                                html.Span("Trimestral (3 meses).", style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Fonte: ", style={"color": "#ffffff"}),
                                html.Span("MongoDB do ACTO - Período: 2024 até setembro de 2025.", style={"color": "#e9ecef"})
                            ])
                        ),
                        dcc.Graph(
                            id='fluxo-por-mes',
                            config={"displayModeBar": False},
                            style={"height": "450px"}
                        )
                    ]),
                    className="mb-4 shadow-lg",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff", "borderRadius": "12px"}
                )
            ], width=6),
            
            # Gráfico de barras horizontais - Contagem de serviço por fluxo (direita)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        create_title_with_tooltip(
                            "Contagem de Serviço por Fluxo",
                            "tooltip-servico-fluxo",
                            html.Div([
                                html.Strong("Nome: ", style={"color": "#ffffff"}),
                                html.Span("Contagem de Serviço por Fluxo", style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Conceito: ", style={"color": "#ffffff"}),
                                html.Span("Quantidade total de serviços distintos associados a cada fluxo no período de referência, ordenados do maior para o menor.", 
                                         style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Método de cálculo: ", style={"color": "#ffffff"}),
                                html.Span("Agrupamento por fluxo e contagem de serviços únicos.", 
                                         style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Periodicidade de atualização: ", style={"color": "#ffffff"}),
                                html.Span("Trimestral (3 meses).", style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Fonte: ", style={"color": "#ffffff"}),
                                html.Span("MongoDB do ACTO - Período: 2024 até setembro de 2025.", style={"color": "#e9ecef"})
                            ])
                        ),
                        dcc.Graph(
                            id='servico-por-fluxo', 
                            style={"height": "450px"},
                            config={"displayModeBar": False}
                        )
                    ]),
                    className="mb-4 shadow-lg",
                    style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff", "borderRadius": "12px"}
                )
            ], width=6),
        ], className="mb-4"),

        # Terceira seção: Gráfico de barras horizontais - Contagem de formulário por serviço (meio)
        dbc.Card(
            dbc.CardBody([
                create_title_with_tooltip(
                    "Contagem de Formulários por Serviço",
                    "tooltip-formulario-servico",
                    html.Div([
                        html.Strong("Nome: ", style={"color": "#ffffff"}),
                        html.Span("Contagem de Formulários por Serviço", style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Conceito: ", style={"color": "#ffffff"}),
                        html.Span("Quantidade total de formulários distintos associados a cada serviço no período de referência, ordenados do maior para o menor.", 
                                 style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Método de cálculo: ", style={"color": "#ffffff"}),
                        html.Span("Agrupamento por serviço e contagem de formulários únicos.", 
                                 style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Periodicidade de atualização: ", style={"color": "#ffffff"}),
                        html.Span("Trimestral (3 meses).", style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Fonte: ", style={"color": "#ffffff"}),
                        html.Span("MongoDB do ACTO - Período: 2024 até setembro de 2025.", style={"color": "#e9ecef"})
                    ])
                ),
                dcc.Graph(
                    id='formulario-por-servico',
                    style={"height": "450px"},
                    config={"displayModeBar": False}
                )
            ]),
            className="mb-4 shadow-lg",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff", "borderRadius": "12px"}
        ),

        # Quarta seção: Tabela detalhada
        dbc.Card(
            dbc.CardBody([
                create_title_with_tooltip(
                    "Detalhamento de Fluxos e Serviços",
                    "tooltip-tabela-detalhada",
                    html.Div([
                        html.Strong("Nome: ", style={"color": "#ffffff"}),
                        html.Span("Detalhamento de Fluxos e Serviços", style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Conceito: ", style={"color": "#ffffff"}),
                        html.Span("Tabela detalhada apresentando a relação entre fluxos, serviços, formulários e etapas.", 
                                 style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Método de cálculo: ", style={"color": "#ffffff"}),
                        html.Span("Agrupamento e contagem de registros por fluxo, serviço, formulário e etapa.", 
                                 style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Periodicidade de atualização: ", style={"color": "#ffffff"}),
                        html.Span("Trimestral (3 meses).", style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Fonte: ", style={"color": "#ffffff"}),
                        html.Span("MongoDB do ACTO - Período: 2024 até setembro de 2025.", style={"color": "#e9ecef"})
                    ])
                ),
                html.Div(id='tabela-detalhada', className="mt-3")
            ]),
            className="mb-4 shadow-sm",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff", "borderRadius": "12px"}
        ),
    ], style={"padding": "20px", "backgroundColor": "#ffffff"})
    
    # Retorna o layout completo para ser usado na aplicação
    return layout
