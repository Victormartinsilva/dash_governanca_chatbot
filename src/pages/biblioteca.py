# Importa os componentes do Dash necessários para criar elementos HTML e gráficos interativos
from dash import html, dcc

# Importa componentes do Dash Bootstrap para facilitar o layout com cards, linhas e colunas
import dash_bootstrap_components as dbc

# Função que retorna o layout da página "Biblioteca" (Visualização Hierárquica)
def biblioteca_layout():
    # Armazena dados filtrados para compartilhamento entre callbacks do Dash
    # 'dcc.Store' é usado para guardar dados no browser sem exibir
    data_store = dcc.Store(id='filtered-data-store')

    # Define o layout principal como um container HTML com estilo
    layout = html.Div([
        # Inclui o armazenamento de dados
        data_store,

        # Título da página
        html.H4("Biblioteca - Análise de Fluxos", className="mb-4", style={"fontWeight": "bold", "color": "#212529"}),
        
        # Descrição da página
        html.P(
            "Visualização hierárquica completa da estrutura: Fluxo > Serviço > Formulário > Campos",
            className="mb-4",
            style={"color": "#6c757d", "fontSize": "16px"}
        ),

        # Seção: Diagrama Hierárquico - Estrutura de Fluxos (em tela cheia)
        dbc.Card(
            dbc.CardBody([
                html.H5("Análise de Fluxos", className="mb-3", 
                       style={"fontWeight": "600", "color": "#212529"}),
                html.P(
                    "Estrutura Hierárquica: Fluxo > Serviço > Formulário > Campos",
                    className="mb-3",
                    style={"color": "#6c757d", "fontSize": "14px"}
                ),
                dcc.Graph(
                    id='biblioteca-hierarquia-tree', 
                    style={"height": "calc(100vh - 300px)", "minHeight": "600px"},
                    config={"displayModeBar": True, "displaylogo": False}
                )
            ]),
            className="mb-4 shadow-sm",
            style={"border": "1px solid #dee2e6", "backgroundColor": "#ffffff"}
        ),
    ], style={"padding": "20px", "backgroundColor": "#ffffff"})
    
    # Retorna o layout completo para ser usado na aplicação
    return layout

