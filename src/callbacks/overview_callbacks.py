from dash import Input, Output, callback_context, State
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import dash_bootstrap_components as dbc
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
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#e9ecef'),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef')
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
        Output("card-etapas", "children"),
        Output("fluxo-por-mes", "figure"),
        Output("formulario-por-servico", "figure"),
        Output("servico-por-fluxo", "figure"),
        Output("tabela-detalhada", "children"),
        Input("filtered-data-store", "data"),
        prevent_initial_call=False,
        allow_duplicate=True
    )
    def update_overview_from_store(filtered_data_json):
        if filtered_data_json is None:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0", "0", empty_fig, empty_fig, empty_fig, html.Div("Nenhum dado disponível")

        # Busca dados diretamente do cache usando os filtros
        filters = filtered_data_json
        df = get_filtered_data("data/meu_arquivo.csv", 
                              filters.get("ano"), 
                              filters.get("fluxo"), 
                              filters.get("servico"), 
                              filters.get("formulario"))
        
        if df.empty:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0", "0", empty_fig, empty_fig, empty_fig, html.Div("Nenhum dado disponível")
        
        try:
            # Calcular KPIs
            qtd_fluxos = df['fluxo'].nunique() if 'fluxo' in df.columns else 0
            qtd_servicos = df['servico'].nunique() if 'servico' in df.columns else 0
            qtd_formularios = df['formulario'].nunique() if 'formulario' in df.columns else 0
            qtd_etapas = df['etapa'].nunique() if 'etapa' in df.columns else 0

            # Usa dados amostrados para gráficos para melhor performance
            df_charts = get_sampled_data_for_charts("data/meu_arquivo.csv", 
                                                   filters.get("ano"), 
                                                   filters.get("fluxo"), 
                                                   filters.get("servico"), 
                                                   filters.get("formulario"))
            
            # Criar gráficos
            fig_fluxo_mes = _create_fluxo_por_mes_chart(df_charts)
            fig_formulario_servico = _create_formulario_por_servico_chart(df_charts)
            fig_servico_fluxo = _create_servico_por_fluxo_chart(df_charts)
            
            # Criar tabela detalhada
            tabela = _create_detailed_table(df_charts)
            
            return (str(qtd_fluxos), str(qtd_servicos), str(qtd_formularios), 
                   str(qtd_etapas), fig_fluxo_mes, fig_formulario_servico, 
                   fig_servico_fluxo, tabela)
                   
        except Exception as e:
            print(f"Erro no callback: {e}")
            import traceback
            traceback.print_exc()
            empty_fig = _create_empty_figure("Erro ao carregar dados")
            return "0", "0", "0", "0", empty_fig, empty_fig, empty_fig, html.Div(f"Erro: {str(e)}")


def _create_fluxo_por_mes_chart(df):
    """Gráfico de linha - Contagem de fluxo por Mês"""
    if 'dataCriacao' not in df.columns or 'fluxo' not in df.columns:
        return _create_empty_figure("Dados não disponíveis")
    
    try:
        df_copy = df.copy()
        df_copy['dataCriacao'] = pd.to_datetime(df_copy['dataCriacao'], errors='coerce')
        df_copy = df_copy.dropna(subset=['dataCriacao'])
        
        # Extrair mês e ano
        df_copy['mes'] = df_copy['dataCriacao'].dt.strftime('%Y-%m')
        df_copy['mes_nome'] = df_copy['dataCriacao'].dt.strftime('%B').str.lower()
        
        # Mapear nomes dos meses em português
        meses_pt = {
            'january': 'janeiro', 'february': 'fevereiro', 'march': 'março',
            'april': 'abril', 'may': 'maio', 'june': 'junho',
            'july': 'julho', 'august': 'agosto', 'september': 'setembro',
            'october': 'outubro', 'november': 'novembro', 'december': 'dezembro'
        }
        df_copy['mes_nome'] = df_copy['mes_nome'].map(meses_pt)
        
        # Agrupar por mês e contar fluxos únicos
        contagem = df_copy.groupby('mes').agg({
            'fluxo': 'nunique',
            'mes_nome': 'first'
        }).reset_index()
        contagem.columns = ['mes', 'contagem_fluxo', 'mes_nome']
        
        # Ordenar por mês (cronologicamente)
        contagem = contagem.sort_values('mes')
        
        # Criar ordem dos meses para garantir que apareçam corretamente
        ordem_meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                      'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
        
        # Criar coluna auxiliar para ordenação
        contagem['ordem'] = contagem['mes_nome'].apply(
            lambda x: ordem_meses.index(x) if x in ordem_meses else 99
        )
        contagem = contagem.sort_values('ordem')
        
        # Criar gráfico de linha profissional
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=contagem['mes_nome'],
            y=contagem['contagem_fluxo'],
            mode='lines+markers',
            line=dict(color='#495057', width=3),
            marker=dict(color='#495057', size=8),
            fill='tozeroy',
            fillcolor='rgba(73, 80, 87, 0.1)',
            name='Contagem de fluxo'
        ))
        
        fig.update_layout(
            template='plotly_white',
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                title="Mês",
                showgrid=True,
                gridcolor='#e9ecef',
                tickfont=dict(color='#495057'),
                titlefont=dict(color='#495057')
            ),
            yaxis=dict(
                title="Contagem de fluxo",
                showgrid=True,
                gridcolor='#e9ecef',
                tickfont=dict(color='#495057'),
                titlefont=dict(color='#495057')
            ),
            showlegend=False,
            margin=dict(l=50, r=20, t=20, b=50)
        )
        
        return fig
        
    except Exception as e:
        print(f"Erro ao criar gráfico de fluxo por mês: {e}")
        import traceback
        traceback.print_exc()
        return _create_empty_figure("Erro ao processar dados")


def _create_formulario_por_servico_chart(df):
    """Gráfico de barras horizontais - Contagem de formulário por serviço"""
    if 'servico' not in df.columns or 'formulario' not in df.columns:
        return _create_empty_figure("Dados não disponíveis")
    
    try:
        # Agrupar por serviço e contar formulários únicos
        contagem = df.groupby('servico').agg({
            'formulario': 'nunique'
        }).reset_index()
        contagem.columns = ['servico', 'quantidade']
        
        # Ordenar por contagem (decrescente) e pegar top 20
        contagem = contagem.sort_values('quantidade', ascending=True).tail(20)
        
        # Criar gráfico de barras horizontais com Plotly Express
        fig = px.bar(
            contagem,
            x='quantidade',
            y='servico',
            orientation='h',
            text='quantidade',
            color='quantidade',
            color_continuous_scale=['#c7e9b4', '#7fcdbb', '#41b6c4', '#1d91c0', '#225ea8'],  # degrade verde-azulado
        )
        
        fig.update_traces(
            textposition='outside',
            marker_line_color='#ffffff',
            marker_line_width=1.2,
            hovertemplate='<b>%{y}</b><br>Quantidade: %{x}<extra></extra>'
        )
        
        fig.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            margin=dict(l=80, r=40, t=30, b=30),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            coloraxis_showscale=False,
            font=dict(family="Arial", size=13, color="#333333"),
            height=450,
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        print(f"Erro ao criar gráfico de formulário por serviço: {e}")
        import traceback
        traceback.print_exc()
        return _create_empty_figure("Erro ao processar dados")


def _create_servico_por_fluxo_chart(df):
    """Gráfico de barras horizontais - Contagem de serviço por fluxo"""
    if 'fluxo' not in df.columns or 'servico' not in df.columns:
        return _create_empty_figure("Dados não disponíveis")
    
    try:
        # Agrupar por fluxo e contar serviços únicos
        contagem = df.groupby('fluxo').agg({
            'servico': 'nunique'
        }).reset_index()
        contagem.columns = ['fluxo', 'contagem_servico']
        
        # Ordenar por contagem (decrescente) e pegar top 20
        contagem = contagem.sort_values('contagem_servico', ascending=True).tail(20)
        
        # Criar gráfico de barras horizontais
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=contagem['fluxo'],
            x=contagem['contagem_servico'],
            orientation='h',
            marker=dict(color='#495057'),
            text=contagem['contagem_servico'],
            textposition='outside',
            textfont=dict(color='#495057')
        ))
        
        fig.update_layout(
            template='plotly_white',
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                title="Contagem de serviço",
                showgrid=True,
                gridcolor='#e9ecef',
                tickfont=dict(color='#495057'),
                titlefont=dict(color='#495057')
            ),
            yaxis=dict(
                title="fluxo",
                showgrid=False,
                tickfont=dict(color='#495057'),
                titlefont=dict(color='#495057')
            ),
            showlegend=False,
            margin=dict(l=300, r=50, t=20, b=50)
        )
        
        return fig
        
    except Exception as e:
        print(f"Erro ao criar gráfico de serviço por fluxo: {e}")
        return _create_empty_figure("Erro ao processar dados")


def _create_detailed_table(df):
    """Criar tabela detalhada com: Fluxo, Qtd Srv por Fluxo, Serviço, Etapa, Formulário"""
    if df.empty or 'fluxo' not in df.columns:
        return html.Div("Nenhum dado disponível", style={"padding": "20px", "textAlign": "center", "color": "#6c757d"})
    
    try:
        # Agrupar dados para a tabela
        df_table = df.groupby(['fluxo', 'servico', 'etapa', 'formulario']).size().reset_index(name='qtd')
        
        # Calcular quantidade de serviços por fluxo
        servicos_por_fluxo = df.groupby('fluxo')['servico'].nunique().reset_index()
        servicos_por_fluxo.columns = ['fluxo', 'qtd_srv_fluxo']
        
        # Mesclar com dados principais
        df_table = df_table.merge(servicos_por_fluxo, on='fluxo', how='left')
        
        # Reordenar colunas
        df_table = df_table[['fluxo', 'qtd_srv_fluxo', 'servico', 'etapa', 'formulario']]
        
        # Ordenar por fluxo
        df_table = df_table.sort_values('fluxo')
        
        # Adicionar linha de total
        total_servicos = df['servico'].nunique()
        
        # Criar tabela usando dbc.Table
        table_data = []
        
        # Header com posição sticky para ficar fixo durante scroll
        header = html.Thead([
            html.Tr([
                html.Th("Fluxo", style={"backgroundColor": "#495057", "color": "white", "padding": "12px", "position": "sticky", "top": 0, "zIndex": 10}),
                html.Th("Qtd Srv por Fluxo", style={"backgroundColor": "#495057", "color": "white", "padding": "12px", "position": "sticky", "top": 0, "zIndex": 10}),
                html.Th("Serviço", style={"backgroundColor": "#495057", "color": "white", "padding": "12px", "position": "sticky", "top": 0, "zIndex": 10}),
                html.Th("Etapa", style={"backgroundColor": "#495057", "color": "white", "padding": "12px", "position": "sticky", "top": 0, "zIndex": 10}),
                html.Th("Formulário", style={"backgroundColor": "#495057", "color": "white", "padding": "12px", "position": "sticky", "top": 0, "zIndex": 10})
            ])
        ], style={"position": "sticky", "top": 0, "zIndex": 10})
        
        # Body
        body_rows = []
        # Manter todas as linhas, mas exibir apenas 15 com scroll
        MAX_LINHAS_VISIVEIS = 15
        
        for idx, row in df_table.iterrows():
            body_rows.append(
                html.Tr([
                    html.Td(str(row['fluxo']), style={"padding": "10px", "border": "1px solid #dee2e6"}),
                    html.Td(str(int(row['qtd_srv_fluxo'])), style={"padding": "10px", "border": "1px solid #dee2e6", "textAlign": "center"}),
                    html.Td(str(row['servico']), style={"padding": "10px", "border": "1px solid #dee2e6"}),
                    html.Td(str(row['etapa']) if pd.notna(row['etapa']) else "", style={"padding": "10px", "border": "1px solid #dee2e6"}),
                    html.Td(str(row['formulario']) if pd.notna(row['formulario']) else "", style={"padding": "10px", "border": "1px solid #dee2e6"})
                ], style={"backgroundColor": "#ffffff" if idx % 2 == 0 else "#f8f9fa"})
            )
        
        # Footer com total
        footer = html.Tfoot([
            html.Tr([
                html.Td("Total", style={"padding": "12px", "border": "1px solid #dee2e6", 
                      "backgroundColor": "#e9ecef", "fontWeight": "bold"}),
                html.Td(str(total_servicos), style={"padding": "12px", "border": "1px solid #dee2e6", 
                      "backgroundColor": "#e9ecef", "fontWeight": "bold"}),
                html.Td("", style={"padding": "12px", "border": "1px solid #dee2e6", 
                      "backgroundColor": "#e9ecef"}),
                html.Td("", style={"padding": "12px", "border": "1px solid #dee2e6", 
                      "backgroundColor": "#e9ecef"}),
                html.Td("", style={"padding": "12px", "border": "1px solid #dee2e6", 
                      "backgroundColor": "#e9ecef"})
            ])
        ])
        
        table = dbc.Table([
            header,
            html.Tbody(body_rows),
            footer
        ], bordered=True, hover=True, responsive=True, striped=False, 
        style={"marginBottom": 0, "fontSize": "14px", "width": "100%"})
        
        # Calcular altura aproximada: altura do header (50px) + altura de cada linha (48px) + footer (50px)
        # Mostrar MAX_LINHAS_VISIVEIS linhas + header + footer
        altura_linha = 48
        altura_header = 50
        altura_footer = 50
        altura_total = altura_header + (MAX_LINHAS_VISIVEIS * altura_linha) + altura_footer
        
        # Envolver a tabela em uma div com altura fixa e scroll
        # Usar display block para melhor controle do scroll
        tabela_com_scroll = html.Div(
            table,
            style={
                "maxHeight": f"{altura_total}px",
                "overflowY": "auto",
                "overflowX": "auto",
                "border": "1px solid #dee2e6",
                "borderRadius": "4px",
                "display": "block"
            }
        )
        
        return tabela_com_scroll
        
    except Exception as e:
        print(f"Erro ao criar tabela detalhada: {e}")
        import traceback
        traceback.print_exc()
        return html.Div(f"Erro ao criar tabela: {str(e)}", style={"padding": "20px", "color": "#dc3545"})
