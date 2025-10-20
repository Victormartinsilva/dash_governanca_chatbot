from dash import Input, Output, callback_context, State
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from src.utils.data_cache import get_filtered_data, get_sampled_data_for_charts
from src.pages.overview import overview_layout
from src.pages.fluxos import fluxos_layout  
from src.pages.formularios import formularios_layout  
from src.pages.campos import campos_layout


def _create_empty_figure(message):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color="gray")
    )
    fig.update_layout(
        template='plotly_white',
        height=400,
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False)
    )
    return fig

def register_callbacks(app):
    @app.callback(
        Output("page-content", "children"),
        Input("main-tabs", "active_tab")
    )
    def render_main(tab):
        if tab == "visao-geral":
            return overview_layout()
        elif tab == "fluxos-servicos":
            return fluxos_layout()
        elif tab == "formularios":
            return formularios_layout()
        elif tab == "campos":
            return campos_layout()
        else:
            return overview_layout()

    @app.callback(
        [Output("ano-dropdown", "value"),
         Output("fluxo-dropdown", "value"),
         Output("servico-dropdown", "value"),
         Output("formulario-dropdown", "value")],
        Input("limpar-filtros", "n_clicks"),
        prevent_initial_call=True
    )
    def clear_filters(n_clicks):
        if n_clicks:
            return None, None, None, None
        return None, None, None, None

    @app.callback(
        Output("filtered-data-store", "data"),
        Input("ano-dropdown", "value"),
        Input("fluxo-dropdown", "value"),
        Input("servico-dropdown", "value"),
        Input("formulario-dropdown", "value"),
        prevent_initial_call=False
    )
    def update_filtered_data_store(ano, fluxo, servico, formulario):
        # Em vez de serializar todo o DataFrame, apenas passamos os parâmetros de filtro
        # Os callbacks individuais buscarão os dados diretamente do cache
        return {
            "ano": ano,
            "fluxo": fluxo, 
            "servico": servico,
            "formulario": formulario
        }

    @app.callback(
        Output("card-fluxos", "children"),
        Output("card-servicos", "children"),
        Output("card-formularios", "children"),
        Output("card-campos", "children"),
        Output("evolucao-mensal", "figure"),
        Output("status-pie", "figure"),
        Output("top-servicos", "figure"),
        Output("complexidade-formularios", "figure"),
        Input("filtered-data-store", "data"),
        prevent_initial_call=False,
        allow_duplicate=True
    )
    def update_overview_from_store(filtered_data_json):
        if filtered_data_json is None:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0", "0", empty_fig, empty_fig, empty_fig, empty_fig

        # Busca dados diretamente do cache usando os filtros
        filters = filtered_data_json
        df = get_filtered_data("data/meu_arquivo.csv", 
                              filters.get("ano"), 
                              filters.get("fluxo"), 
                              filters.get("servico"), 
                              filters.get("formulario"))
        
        if df.empty:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0", "0", empty_fig, empty_fig, empty_fig, empty_fig
        
        try:
            qtd_fluxos = df['fluxo'].nunique() if 'fluxo' in df.columns else 0
            qtd_servicos = df['servico'].nunique() if 'servico' in df.columns else 0
            qtd_formularios = df['formulario'].nunique() if 'formulario' in df.columns else 0
            qtd_campos = df['nomeCampo'].nunique() if 'nomeCampo' in df.columns else 0

            # Usa dados amostrados para gráficos para melhor performance
            df_charts = get_sampled_data_for_charts("data/meu_arquivo.csv", 
                                                   filters.get("ano"), 
                                                   filters.get("fluxo"), 
                                                   filters.get("servico"), 
                                                   filters.get("formulario"))
            
            fig_line = _create_monthly_evolution_chart(df_charts)
            fig_pie = _create_status_distribution_chart(df_charts)
            fig_servicos = _create_top_services_chart(df_charts)
            fig_comp = _create_complexity_chart(df_charts)
            
            return (str(qtd_servicos), str(qtd_fluxos), str(qtd_formularios), 
                   str(qtd_campos), fig_line, fig_pie, fig_servicos, fig_comp)
                   
        except Exception as e:
            print(f"Erro no callback: {e}")
            empty_fig = _create_empty_figure("Erro ao carregar dados")
            return "0", "0", "0", "0", empty_fig, empty_fig, empty_fig, empty_fig


def _create_monthly_evolution_chart(df):
    if 'dataCriacao' not in df.columns or 'statusFluxo' not in df.columns:
        return _create_empty_figure("Dados de evolução não disponíveis")
    
    try:
        tmp = df.copy()
        tmp['mes'] = pd.to_datetime(tmp['dataCriacao']).dt.to_period('M').astype(str)
        grp = tmp.groupby(['mes', 'statusFluxo']).size().reset_index(name='qtd')
        
        status_map = {1: 'Ativo', 2: 'Concluído', 3: 'Cancelado', 4: 'Pendente'}
        grp['status_nome'] = grp['statusFluxo'].map(status_map).fillna('Outros')
        
        fig = px.line(
            grp, 
            x='mes', 
            y='qtd', 
            color='status_nome',
            title='Evolução Mensal de Fluxos por Status',
            template='plotly_white',
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        
        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Quantidade de Fluxos",
            legend_title="Status",
            height=400,
            showlegend=True
        )
        
        return fig
        
    except Exception as e:
        print(f"Erro ao criar gráfico de evolução: {e}")
        return _create_empty_figure("Erro ao processar dados de evolução")


def _create_status_distribution_chart(df):
    if 'statusFluxo' not in df.columns:
        return _create_empty_figure("Dados de status não disponíveis")
    
    try:
        status_counts = df['statusFluxo'].value_counts().reset_index()
        status_counts.columns = ['status', 'qtd']
        
        status_map = {1: 'Ativo', 2: 'Concluído', 3: 'Cancelado', 4: 'Pendente'}
        status_counts['status_nome'] = status_counts['status'].map(status_map).fillna('Outros')
        
        fig = px.pie(
            status_counts, 
            names='status_nome', 
            values='qtd', 
            title='Distribuição de Fluxos por Status',
            template='plotly_white',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        
        fig.update_layout(
            height=400,
            showlegend=True
        )
        
        return fig
        
    except Exception as e:
        print(f"Erro ao criar gráfico de status: {e}")
        return _create_empty_figure("Erro ao processar dados de status")


def _create_top_services_chart(df):
    if 'servico' not in df.columns:
        return _create_empty_figure("Dados de serviços não disponíveis")
    
    try:
        top_servicos = df['servico'].value_counts().head(5).reset_index()
        top_servicos.columns = ['servico', 'qtd']
        
        fig = px.bar(
            top_servicos, 
            x='qtd', 
            y='servico', 
            orientation='h',
            title='Top 5 Serviços Mais Utilizados',
            template='plotly_white',
            color='qtd',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            xaxis_title="Quantidade de Fluxos",
            yaxis_title="Serviço",
            height=300,
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        print(f"Erro ao criar gráfico de serviços: {e}")
        return _create_empty_figure("Erro ao processar dados de serviços")

def _create_complexity_chart(df):
    if 'formulario' not in df.columns or 'nomeCampo' not in df.columns:
        return _create_empty_figure("Dados de formulários ou campos não disponíveis")
    
    try:
        comp = df.groupby('formulario')['nomeCampo'].nunique().reset_index(name='qtd_campos').sort_values('qtd_campos', ascending=False)
        fig_comp = px.bar(comp.head(30), x='qtd_campos', y='formulario', orientation='h', title='Complexidade dos Formulários (por Nº de Campos)', template='plotly_white')
        fig_comp.update_layout(height=500)
        return fig_comp
    except Exception as e:
        print(f"Erro ao criar gráfico de complexidade: {e}")
        return _create_empty_figure("Erro ao processar dados de complexidade")

