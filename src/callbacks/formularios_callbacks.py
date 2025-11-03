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
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#e9ecef'),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef')
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
            return "0", "0", "0", "0", empty_fig, empty_fig, None, empty_fig

        # Busca dados diretamente do cache usando os filtros
        filters = filtered_data_json
        df = get_filtered_data("data/meu_arquivo.csv", 
                              filters.get("ano"), 
                              filters.get("fluxo"), 
                              filters.get("servico"), 
                              filters.get("formulario"))

        if df.empty:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0", "0", empty_fig, empty_fig, None, empty_fig

        try:
            qtd_formularios = df["formulario"].nunique() if "formulario" in df.columns else 0
            qtd_campos = df["nomeCampo"].nunique() if "nomeCampo" in df.columns else 0
            media_campos_formulario = round(df.groupby("formulario")["nomeCampo"].nunique().mean(), 2) if "formulario" in df.columns and "nomeCampo" in df.columns else 0

            # Calcular quantidade total de campos padronizados (únicos)
            padrao_prefixos = ["TXT_", "CBO_", "CHK_", "RAD_", "BTN_", "TAB_", "ICO_", "IMG_", "LBL_", "DAT_", "NUM_", "TEL_", "EML_", "URL_"]
            if "nomeCampo" in df.columns:
                df["is_padronizado"] = df["nomeCampo"].apply(
                    lambda x: any(str(x).startswith(prefix) for prefix in padrao_prefixos) 
                    if pd.notna(x) and str(x) != 'nan' else False
                )
                
                # Contar campos padronizados únicos em todo o dataframe
                campos_padronizados_unicos = df[df["is_padronizado"] == True]["nomeCampo"].nunique()
                qtd_campos_padrao = str(campos_padronizados_unicos)
            else:
                qtd_campos_padrao = "0"

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
            
            return str(qtd_formularios), str(qtd_campos), str(media_campos_formulario), qtd_campos_padrao, fig_formularios_mais_usados, fig_complexidade_formularios, tabela_formularios_utilizados, fig_analise_fluxo_complexidade
            
        except Exception as e:
            print(f"Erro ao atualizar gráficos de formulários: {e}")
            import traceback
            traceback.print_exc()
            empty_fig = _create_empty_figure("Erro ao carregar dados")
            empty_div = html.Div("Erro ao carregar dados", style={"padding": "20px", "textAlign": "center", "color": "#dc3545"})
            return "0", "0", "0", "0", empty_fig, empty_fig, empty_div, empty_fig

def _create_formularios_mais_usados_chart(df):
    """Gráfico de barras horizontais - Formulários Mais Utilizados em Fluxos de Trabalho"""
    if "formulario" not in df.columns or "fluxo" not in df.columns:
        return _create_empty_figure("Dados de formulários não disponíveis")
    
    try:
        # Contar quantos fluxos únicos cada formulário é usado
        formularios_fluxos = df.groupby("formulario")["fluxo"].nunique().reset_index()
        formularios_fluxos.columns = ["formulario", "qtd_fluxos"]
        formularios_fluxos = formularios_fluxos.sort_values("qtd_fluxos", ascending=True).tail(20)
        
        # Criar gráfico de barras horizontais
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=formularios_fluxos['formulario'],
            x=formularios_fluxos['qtd_fluxos'],
            orientation='h',
            marker=dict(
                color='#495057',
                line=dict(color='#ffffff', width=1)
            ),
            text=formularios_fluxos['qtd_fluxos'],
            textposition='outside',
            textfont=dict(color='#495057', size=12)
        ))
        
        fig.update_layout(
            template='plotly_white',
            height=450,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                title="Formulários por Fluxo",
                showgrid=True,
                gridcolor='#e9ecef',
                gridwidth=1,
                tickfont=dict(color='#495057'),
                titlefont=dict(color='#495057'),
                range=[0, formularios_fluxos['qtd_fluxos'].max() * 1.15]
            ),
            yaxis=dict(
                title="Formulário",
                showgrid=False,
                tickfont=dict(color='#495057', size=10),
                titlefont=dict(color='#495057')
            ),
            showlegend=False,
            margin=dict(l=300, r=80, t=20, b=50),
            autosize=False
        )
        
        return fig
    except Exception as e:
        print(f"Erro ao criar gráfico de formulários mais usados: {e}")
        return _create_empty_figure("Erro ao processar dados")

def _create_complexidade_formularios_chart(df):
    """Gráfico de barras horizontais - Formulários que Utilizados Mais Campos"""
    if "formulario" not in df.columns or "nomeCampo" not in df.columns:
        return _create_empty_figure("Dados de formulários ou campos não disponíveis")
    
    try:
        # Contar campos únicos por formulário
        comp = df.groupby("formulario")["nomeCampo"].nunique().reset_index(name="qtd_campos")
        comp = comp.sort_values("qtd_campos", ascending=True).tail(20)
        
        # Criar gráfico de barras horizontais
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=comp['formulario'],
            x=comp['qtd_campos'],
            orientation='h',
            marker=dict(
                color='#495057',
                line=dict(color='#ffffff', width=1)
            ),
            text=comp['qtd_campos'],
            textposition='outside',
            textfont=dict(color='#495057', size=12)
        ))
        
        fig.update_layout(
            template='plotly_white',
            height=450,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                title="Qnt Campos",
                showgrid=True,
                gridcolor='#e9ecef',
                gridwidth=1,
                tickfont=dict(color='#495057'),
                titlefont=dict(color='#495057'),
                range=[0, comp['qtd_campos'].max() * 1.15]
            ),
            yaxis=dict(
                title="Formulário",
                showgrid=False,
                tickfont=dict(color='#495057', size=10),
                titlefont=dict(color='#495057')
            ),
            showlegend=False,
            margin=dict(l=300, r=80, t=20, b=50),
            autosize=False
        )
        
        return fig
    except Exception as e:
        print(f"Erro ao criar gráfico de complexidade: {e}")
        return _create_empty_figure("Erro ao processar dados")

def _create_formularios_utilizados_table(df):
    """Criar tabela de ranking de formulários por uso em fluxos x quantidade de campos"""
    if "formulario" not in df.columns or "fluxo" not in df.columns or "nomeCampo" not in df.columns:
        return html.Div("Nenhum dado disponível", style={"padding": "20px", "textAlign": "center", "color": "#6c757d"})
    
    try:
        # Contar fluxos únicos por formulário
        form_flux_counts = df.groupby("formulario")["fluxo"].nunique().reset_index(name="fluxos_usados")
        
        # Contar campos únicos por formulário
        form_campos_counts = df.groupby("formulario")["nomeCampo"].nunique().reset_index(name="campos")
        
        # Fazer merge
        ranking_df = pd.merge(form_flux_counts, form_campos_counts, on="formulario")
        
        # Calcular % de contribuição (baseado na soma de fluxos_usados * campos)
        total_contribuicao = (ranking_df["fluxos_usados"] * ranking_df["campos"]).sum()
        ranking_df["pct_contribuicao"] = ((ranking_df["fluxos_usados"] * ranking_df["campos"]) / total_contribuicao * 100).round(2)
        
        # Ordenar por contribuição (descendente)
        ranking_df = ranking_df.sort_values("pct_contribuicao", ascending=False)
        
        # Adicionar ranking
        ranking_df.insert(0, "ranking", range(1, len(ranking_df) + 1))
        
        # Renomear colunas
        ranking_df.columns = ["Ranking", "Formulário", "Fluxos Usados", "Campos", "% de contribuição"]
        
        # Formatar % de contribuição
        ranking_df["% de contribuição"] = ranking_df["% de contribuição"].apply(lambda x: f"{x:.2f}%")
        
        # Criar tabela estilizada
        table = dbc.Table.from_dataframe(
            ranking_df,
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            className="table-sm",
            style={
                "fontSize": "14px",
                "color": "#495057"
            }
        )
        
        return table
    except Exception as e:
        print(f"Erro ao criar tabela de formulários utilizados: {e}")
        import traceback
        traceback.print_exc()
        return html.Div(f"Erro ao processar dados: {str(e)}", style={"padding": "20px", "textAlign": "center", "color": "#dc3545"})

def _create_analise_fluxo_complexidade_chart(df):
    """Gráfico de scatter plot - Análise de Risco vs. Complexidade dos Fluxos"""
    if "fluxo" not in df.columns or "formulario" not in df.columns or "nomeCampo" not in df.columns:
        return _create_empty_figure("Dados não disponíveis")
    
    try:
        # Calcular complexidade: média de campos por formulário por fluxo
        fluxo_complexidade = df.groupby(["fluxo", "formulario"])["nomeCampo"].nunique().reset_index()
        fluxo_complexidade = fluxo_complexidade.groupby("fluxo")["nomeCampo"].mean().reset_index(name="media_campos_por_formulario")
        
        # Calcular quantidade total de campos por fluxo (para o eixo Y)
        fluxo_qtd_campos = df.groupby("fluxo")["nomeCampo"].nunique().reset_index(name="qtd_campos_por_fluxo")
        
        # Calcular padronização (risco): quanto menor a padronização, maior o risco
        padrao_prefixos = ["TXT_", "CBO_", "CHK_", "RAD_", "BTN_", "TAB_", "ICO_", "IMG_", "LBL_", "DAT_", "NUM_", "TEL_", "EML_", "URL_"]
        df_work = df.copy()
        df_work["is_padronizado"] = df_work["nomeCampo"].apply(
            lambda x: any(str(x).startswith(prefix) for prefix in padrao_prefixos) 
            if pd.notna(x) and str(x) != 'nan' else False
        )
        
        # Calcular % de padronização por fluxo (baseado em campos únicos)
        percentuais_fluxos = []
        for fluxo in df_work['fluxo'].unique():
            df_fluxo = df_work[df_work['fluxo'] == fluxo]
            total_campos_unicos = df_fluxo['nomeCampo'].nunique()
            if total_campos_unicos > 0:
                campos_padronizados_unicos = df_fluxo[df_fluxo['is_padronizado'] == True]['nomeCampo'].nunique()
                pct_fluxo = (campos_padronizados_unicos / total_campos_unicos) * 100
                percentuais_fluxos.append({'fluxo': fluxo, 'pct_padronizacao': pct_fluxo})
        
        fluxo_padronizacao = pd.DataFrame(percentuais_fluxos)
        
        # Contar número de formulários por fluxo (para tamanho dos pontos)
        fluxo_num_formularios = df.groupby("fluxo")["formulario"].nunique().reset_index(name="num_formularios")
        
        # Fazer merge de todos os dados
        analise_df = pd.merge(fluxo_complexidade, fluxo_qtd_campos, on="fluxo")
        analise_df = pd.merge(analise_df, fluxo_padronizacao, on="fluxo", how="left")
        analise_df = pd.merge(analise_df, fluxo_num_formularios, on="fluxo", how="left")
        analise_df["pct_padronizacao"] = analise_df["pct_padronizacao"].fillna(0)
        analise_df["num_formularios"] = analise_df["num_formularios"].fillna(1)
        
        # Categorizar risco baseado na padronização e complexidade
        # Risco inversamente proporcional à padronização e diretamente proporcional à complexidade
        def categorizar_risco(row):
            pct_pad = row["pct_padronizacao"]
            media_campos = row["media_campos_por_formulario"]
            
            # Baixa padronização (< 50%) e alta complexidade (> 50 campos) = risco alto
            # Alta padronização (> 80%) e baixa complexidade (< 30 campos) = risco muito baixo
            if pct_pad < 30 or (pct_pad < 50 and media_campos > 50):
                return "risco_alto"
            elif pct_pad < 50 or (pct_pad < 70 and media_campos > 40):
                return "risco_medio"
            elif pct_pad < 80 or media_campos > 30:
                return "risco_baixo"
            else:
                return "risco_muito_baixo"
        
        analise_df["risco"] = analise_df.apply(categorizar_risco, axis=1)
        
        # Mapear cores e nomes para categorias de risco
        cores_risco = {
            "risco_muito_baixo": "#27ae60",  # Verde mais escuro
            "risco_baixo": "#3498db",        # Azul
            "risco_medio": "#f39c12",        # Laranja
            "risco_alto": "#e74c3c"          # Vermelho
        }
        
        nomes_risco = {
            "risco_muito_baixo": "Risco Muito Baixo",
            "risco_baixo": "Risco Baixo",
            "risco_medio": "Risco Médio",
            "risco_alto": "Risco Alto"
        }
        
        # Calcular tamanho dos pontos baseado no número de formulários (normalizado)
        min_size = 8
        max_size = 20
        if analise_df["num_formularios"].max() > analise_df["num_formularios"].min():
            analise_df["tamanho_ponto"] = min_size + (analise_df["num_formularios"] - analise_df["num_formularios"].min()) / (analise_df["num_formularios"].max() - analise_df["num_formularios"].min()) * (max_size - min_size)
        else:
            analise_df["tamanho_ponto"] = (min_size + max_size) / 2
        
        # Criar gráfico de scatter plot
        fig = go.Figure()
        
        # Ordem de exibição: do menor para o maior risco (para melhor sobreposição)
        ordem_risco = ["risco_muito_baixo", "risco_baixo", "risco_medio", "risco_alto"]
        
        for risco_cat in ordem_risco:
            df_risco = analise_df[analise_df["risco"] == risco_cat]
            if not df_risco.empty:
                fig.add_trace(go.Scatter(
                    x=df_risco["media_campos_por_formulario"],
                    y=df_risco["qtd_campos_por_fluxo"],
                    mode='markers',
                    name=nomes_risco[risco_cat],
                    marker=dict(
                        size=df_risco["tamanho_ponto"],
                        color=cores_risco[risco_cat],
                        line=dict(width=1.5, color='white'),
                        opacity=0.8
                    ),
                    text=df_risco["fluxo"],
                    customdata=df_risco[["pct_padronizacao", "num_formularios"]].values,
                    hovertemplate='<b>%{text}</b><br>' +
                                  '<b>Média de Campos por Formulário:</b> %{x:.2f}<br>' +
                                  '<b>Qtd Total de Campos no Fluxo:</b> %{y}<br>' +
                                  '<b>% Padronização:</b> %{customdata[0]:.1f}%<br>' +
                                  '<b>Nº Formulários:</b> %{customdata[1]:.0f}<br>' +
                                  '<b>Categoria de Risco:</b> ' + nomes_risco[risco_cat] + '<extra></extra>'
                ))
        
        # Calcular médias para linhas de referência
        media_complexidade = analise_df["media_campos_por_formulario"].mean()
        media_campos_fluxo = analise_df["qtd_campos_por_fluxo"].mean()
        
        # Adicionar linhas de referência (médias)
        fig.add_hline(
            y=media_campos_fluxo,
            line_dash="dash",
            line_color="#95a5a6",
            opacity=0.5,
            annotation_text=f"Média: {media_campos_fluxo:.1f}",
            annotation_position="right",
            annotation_font_size=10
        )
        
        fig.add_vline(
            x=media_complexidade,
            line_dash="dash",
            line_color="#95a5a6",
            opacity=0.5,
            annotation_text=f"Média: {media_complexidade:.1f}",
            annotation_position="top",
            annotation_font_size=10
        )
        
        fig.update_layout(
            template='plotly_white',
            height=600,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                title="Média de Campos por Formulário",
                showgrid=True,
                gridcolor='#e9ecef',
                gridwidth=1,
                tickfont=dict(color='#495057', size=11),
                titlefont=dict(color='#495057', size=13)
            ),
            yaxis=dict(
                title="Quantidade Total de Campos no Fluxo",
                showgrid=True,
                gridcolor='#e9ecef',
                gridwidth=1,
                tickfont=dict(color='#495057', size=11),
                titlefont=dict(color='#495057', size=13)
            ),
            legend=dict(
                title=dict(text="Categoria de Risco", font=dict(size=12, color='#495057')),
                font=dict(color='#495057', size=11),
                x=1.02,
                y=1,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='#dee2e6',
                borderwidth=1
            ),
            margin=dict(l=100, r=200, t=60, b=80),
            hovermode='closest',
            title=dict(
                text="Análise de Risco vs. Complexidade dos Fluxos",
                font=dict(size=16, color='#212529'),
                x=0.5,
                xanchor='center',
                pad=dict(t=10, b=20)
            )
        )
        
        return fig
    except Exception as e:
        print(f"Erro ao criar gráfico de análise de risco vs complexidade: {e}")
        import traceback
        traceback.print_exc()
        return _create_empty_figure("Erro ao processar dados")

