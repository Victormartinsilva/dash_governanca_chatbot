from dash import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os
from src.utils.data_loader import stream_filtered_df
from src.utils.data_processor import prepare_chart_data
from src.pages.biblioteca import biblioteca_layout

# Caminho do arquivo CSV
CSV_PATH = "data/meu_arquivo.csv"

def _create_empty_figure(message):
    """Cria uma figura vazia com mensagem"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color="gray")
    )
    fig.update_layout(
        template='plotly_white',
        height=600,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#e9ecef'),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef')
    )
    return fig

def _create_fluxos_hierarquia_tree(df):
    """Cria diagrama hierárquico (treemap) mostrando Fluxo -> Serviço -> Formulário -> Campos"""
    if df.empty or 'fluxo' not in df.columns or 'servico' not in df.columns or 'formulario' not in df.columns or 'nomeCampo' not in df.columns:
        return _create_empty_figure("Dados não disponíveis")
    
    try:
        # Preparar dados hierárquicos
        # Agrupar por fluxo, serviço, formulário e campo, contando ocorrências
        df_hierarquia = df.groupby(['fluxo', 'servico', 'formulario', 'nomeCampo']).size().reset_index(name='Qtd')
        
        # Renomear colunas para o formato esperado pelo treemap
        df_hierarquia = df_hierarquia.rename(columns={
            'fluxo': 'Fluxo',
            'servico': 'Serviço',
            'formulario': 'Formulário',
            'nomeCampo': 'Campo'
        })
        
        # Limitar a quantidade de dados se houver muitos (para performance)
        if len(df_hierarquia) > 10000:
            # Amostrar mantendo representatividade por fluxo
            df_hierarquia = df_hierarquia.groupby('Fluxo').apply(
                lambda x: x.sample(min(500, len(x)), random_state=42)
            ).reset_index(drop=True)
        
        # Criar o treemap
        fig = px.treemap(
            df_hierarquia,
            path=["Fluxo", "Serviço", "Formulário", "Campo"],
            values="Qtd",
            color="Fluxo",
            color_discrete_sequence=px.colors.qualitative.Set2,
            title="Estrutura Hierárquica - Fluxo > Serviço > Formulário > Campos"
        )
        
        # Atualizar estilo
        fig.update_traces(root_color="lightgray")
        fig.update_layout(
            template='plotly_white',
            height=600,
            margin=dict(t=50, l=10, r=10, b=10),
            plot_bgcolor='white',
            paper_bgcolor='white',
            title=dict(
                text="Estrutura Hierárquica - Fluxo > Serviço > Formulário > Campos",
                font=dict(size=16, color="#212529"),
                x=0.5,
                xanchor='center'
            ),
            font=dict(color='#495057')
        )
        
        return fig
        
    except Exception as e:
        print(f"Erro ao criar diagrama hierárquico: {e}")
        import traceback
        traceback.print_exc()
        return _create_empty_figure("Erro ao processar dados")

def register_callbacks(app):
    @app.callback(
        Output("biblioteca-hierarquia-tree", "figure"),
        Input("filtered-data-store", "data"),
        prevent_initial_call=False,
        allow_duplicate=True
    )
    def update_biblioteca_hierarquia(filtered_data_json):
        if filtered_data_json is None:
            return _create_empty_figure("Nenhum dado disponível")

        # Busca dados diretamente do cache usando os filtros
        filters = filtered_data_json
        df = stream_filtered_df(CSV_PATH,
                              filters.get("ano"), 
                              filters.get("fluxo"), 
                              filters.get("servico"), 
                              filters.get("formulario"))
        
        if df.empty:
            return _create_empty_figure("Nenhum dado disponível")

        try:
            # OTIMIZAÇÃO: Preparar dados para gráficos (amostragem se necessário)
            # Para biblioteca, podemos aumentar o limite já que é a única visualização
            df_charts = prepare_chart_data(df, max_rows=100000)
            
            # Criar gráfico hierárquico
            fig_hierarquia = _create_fluxos_hierarquia_tree(df_charts)
            
            return fig_hierarquia
            
        except Exception as e:
            print(f"Erro ao atualizar gráfico de biblioteca: {e}")
            import traceback
            traceback.print_exc()
            return _create_empty_figure("Erro ao carregar dados")

