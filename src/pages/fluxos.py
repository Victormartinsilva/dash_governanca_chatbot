from dash import html, dcc
import dash_bootstrap_components as dbc

def fluxos_layout():
    data_store = dcc.Store(id='filtered-data-store')

    layout = html.Div([
        data_store,
        html.H4("Análise de Fluxos e Serviços", className="mt-4"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='card-servicos-fluxo', className="text-center"), html.P("Contagem de serviço", className="text-center text-muted")])]), width=3),
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='card-fluxos-fluxo', className="text-center"), html.P("Contagem de fluxo", className="text-center text-muted")])]), width=3),
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='media-campos-fluxo', className="text-center"), html.P("Media Campos por Fluxo", className="text-center text-muted")])]), width=3),
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='pct-fluxo-padronizado', className="text-center"), html.P("% Fluxo Padronizado", className="text-center text-muted")])]), width=3),
        ], className="mt-3"),

        dcc.Graph(id='percentual-padronizacao-fluxo', className="mt-4"),

        html.H4("Análise de Fluxos por Serviços", className="mt-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(id='contagem-servico-por-fluxo'), width=6),
            dbc.Col(html.Div(id='padronizacao-por-fluxo-tabela'), width=6),
        ], className="mt-3"),

        html.H4("Análise de Fluxos", className="mt-4"),
        html.Div(id='analise-fluxos-tree')
    ])
    return layout
