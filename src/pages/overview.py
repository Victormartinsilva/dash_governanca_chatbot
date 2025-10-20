from dash import html, dcc
import dash_bootstrap_components as dbc

def overview_layout():
    data_store = dcc.Store(id='filtered-data-store')

    layout = html.Div([
        data_store,
        html.H4("Geral de Fluxo e Atividades", className="mt-4"),
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='card-servicos', className="text-center"), html.P("Contagem de serviço", className="text-center text-muted")])]), width=3),
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='card-fluxos', className="text-center"), html.P("Contagem de fluxo", className="text-center text-muted")])]), width=3),
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='card-formularios', className="text-center"), html.P("Contagem de formulário", className="text-center text-muted")])]), width=3),
            dbc.Col(dbc.Card([dbc.CardBody([html.H1(id='card-campos', className="text-center"), html.P("Qtd.Campos", className="text-center text-muted")])]), width=3),
        ], className="mt-3"),

        dbc.Row([
            dbc.Col(dcc.Graph(id='status-pie'), width=6),
            dbc.Col(dcc.Graph(id='top-servicos'), width=6),
        ], className="mt-4"),

        dcc.Graph(id='evolucao-mensal', className="mt-4"),

        dcc.Graph(id='complexidade-formularios', className="mt-4"),
    ])
    
    return layout

