from dash import Input, Output, no_update
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from src.utils.data_cache import get_filtered_data, get_sampled_data_for_charts
from src.pages.fluxos import fluxos_layout
import dash_bootstrap_components as dbc
from dash import html

def register_callbacks(app):
    @app.callback(
        Output("card-servicos-fluxo", "children"),
        Output("card-fluxos-fluxo", "children"),
        Output("media-campos-fluxo", "children"),
        Output("pct-fluxo-padronizado", "children"),
        Output("percentual-padronizacao-fluxo", "figure"),
        Output("contagem-servico-por-fluxo", "figure"),
        Output("padronizacao-por-fluxo-tabela", "children"),
        Output("analise-fluxos-tree", "children"),
        Input("filtered-data-store", "data"),
        prevent_initial_call=False,
        allow_duplicate=True
    )
    def update_fluxos(filtered_data_json):
        if filtered_data_json is None:
            return "0", "0", "0", "0%", {}, {}, None, None

        # Busca dados diretamente do cache usando os filtros
        filters = filtered_data_json
        df = get_filtered_data("data/meu_arquivo.csv", 
                              filters.get("ano"), 
                              filters.get("fluxo"), 
                              filters.get("servico"), 
                              filters.get("formulario"))
        
        if df.empty:
            return "0", "0", "0", "0%", {}, {}, None, None

        try:
            qtd_servicos = df['servico'].nunique() if 'servico' in df.columns else 0
            qtd_fluxos = df['fluxo'].nunique() if 'fluxo' in df.columns else 0
            media_campos_fluxo = round(df.groupby('fluxo')['nomeCampo'].nunique().mean(), 2) if 'fluxo' in df.columns and 'nomeCampo' in df.columns else 0
            
            padrao_prefixos = ["TXT_", "CBO_", "CHK_", "RAD_", "BTN_", "TAB_", "ICO_", "IMG_", "LBL_", "DAT_", "NUM_", "TEL_", "EML_", "URL_"]
            if 'nomeCampo' in df.columns:
                df["is_padronizado"] = df["nomeCampo"].apply(
                    lambda x: any(str(x).startswith(prefix) for prefix in padrao_prefixos) 
                    if pd.notna(x) and str(x) != 'nan' else False
                )
                fluxo_padronizacao = df.groupby('fluxo').apply(lambda x: (x['is_padronizado'].sum() / len(x)) * 100 if len(x) > 0 else 0)
                pct_fluxo_padronizado = f"{fluxo_padronizacao.mean():.2f}%" if not fluxo_padronizacao.empty else "0%"
            else:
                pct_fluxo_padronizado = "0%"

            # Usa dados amostrados para gráficos para melhor performance
            df_charts = get_sampled_data_for_charts("data/meu_arquivo.csv", 
                                                   filters.get("ano"), 
                                                   filters.get("fluxo"), 
                                                   filters.get("servico"), 
                                                   filters.get("formulario"))
            
            fig_percentual_padronizacao = _create_fluxo_padronizacao_chart(df_charts)
            fig_contagem_servico_fluxo = _create_ranking_chart(df_charts)
            tabela_padronizacao = _create_padronizacao_tabela(df_charts)
            tree_analise_fluxos = _create_fluxo_tree(df_charts)
            
            return str(qtd_servicos), str(qtd_fluxos), str(media_campos_fluxo), pct_fluxo_padronizado, fig_percentual_padronizacao, fig_contagem_servico_fluxo, tabela_padronizacao, tree_analise_fluxos
            
        except Exception as e:
            print(f"Erro ao atualizar gráficos de fluxos: {e}")
            return "0", "0", "0", "0%", {}, {}, None, None

def _create_fluxo_padronizacao_chart(df):
    if 'fluxo' not in df.columns or 'is_padronizado' not in df.columns:
        return go.Figure()
    fluxo_padronizacao = df.groupby('fluxo')['is_padronizado'].value_counts(normalize=True).unstack().fillna(0)
    fluxo_padronizacao['percent_padronizado'] = fluxo_padronizacao[True] * 100
    fluxo_padronizacao = fluxo_padronizacao.sort_values('percent_padronizado', ascending=False).reset_index()
    
    fig = px.bar(fluxo_padronizacao.head(20), x='percent_padronizado', y='fluxo', orientation='h', title='Percentual Padronização Fluxo por Fluxo', template='plotly_white')
    fig.update_layout(xaxis_title='Percentual Padronizado', yaxis_title='Fluxo')
    return fig

def _create_ranking_chart(df):
    if 'fluxo' not in df.columns or 'servico' not in df.columns:
        return go.Figure()
    ranking = df.groupby('fluxo')['servico'].nunique().reset_index().sort_values('servico', ascending=False)
    ranking.columns = ['fluxo', 'contagem_servico']
    fig = px.bar(ranking.head(20), x='contagem_servico', y='fluxo', orientation='h', title='Contagem de Serviço por Fluxo', template='plotly_white')
    fig.update_layout(xaxis_title='Contagem de Serviço', yaxis_title='Fluxo')
    return fig

def _create_padronizacao_tabela(df):
    if 'fluxo' not in df.columns or 'nomeCampo' not in df.columns or 'is_padronizado' not in df.columns:
        return None
    
    padronizacao_por_fluxo = df.groupby('fluxo').agg(
        Campos=('nomeCampo', 'nunique'),
        Campos_Padronizados=('is_padronizado', lambda x: x.sum()),
    ).reset_index()
    padronizacao_por_fluxo['% Padronizacao'] = (padronizacao_por_fluxo['Campos_Padronizados'] / padronizacao_por_fluxo['Campos'] * 100).round(2)
    padronizacao_por_fluxo = padronizacao_por_fluxo.sort_values('% Padronizacao', ascending=False)
    
    return dbc.Table.from_dataframe(padronizacao_por_fluxo, striped=True, bordered=True, hover=True)

def _create_fluxo_tree(df):
    if 'fluxo' not in df.columns:
        return None
    fluxos = df['fluxo'].unique()
    tree = html.Ul([html.Li(fluxo) for fluxo in fluxos])
    return tree

