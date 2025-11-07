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
                create_title_with_tooltip(
                    "Campos Mais Usados",
                    "tooltip-campos-mais-usados",
                    html.Div([
                        html.Strong("Nome: ", style={"color": "#ffffff"}),
                        html.Span("Campos Mais Usados", style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Conceito: ", style={"color": "#ffffff"}),
                        html.Span("Quantidade total de ocorrências de cada campo no período de referência, ordenados do maior para o menor.", 
                                 style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Método de cálculo: ", style={"color": "#ffffff"}),
                        html.Span("Contagem de ocorrências únicas de cada campo.", 
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
                dcc.Graph(id='campos-mais-usados', style={"height": "450px"},
                         config={"displayModeBar": False})
            ]),
            className="mb-4 shadow-lg",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff", "borderRadius": "12px"}
        ),

        # Terceira seção: Dois gráficos lado a lado
        dbc.Row([
            # Gráfico - Campos com Variações (esquerda)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        create_title_with_tooltip(
                            "Campos com Variações",
                            "tooltip-campos-variacoes",
                            html.Div([
                                html.Strong("Nome: ", style={"color": "#ffffff"}),
                                html.Span("Campos com Variações", style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Conceito: ", style={"color": "#ffffff"}),
                                html.Span("Quantidade de variações de legenda para cada campo, ordenados do maior para o menor.", 
                                         style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Método de cálculo: ", style={"color": "#ffffff"}),
                                html.Span("Agrupamento por campo e contagem de legendas distintas (variações).", 
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
                            id='campos-com-variacoes',
                            style={"height": "450px"},
                            config={"displayModeBar": False}
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
            
            # Tabela - Autoria de Dados (direita)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        create_title_with_tooltip(
                            "Autoria de Dados",
                            "tooltip-autoria-dados",
                            html.Div([
                                html.Strong("Nome: ", style={"color": "#ffffff"}),
                                html.Span("Autoria de Dados", style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Conceito: ", style={"color": "#ffffff"}),
                                html.Span("Quantidade de campos distintos criados por cada autor no período de referência.", 
                                         style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Método de cálculo: ", style={"color": "#ffffff"}),
                                html.Span("Agrupamento por autor e contagem de campos únicos criados.", 
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
                            id='tabela-autoria-dados',
                            style={"width": "100%", "overflow": "auto"}
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

        # Quarta seção: Gráfico - Diversidade de Campos por Tipo
        dbc.Card(
            dbc.CardBody([
                create_title_with_tooltip(
                    "Diversidade de Campos por Tipo",
                    "tooltip-diversidade-tipo",
                    html.Div([
                        html.Strong("Nome: ", style={"color": "#ffffff"}),
                        html.Span("Diversidade de Campos por Tipo", style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Conceito: ", style={"color": "#ffffff"}),
                        html.Span("Quantidade de campos por tipo de componente no período de referência.", 
                                 style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Método de cálculo: ", style={"color": "#ffffff"}),
                        html.Span("Agrupamento por tipo de componente e contagem de ocorrências.", 
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
                dcc.Graph(id='diversidade-campos-tipo', style={"height": "450px"},
                         config={"displayModeBar": False})
            ]),
            className="mb-4 shadow-lg",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff", "borderRadius": "12px"}
        ),
    ], style={"padding": "20px", "backgroundColor": "#ffffff"})
    
    # Retorna o layout completo para ser usado na aplicação
    return layout
