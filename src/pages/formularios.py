from dash import html, dcc
import dash_bootstrap_components as dbc

def formularios_layout():
    data_store = dcc.Store(id='filtered-data-store')

    layout = html.Div([
        data_store,
        html.H4("Análise de Formulários", className="mt-4"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='card-formularios-form', className="text-center"), html.P("Contagem de formulário", className="text-center text-muted")])]), width=3),
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='card-campos-form', className="text-center"), html.P("Qtd.Campos", className="text-center text-muted")])]), width=3),
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='media-campos-formulario', className="text-center"), html.P("Média Campos por Formulário", className="text-center text-muted")])]), width=3),
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='pct-formularios-padrao', className="text-center"), html.P("% Formulário Padrão", className="text-center text-muted")])]), width=3),
        ], className="mt-3"),

        dbc.Row([
            dbc.Col(dcc.Graph(id='formularios-mais-usados'), width=6),
            dbc.Col(dcc.Graph(id='complexidade-formularios-form'), width=6),
        ], className="mt-4"),

        html.H4("Formulários Mais Utilizados", className="mt-4"),
        html.Div(id='formularios-utilizados-table'),

        html.H4("Análise de Fluxo vs. Complexidade dos Fluxos", className="mt-4"),
        dcc.Graph(id='analise-fluxo-complexidade')
    ])
    return layout
