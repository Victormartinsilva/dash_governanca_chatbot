from dash import html, dcc
import dash_bootstrap_components as dbc

def campos_layout():
    data_store = dcc.Store(id='filtered-data-store')

    layout = html.Div([
        data_store,
        html.H4("Ranking de Utilização de Campos (Geral)", className="mt-4"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='card-campos-distintos', className="text-center"), html.P("Qtd Campos Distintos", className="text-center text-muted")])]), width=4),
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='card-campos-padronizados', className="text-center"), html.P("Qtd Campos Padronizados Total", className="text-center text-muted")])]), width=4),
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='pct-campos-padrao', className="text-center"), html.P("% Campos Padronizados", className="text-center text-muted")])]), width=4),
        ], className="mt-3"),

        dcc.Graph(id='campos-mais-usados', className="mt-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(id='campos-com-variacoes'), width=6),
            dbc.Col(html.Div(id='tabela-autoria-dados'), width=6),
        ], className="mt-4"),

        dcc.Graph(id='diversidade-campos-tipo', className="mt-4"),
    ])
    return layout
