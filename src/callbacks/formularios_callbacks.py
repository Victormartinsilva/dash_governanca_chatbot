from dash import Input, Output
import plotly.express as px
import pandas as pd
import json
from src.utils.data_cache import get_filtered_data, get_sampled_data_for_charts
from src.pages.formularios import formularios_layout
import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objects as go

def _create_empty_figure(message):
    """Cria uma figura vazia com mensagem."""
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
        Output("card-formularios-form", "children"),
        Output("card-campos-form", "children"),
        Output("media-campos-formulario", "children"),
        Output("pct-formularios-padrao", "children"),
        Output("formularios-mais-usados", "figure"),
        Output("complexidade-formularios-form", "figure"),
        Output("formularios-utilizados-table", "children"),
        Output("analise-fluxo-complexidade", "figure"),
        Input("filtered-data-store", "data"),
        prevent_initial_call=False,
        allow_duplicate=True
    )
    def update_formularios(filtered_data_json):
        if filtered_data_json is None:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0", "0%", empty_fig, empty_fig, None, empty_fig

        # Busca dados diretamente do cache usando os filtros
        filters = filtered_data_json
        df = get_filtered_data("data/meu_arquivo.csv", 
                              filters.get("ano"), 
                              filters.get("fluxo"), 
                              filters.get("servico"), 
                              filters.get("formulario"))

        if df.empty:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0", "0%", empty_fig, empty_fig, None, empty_fig

        try:
            qtd_formularios = df["formulario"].nunique() if "formulario" in df.columns else 0
            qtd_campos = df["nomeCampo"].nunique() if "nomeCampo" in df.columns else 0
            media_campos_formulario = round(df.groupby("formulario")["nomeCampo"].nunique().mean(), 2) if "formulario" in df.columns and "nomeCampo" in df.columns else 0

            padrao_prefixos = ["TXT_", "CBO_", "CHK_", "RAD_", "BTN_", "TAB_", "ICO_", "IMG_", "LBL_", "DAT_", "NUM_", "TEL_", "EML_", "URL_"]
            if "nomeCampo" in df.columns:
                df["is_padronizado"] = df["nomeCampo"].apply(
                    lambda x: any(str(x).startswith(prefix) for prefix in padrao_prefixos) 
                    if pd.notna(x) and str(x) != 'nan' else False
                )
                form_padronizacao = df.groupby("formulario").apply(lambda x: (x["is_padronizado"].sum() / len(x)) * 100 if len(x) > 0 else 0)
                pct_formularios_padrao = f"{form_padronizacao.mean():.2f}%" if not form_padronizacao.empty else "0%"
            else:
                pct_formularios_padrao = "0%"

            # Usa dados completos para estatísticas dos cards
            # Usa dados amostrados para gráficos para melhor performance
            df_charts = get_sampled_data_for_charts("data/meu_arquivo.csv", 
                                                   filters.get("ano"), 
                                                   filters.get("fluxo"), 
                                                   filters.get("servico"), 
                                                   filters.get("formulario"))
            
            fig_formularios_mais_usados = _create_formularios_mais_usados_chart(df_charts)
            fig_complexidade_formularios = _create_complexidade_formularios_chart(df_charts)
            tabela_formularios_utilizados = _create_formularios_utilizados_table(df_charts)
            fig_analise_fluxo_complexidade = _create_analise_fluxo_complexidade_chart(df_charts)
            
            return str(qtd_formularios), str(qtd_campos), str(media_campos_formulario), pct_formularios_padrao, fig_formularios_mais_usados, fig_complexidade_formularios, tabela_formularios_utilizados, fig_analise_fluxo_complexidade
            
        except Exception as e:
            print(f"Erro ao atualizar gráficos de formulários: {e}")
            return "0", "0", "0", "0%", empty_fig, empty_fig, None, empty_fig

def _create_formularios_mais_usados_chart(df):
    if "formulario" not in df.columns:
        return _create_empty_figure("Dados de formulários não disponíveis")
    used = df["formulario"].value_counts().reset_index()
    used.columns = ["formulario","qtd"]
    fig = px.bar(used.head(20).sort_values("qtd"), x="qtd", y="formulario", orientation="h", title="Formulários Mais Utilizados", template="plotly_white")
    fig.update_layout(height=500)
    return fig

def _create_complexidade_formularios_chart(df):
    if "formulario" not in df.columns or "nomeCampo" not in df.columns:
        return _create_empty_figure("Dados de formulários ou campos não disponíveis")
    comp = df.groupby("formulario")["nomeCampo"].nunique().reset_index(name="qtd_campos").sort_values("qtd_campos", ascending=False)
    fig = px.bar(comp.head(30), x="qtd_campos", y="formulario", orientation="h", title="Complexidade dos Formulários (por Nº de Campos)", template="plotly_white")
    fig.update_layout(height=500)
    return fig

def _create_formularios_utilizados_table(df):
    if "formulario" not in df.columns or "fluxo" not in df.columns:
        return None
    
    form_flux_counts = df.groupby(["formulario", "fluxo"]).size().reset_index(name="qtd")
    form_flux_counts_pivot = form_flux_counts.pivot_table(index="formulario", columns="fluxo", values="qtd", fill_value=0)
    
    return dbc.Table.from_dataframe(form_flux_counts_pivot.reset_index(), striped=True, bordered=True, hover=True)

def _create_analise_fluxo_complexidade_chart(df):
    if "fluxo" not in df.columns or "formulario" not in df.columns or "nomeCampo" not in df.columns:
        return go.Figure()
    
    fluxo_complexidade = df.groupby(["fluxo", "formulario"])["nomeCampo"].nunique().reset_index()
    fluxo_complexidade = fluxo_complexidade.groupby("fluxo")["nomeCampo"].mean().reset_index(name="media_campos_por_formulario")

    padrao_prefixos = ["TXT_", "CBO_", "CHK_", "RAD_", "BTN_", "TAB_", "ICO_", "IMG_", "LBL_", "DAT_", "NUM_", "TEL_", "EML_", "URL_"]
    df["is_padronizado"] = df["nomeCampo"].apply(
        lambda x: any(str(x).startswith(prefix) for prefix in padrao_prefixos) 
        if pd.notna(x) and str(x) != 'nan' else False
    )
    fluxo_padronizacao = df.groupby("fluxo").apply(lambda x: (x["is_padronizado"].sum() / len(x)) * 100 if len(x) > 0 else 0).reset_index(name="pct_padronizacao")

    analise_df = pd.merge(fluxo_complexidade, fluxo_padronizacao, on="fluxo")

    fig = px.scatter(analise_df, 
                     x="media_campos_por_formulario", 
                     y="pct_padronizacao", 
                     text="fluxo", 
                     title="Análise de Fluxo vs. Complexidade e Padronização", 
                     template="plotly_white")
    fig.update_traces(textposition="top center")
    fig.update_layout(height=600)
    return fig

