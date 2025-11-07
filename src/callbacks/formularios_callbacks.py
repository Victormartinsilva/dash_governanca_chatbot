from dash import Input, Output
import plotly.express as px
import pandas as pd
import json
import os
from src.utils.data_loader import stream_filtered_df
from src.utils.data_processor import calculate_kpis, prepare_chart_data
from src.pages.formularios import formularios_layout
import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objects as go

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
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#e9ecef'),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef')
    )
    return fig

# REMOVIDO: Função _is_padronizado
# Agora usamos src.utils.data_processor que centraliza todo o processamento

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
        df = stream_filtered_df(CSV_PATH,
                              filters.get("ano"), 
                              filters.get("fluxo"), 
                              filters.get("servico"), 
                              filters.get("formulario"))

        if df.empty:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0", "0", empty_fig, empty_fig, None, empty_fig

        try:
            # OTIMIZAÇÃO: Calcular KPIs usando função centralizada (dados já processados)
            kpis = calculate_kpis(df)
            
            # OTIMIZAÇÃO: Preparar dados para gráficos (amostragem se necessário)
            df_charts = prepare_chart_data(df, max_rows=50000)
            
            # Criar gráficos usando dados já processados
            fig_formularios_mais_usados = _create_formularios_mais_usados_chart(df_charts)
            fig_complexidade_formularios = _create_complexidade_formularios_chart(df_charts)
            tabela_formularios_utilizados = _create_formularios_utilizados_table(df_charts)
            fig_analise_fluxo_complexidade = _create_analise_fluxo_complexidade_chart(df_charts)
            
            return str(kpis['qtd_formularios']), str(kpis['qtd_campos_distintos']), str(kpis['media_campos_formulario']), str(kpis['qtd_campos_padronizados']), fig_formularios_mais_usados, fig_complexidade_formularios, tabela_formularios_utilizados, fig_analise_fluxo_complexidade
            
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
        formularios_fluxos = formularios_fluxos.sort_values("qtd_fluxos", ascending=False).head(20)
        
        # Truncar nomes longos para melhor visualização (máximo 50 caracteres)
        MAX_LABEL_LENGTH = 50
        formularios_labels = []
        formularios_full_names = formularios_fluxos['formulario'].tolist()
        
        for name in formularios_full_names:
            if len(name) > MAX_LABEL_LENGTH:
                formularios_labels.append(name[:MAX_LABEL_LENGTH] + "...")
            else:
                formularios_labels.append(name)
        
        # Criar gradiente de cores bonito (tons de verde-azul)
        n_items = len(formularios_fluxos)
        colors = []
        base_colors = [
            (199, 233, 180),  # Verde claro
            (127, 205, 187),  # Verde-azulado
            (65, 182, 196),   # Azul claro
            (29, 145, 192),   # Azul médio
            (34, 94, 168)     # Azul escuro
        ]
        
        if n_items == 0:
            colors = []
        elif n_items == 1:
            colors = [f'rgb({base_colors[0][0]}, {base_colors[0][1]}, {base_colors[0][2]})']
        else:
            for i in range(n_items):
                color_idx = int((i / (n_items - 1)) * (len(base_colors) - 1))
                if color_idx >= len(base_colors) - 1:
                    r, g, b = base_colors[-1]
                else:
                    frac = (i / (n_items - 1)) * (len(base_colors) - 1) - color_idx
                    r1, g1, b1 = base_colors[color_idx]
                    r2, g2, b2 = base_colors[color_idx + 1]
                    r = int(r1 + (r2 - r1) * frac)
                    g = int(g1 + (g2 - g1) * frac)
                    b = int(b1 + (b2 - b1) * frac)
                colors.append(f'rgb({r}, {g}, {b})')
        
        # Criar gráfico de barras horizontais
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=formularios_fluxos['qtd_fluxos'],
            y=formularios_labels,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.9)', width=2),
                opacity=0.95
            ),
            text=[f"{val:,}".replace(",", ".") for val in formularios_fluxos['qtd_fluxos']],
            textposition='outside',
            textfont=dict(color='#2c3e50', size=12, family='Arial, sans-serif'),
            hovertemplate='<b style="font-size: 14px;">%{customdata}</b><br>' +
                         '<span style="color: #41b6c4;">Fluxos:</span> <b>%{x:,.0f}</b><extra></extra>',
            customdata=formularios_full_names,
            cliponaxis=False
        ))
        
        # Inverter ordem para mostrar maior no topo
        category_array = formularios_labels[::-1]
        
        fig.update_layout(
            template='plotly_white',
            height=450,
            plot_bgcolor='#ffffff',
            paper_bgcolor='white',
            xaxis=dict(
                title=dict(
                    text="Quantidade de Fluxos",
                    font=dict(color='#2c3e50', size=13, family='Arial, sans-serif')
                ),
                showgrid=True,
                gridcolor='rgba(230, 236, 240, 0.8)',
                gridwidth=1.5,
                tickfont=dict(color='#6c757d', size=11, family='Arial, sans-serif'),
                showline=False,
                zeroline=True,
                zerolinecolor='rgba(230, 236, 240, 0.8)',
                zerolinewidth=1.5,
                range=[0, formularios_fluxos['qtd_fluxos'].max() * 1.15]
            ),
            yaxis=dict(
                title="",
                showgrid=False,
                tickfont=dict(color='#495057', size=10, family='Arial, sans-serif'),
                showline=False,
                categoryorder='array',
                categoryarray=category_array
            ),
            showlegend=False,
            margin=dict(l=180, r=120, t=20, b=60),
            hovermode='closest',
            font=dict(family='Arial, sans-serif', color='#495057'),
            bargap=0.4
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
        comp = comp.sort_values("qtd_campos", ascending=False).head(20)
        
        # Truncar nomes longos para melhor visualização (máximo 50 caracteres)
        MAX_LABEL_LENGTH = 50
        formularios_labels = []
        formularios_full_names = comp['formulario'].tolist()
        
        for name in formularios_full_names:
            if len(name) > MAX_LABEL_LENGTH:
                formularios_labels.append(name[:MAX_LABEL_LENGTH] + "...")
            else:
                formularios_labels.append(name)
        
        # Criar gradiente de cores bonito (tons de azul corporativo)
        n_items = len(comp)
        colors = []
        base_color = (46, 134, 171)  # RGB do #2E86AB
        
        for i in range(n_items):
            intensity = 0.6 + (0.4 * (n_items - i) / n_items)
            r, g, b = [int(c * intensity) for c in base_color]
            colors.append(f'rgb({r}, {g}, {b})')
        
        # Criar gráfico de barras horizontais
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=comp['qtd_campos'],
            y=formularios_labels,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.9)', width=2),
                opacity=0.95
            ),
            text=[f"{val:,}".replace(",", ".") for val in comp['qtd_campos']],
            textposition='outside',
            textfont=dict(color='#2c3e50', size=12, family='Arial, sans-serif'),
            hovertemplate='<b style="font-size: 14px;">%{customdata}</b><br>' +
                         '<span style="color: #2E86AB;">Campos:</span> <b>%{x:,.0f}</b><extra></extra>',
            customdata=formularios_full_names,
            cliponaxis=False
        ))
        
        # Inverter ordem para mostrar maior no topo
        category_array = formularios_labels[::-1]
        
        fig.update_layout(
            template='plotly_white',
            height=450,
            plot_bgcolor='#ffffff',
            paper_bgcolor='white',
            xaxis=dict(
                title=dict(
                    text="Quantidade de Campos",
                    font=dict(color='#2c3e50', size=13, family='Arial, sans-serif')
                ),
                showgrid=True,
                gridcolor='rgba(230, 236, 240, 0.8)',
                gridwidth=1.5,
                tickfont=dict(color='#6c757d', size=11, family='Arial, sans-serif'),
                showline=False,
                zeroline=True,
                zerolinecolor='rgba(230, 236, 240, 0.8)',
                zerolinewidth=1.5,
                range=[0, comp['qtd_campos'].max() * 1.15]
            ),
            yaxis=dict(
                title="",
                showgrid=False,
                tickfont=dict(color='#495057', size=10, family='Arial, sans-serif'),
                showline=False,
                categoryorder='array',
                categoryarray=category_array
            ),
            showlegend=False,
            margin=dict(l=180, r=120, t=20, b=60),
            hovermode='closest',
            font=dict(family='Arial, sans-serif', color='#495057'),
            bargap=0.4
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
        
        # Criar tabela estilizada com estilo similar à overview
        header_style = {
            "backgroundColor": "#1e3a5f",
            "color": "white",
            "padding": "12px 16px",
            "position": "sticky",
            "top": 0,
            "zIndex": 10,
            "fontWeight": "bold",
            "fontSize": "13px",
            "textAlign": "center",
            "border": "none",
            "whiteSpace": "nowrap"
        }
        
        header_cells = [
            html.Th("Ranking", style={**header_style}),
            html.Th("Formulário", style={**header_style, "textAlign": "left"}),
            html.Th("Fluxos Usados", style=header_style),
            html.Th("Campos", style=header_style),
            html.Th("% Contribuição", style=header_style)
        ]
        
        header = html.Thead([html.Tr(header_cells)], style={"position": "sticky", "top": 0, "zIndex": 10})
        
        body_rows = []
        cell_style = {
            "padding": "12px 16px",
            "border": "1px solid #dee2e6",
            "fontSize": "13px",
            "color": "#212529",
            "whiteSpace": "nowrap",
            "overflow": "hidden",
            "textOverflow": "ellipsis"
        }
        
        for idx, row in ranking_df.head(20).iterrows():
            formulario_text = str(row['Formulário'])
            if len(formulario_text) > 60:
                formulario_text = formulario_text[:57] + "..."
            
            body_rows.append(
                html.Tr([
                    html.Td(str(int(row['Ranking'])), style={**cell_style, "textAlign": "center"}),
                    html.Td(formulario_text, style={**cell_style, "maxWidth": "400px"}),
                    html.Td(str(int(row['Fluxos Usados'])), style={**cell_style, "textAlign": "center"}),
                    html.Td(str(int(row['Campos'])), style={**cell_style, "textAlign": "center"}),
                    html.Td(row['% de contribuição'], style={**cell_style, "textAlign": "center"})
                ], style={
                    "backgroundColor": "#ffffff" if idx % 2 == 0 else "#f8f9fa",
                    "borderBottom": "1px solid #dee2e6"
                })
            )
        
        table = dbc.Table([
            header,
            html.Tbody(body_rows)
        ], bordered=False, hover=True, responsive=True, striped=False, 
        style={
            "marginBottom": 0,
            "fontSize": "13px",
            "width": "100%",
            "borderCollapse": "separate",
            "borderSpacing": 0,
            "borderRadius": "8px",
            "overflow": "hidden"
        })
        
        tabela_com_scroll = html.Div(
            table,
            style={
                "maxHeight": "600px",
                "overflowY": "auto",
                "overflowX": "auto",
                "border": "1px solid #dee2e6",
                "borderRadius": "8px",
                "display": "block",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
            }
        )
        
        return tabela_com_scroll
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
        
        # OTIMIZAÇÃO: Usar coluna is_padronizado já processada
        df_work = df.copy()
        # is_padronizado já existe no DataFrame processado
        
        # Calcular % de padronização por fluxo (baseado em campos únicos)
        percentuais_fluxos = []
        for fluxo in df_work['fluxo'].unique():
            df_fluxo = df_work[df_work['fluxo'] == fluxo]
            total_campos_unicos = df_fluxo['nomeCampo'].nunique()
            if total_campos_unicos > 0:
                campos_padronizados_unicos = df_fluxo[df_fluxo['is_padronizado'] == 1]['nomeCampo'].nunique()
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

