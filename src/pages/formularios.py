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
                        create_title_with_tooltip(
                            "Formulários Mais Utilizados em Fluxos de Trabalho",
                            "tooltip-formularios-mais-usados",
                            html.Div([
                                html.Strong("Nome: ", style={"color": "#ffffff"}),
                                html.Span("Formulários Mais Utilizados em Fluxos de Trabalho", style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Conceito: ", style={"color": "#ffffff"}),
                                html.Span("Quantidade de fluxos distintos em que cada formulário é utilizado, ordenados do maior para o menor.", 
                                         style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Método de cálculo: ", style={"color": "#ffffff"}),
                                html.Span("Agrupamento por formulário e contagem de fluxos únicos onde é utilizado.", 
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
                            id='formularios-mais-usados',
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
            
            # Gráfico de barras horizontais - Formulários que Utilizados Mais Campos (direita)
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        create_title_with_tooltip(
                            "Formulários que Utilizados Mais Campos",
                            "tooltip-complexidade-formularios",
                            html.Div([
                                html.Strong("Nome: ", style={"color": "#ffffff"}),
                                html.Span("Formulários que Utilizados Mais Campos", style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Conceito: ", style={"color": "#ffffff"}),
                                html.Span("Quantidade de campos distintos por formulário, ordenados do maior para o menor.", 
                                         style={"color": "#e9ecef"}),
                                html.Br(),
                                html.Br(),
                                html.Strong("Método de cálculo: ", style={"color": "#ffffff"}),
                                html.Span("Agrupamento por formulário e contagem de campos únicos.", 
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
                            id='complexidade-formularios-form',
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
            ], width=6, style={"paddingLeft": "5px", "paddingRight": "10px"}),
        ], className="mb-4"),

        # Terceira seção: Tabela - Ranking Formulários por uso Fluxos x Qnt. Campos
        dbc.Card(
            dbc.CardBody([
                create_title_with_tooltip(
                    "Ranking Formulários por uso Fluxos x Qnt. Campos",
                    "tooltip-ranking-formularios",
                    html.Div([
                        html.Strong("Nome: ", style={"color": "#ffffff"}),
                        html.Span("Ranking Formulários por uso Fluxos x Qnt. Campos", style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Conceito: ", style={"color": "#ffffff"}),
                        html.Span("Ranking de formulários ordenado por contribuição relativa (fluxos usados × quantidade de campos).", 
                                 style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Método de cálculo: ", style={"color": "#ffffff"}),
                        html.Span("Produto entre fluxos únicos e campos únicos por formulário, normalizado em percentual de contribuição.", 
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
                    id='formularios-utilizados-table',
                    style={"width": "100%", "overflow": "auto"}
                )
            ]),
            className="mb-4 shadow-lg",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff", "borderRadius": "12px"}
        ),

        # Quarta seção: Análise de Risco vs. Complexidade dos Fluxos
        dbc.Card(
            dbc.CardBody([
                create_title_with_tooltip(
                    "Análise de Risco vs. Complexidade dos Fluxos",
                    "tooltip-analise-risco",
                    html.Div([
                        html.Strong("Nome: ", style={"color": "#ffffff"}),
                        html.Span("Análise de Risco vs. Complexidade dos Fluxos", style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Conceito: ", style={"color": "#ffffff"}),
                        html.Span("Análise visual da relação entre complexidade (campos) e risco (baseado em padronização) dos fluxos.", 
                                 style={"color": "#e9ecef"}),
                        html.Br(),
                        html.Br(),
                        html.Strong("Método de cálculo: ", style={"color": "#ffffff"}),
                        html.Span("Categorização de risco baseada em percentual de padronização e média de campos por formulário. Tamanho dos pontos representa número de formulários.", 
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
                    id='analise-fluxo-complexidade',
                    style={"height": "600px"},
                    config={"displayModeBar": False}
                )
            ]),
            className="mb-4 shadow-lg",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff", "borderRadius": "12px"}
        ),
    ], style={"padding": "20px", "backgroundColor": "#ffffff"})
    
    # Retorna o layout completo para ser usado na aplicação
    return layout
