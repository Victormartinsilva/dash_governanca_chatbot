from dash import Input, Output
import plotly.express as px
import pandas as pd
import json
from src.utils.data_cache import get_filtered_data, get_sampled_data_for_charts
from src.pages.campos import campos_layout
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
        Output("card-campos-distintos", "children"),
        Output("card-campos-padronizados", "children"),
        Output("pct-campos-padrao", "children"),
        Output("campos-mais-usados", "figure"),
        Output("campos-com-variacoes", "figure"),
        Output("tabela-autoria-dados", "children"),
        Output("diversidade-campos-tipo", "figure"),
        Input("filtered-data-store", "data"),
        prevent_initial_call=False,
        allow_duplicate=True
    )
    def update_campos(filtered_data_json):
        if filtered_data_json is None:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0%", empty_fig, empty_fig, None, empty_fig

        # Busca dados diretamente do cache usando os filtros
        filters = filtered_data_json
        df = get_filtered_data("data/meu_arquivo.csv", 
                              filters.get("ano"), 
                              filters.get("fluxo"), 
                              filters.get("servico"), 
                              filters.get("formulario"))

        if df.empty:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0%", empty_fig, empty_fig, None, empty_fig

        try:
            padrao_prefixos = ["TXT_", "CBO_", "CHK_", "RAD_", "BTN_", "TAB_", "ICO_", "IMG_", "LBL_", "DAT_", "NUM_", "TEL_", "EML_", "URL_"]
            
            if 'nomeCampo' in df.columns:
                df["is_padronizado"] = df["nomeCampo"].apply(
                    lambda x: any(str(x).startswith(prefix) for prefix in padrao_prefixos) 
                    if pd.notna(x) and str(x) != 'nan' else False
                )
                qtd_campos_distintos = df["nomeCampo"].nunique()
                qtd_campos_padronizados = df[df["is_padronizado"]]["nomeCampo"].nunique()
                pct_campos_padrao = f"{((qtd_campos_padronizados / qtd_campos_distintos) * 100):.2f}%" if qtd_campos_distintos > 0 else "0%"
            else:
                qtd_campos_distintos = 0
                qtd_campos_padronizados = 0
                pct_campos_padrao = "0%"

            # Usa dados amostrados para gráficos para melhor performance
            df_charts = get_sampled_data_for_charts("data/meu_arquivo.csv", 
                                                   filters.get("ano"), 
                                                   filters.get("fluxo"), 
                                                   filters.get("servico"), 
                                                   filters.get("formulario"))
            
            fig_top = _create_campos_mais_usados_chart(df_charts)
            fig_var = _create_campos_com_variacoes_chart(df_charts)
            fig_diversidade = _create_diversidade_campos_tipo_chart(df_charts)

            tabela_autoria = _create_tabela_autoria_dados(df_charts)

            return str(qtd_campos_distintos), str(qtd_campos_padronizados), pct_campos_padrao, fig_top, fig_var, tabela_autoria, fig_diversidade
                   
        except Exception as e:
            print(f"Erro no callback: {e}")
            empty_fig = _create_empty_figure("Erro ao carregar dados")
            return "0", "0", "0%", empty_fig, empty_fig, None, empty_fig

def _create_campos_mais_usados_chart(df):
    if 'nomeCampo' not in df.columns:
        return _create_empty_figure("Dados de campos não disponíveis")
    top = df['nomeCampo'].value_counts().reset_index()
    top.columns = ['nomeCampo','qtd']
    fig = px.bar(top.head(30), x='qtd', y='nomeCampo', orientation='h', title='Campos Mais Utilizados (Geral)', template='plotly_white')
    fig.update_layout(height=500)
    return fig

def _create_campos_com_variacoes_chart(df):
    if 'nomeCampo' not in df.columns or 'legendaCampoFilho' not in df.columns:
        return _create_empty_figure("Dados de variação de campos não disponíveis")
    var = df.groupby('nomeCampo')['legendaCampoFilho'].nunique().reset_index(name='variacoes').sort_values('variacoes', ascending=False)
    fig = px.bar(var.head(30), x='variacoes', y='nomeCampo', orientation='h', title='Campos com Mais Variação de Legenda', template='plotly_white')
    fig.update_layout(height=500)
    return fig

def _create_tabela_autoria_dados(df):
    if 'autor' not in df.columns or 'nomeCampo' not in df.columns:
        return dbc.Table.from_dataframe(pd.DataFrame({'Autor': ["N/A"], 'Campos Criados': [0]}), striped=True, bordered=True, hover=True)
    
    autoria_data = df.groupby('autor')['nomeCampo'].nunique().reset_index(name='Campos Criados')
    autoria_data.columns = ['Autor', 'Campos Criados']
    return dbc.Table.from_dataframe(autoria_data.head(10), striped=True, bordered=True, hover=True)

def _create_diversidade_campos_tipo_chart(df):
    if 'tipoCampo' not in df.columns:
        return _create_empty_figure("Dados de tipo de campo não disponíveis")
    
    tipo_componente_map = {
        "TXT_": "Caixa de Texto",
        "CBO_": "Combobox",
        "CHK_": "Checkbox",
        "RAD_": "Radio Button",
        "BTN_": "Botão",
        "TAB_": "Tabela",
        "ICO_": "Ícone",
        "IMG_": "Imagem",
        "LBL_": "Label",
        "DAT_": "Data",
        "NUM_": "Número",
        "TEL_": "Telefone",
        "EML_": "Email",
        "URL_": "URL"
    }

    df["tipo_componente"] = df["nomeCampo"].apply(
        lambda x: next((v for k, v in tipo_componente_map.items() if str(x).startswith(k)), "Outros/Sem Padrão") 
        if pd.notna(x) and str(x) != 'nan' else "Outros/Sem Padrão"
    )
    
    diversidade = df['tipo_componente'].value_counts().reset_index()
    diversidade.columns = ['Tipo de Componente', 'Quantidade']
    
    fig = px.bar(diversidade, x='Tipo de Componente', y='Quantidade', title='Diversidade de Campos por Tipo de Componente', template='plotly_white')
    fig.update_layout(height=500)
    return fig

