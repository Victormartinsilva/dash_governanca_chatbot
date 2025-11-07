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

# Função que retorna o layout da página "Fluxos/Serviços" (Análise de Fluxos)
def fluxos_layout():
    # Armazena dados filtrados para compartilhamento entre callbacks do Dash
    # 'dcc.Store' é usado para guardar dados no browser sem exibir
    data_store = dcc.Store(id='filtered-data-store')

    # Define o layout principal como um container HTML com estilo
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
                create_title_with_tooltip(
                    "Percentual de Padronização por Fluxo",
                    "tooltip-padronizacao-fluxo",
                    html.Div([
                        html.Strong("Nome: ", style={"color": "#ffffff"}),
                        html.Span("Percentual de Padronização por Fluxo", style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Conceito: ", style={"color": "#ffffff"}),
                        html.Span("Percentual de campos padronizados por fluxo no período de referência.", 
                                 style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Método de cálculo: ", style={"color": "#ffffff"}),
                        html.Span("Razão entre campos padronizados e total de campos por fluxo, multiplicado por 100.", 
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
                dcc.Graph(id='percentual-padronizacao-fluxo', style={"height": "450px"},
                         config={"displayModeBar": False})
            ]),
            className="mb-4 shadow-lg",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff", "borderRadius": "12px"}
        ),

        # Terceira seção: Dois gráficos lado a lado
        dbc.Row([
            # Gráfico de barras horizontais - Análise de Fluxos por Serviços (esquerda)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        create_title_with_tooltip(
                            "Análise de Fluxos por Serviços",
                            "tooltip-fluxos-servicos",
                            html.Div([
                                html.Strong("Nome: ", style={"color": "#ffffff"}),
                                html.Span("Análise de Fluxos por Serviços", style={"color": "#e9ecef"}),
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
                        html.Div(
                            dcc.Graph(
                                id='contagem-servico-por-fluxo',
                                style={"height": "820px"},
                                config={"displayModeBar": False}
                            ),
                            style={"height": "820px", "overflow": "hidden", "width": "100%"}
                        )
                    ]),
                    className="mb-4 shadow-lg",
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
                        create_title_with_tooltip(
                            "Padronização por Fluxo",
                            "tooltip-tabela-padronizacao",
                            html.Div([
                                html.Strong("Nome: ", style={"color": "#ffffff"}),
                                html.Span("Padronização por Fluxo", style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Conceito: ", style={"color": "#ffffff"}),
                                html.Span("Tabela detalhada apresentando a relação entre fluxos, campos do formulário e campos padronizados.", 
                                         style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Método de cálculo: ", style={"color": "#ffffff"}),
                                html.Span("Agrupamento por fluxo, contagem de campos únicos e cálculo do percentual de padronização.", 
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
                        html.Div(
                            id='padronizacao-por-fluxo-tabela',
                            style={"width": "100%", "overflow": "hidden"}
                        )
                    ]),
                    className="mb-4 shadow-lg",
                    style={
                        "border": "1px solid #dee2e6",
                        "backgroundColor": "#ffffff",
                        "borderRadius": "12px",
                        "height": "100%"
                    }
                )
            ], width=6, style={"paddingLeft": "5px", "paddingRight": "10px"}),
        ], className="mb-4"),
    ], style={"padding": "20px", "backgroundColor": "#ffffff"})
    
    # Retorna o layout completo para ser usado na aplicação
    return layout
