from dash import Input, Output, callback_context, State
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import dash_bootstrap_components as dbc
from src.utils.data_loader import stream_filtered_df
from src.utils.data_processor import calculate_kpis, prepare_chart_data
import os
from src.pages.overview import overview_layout
from src.pages.fluxos import fluxos_layout  
from src.pages.formularios import formularios_layout  
from src.pages.campos import campos_layout
from src.pages.biblioteca import biblioteca_layout

# Caminho do arquivo CSV
CSV_PATH = "data/meu_arquivo.csv"


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
        elif tab == "biblioteca":
            return biblioteca_layout()
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
        df = stream_filtered_df(CSV_PATH,
                              filters.get("ano"), 
                              filters.get("fluxo"), 
                              filters.get("servico"), 
                              filters.get("formulario"))
        
        if df.empty:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0", "0", empty_fig, empty_fig, empty_fig, html.Div("Nenhum dado disponível")
        
        try:
            # OTIMIZAÇÃO: Calcular KPIs usando função centralizada (muito mais rápido)
            kpis = calculate_kpis(df)
            
            # OTIMIZAÇÃO: Preparar dados para gráficos (amostragem se necessário)
            df_charts = prepare_chart_data(df, max_rows=50000)
            
            # Criar gráficos usando dados já processados
            fig_fluxo_mes = _create_fluxo_por_mes_chart(df_charts)
            fig_formulario_servico = _create_formulario_por_servico_chart(df_charts)
            fig_servico_fluxo = _create_servico_por_fluxo_chart(df_charts)
            
            # OTIMIZAÇÃO: Limitar dados da tabela para melhor performance
            tabela = _create_detailed_table(df_charts.head(1000))  # Limitar a 1000 linhas
            
            return (str(kpis['qtd_fluxos']), str(kpis['qtd_servicos']), str(kpis['qtd_formularios']), 
                   str(kpis['qtd_etapas']), fig_fluxo_mes, fig_formulario_servico, 
                   fig_servico_fluxo, tabela)
                   
        except Exception as e:
            print(f"Erro no callback: {e}")
            import traceback
            traceback.print_exc()
            empty_fig = _create_empty_figure("Erro ao carregar dados")
            return "0", "0", "0", "0", empty_fig, empty_fig, empty_fig, html.Div(f"Erro: {str(e)}")


def _create_fluxo_por_mes_chart(df):
    """Gráfico de barras horizontais - Top fluxos ordenados do maior para o menor"""
    if 'fluxo' not in df.columns:
        return _create_empty_figure("Dados não disponíveis")
    
    try:
        # Agrupar por fluxo e contar registros, ordenar do maior para o menor
        fluxos_contagem = df.groupby('fluxo').size().sort_values(ascending=False).head(20)
        
        if fluxos_contagem.empty:
            return _create_empty_figure("Nenhum dado disponível")
        
        # Truncar nomes longos para melhor visualização (máximo 50 caracteres)
        MAX_LABEL_LENGTH = 50
        fluxos_labels = []
        fluxos_full_names = fluxos_contagem.index.tolist()
        
        for name in fluxos_full_names:
            if len(name) > MAX_LABEL_LENGTH:
                fluxos_labels.append(name[:MAX_LABEL_LENGTH] + "...")
            else:
                fluxos_labels.append(name)
        
        # Criar gradiente de cores bonito (do mais escuro para o mais claro)
        # Usando tons de azul corporativo (#2E86AB) variando a intensidade
        n_fluxos = len(fluxos_contagem)
        colors = []
        base_color = (46, 134, 171)  # RGB do #2E86AB
        
        for i in range(n_fluxos):
            # Gradiente do mais escuro (maior valor) para o mais claro (menor valor)
            intensity = 0.6 + (0.4 * (n_fluxos - i) / n_fluxos)  # Varia de 0.6 a 1.0
            r, g, b = [int(c * intensity) for c in base_color]
            colors.append(f'rgb({r}, {g}, {b})')
        
        # Criar gráfico de barras horizontais com visual moderno e profissional
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=fluxos_contagem.values,
            y=fluxos_labels,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.9)', width=2),
                opacity=0.95
            ),
            text=[f"{val:,}".replace(",", ".") for val in fluxos_contagem.values],
            textposition='outside',
            textfont=dict(color='#2c3e50', size=12, family='Arial, sans-serif'),
            hovertemplate='<b style="font-size: 14px;">%{customdata}</b><br>' +
                         '<span style="color: #2E86AB;">Quantidade:</span> <b>%{x:,.0f}</b><extra></extra>',
            customdata=fluxos_full_names,  # Armazenar nome completo para hover
            cliponaxis=False
        ))
        
        # Inverter ordem para mostrar maior no topo
        category_array = fluxos_labels[::-1]
        
        fig.update_layout(
            template='plotly_white',
            height=450,
            plot_bgcolor='#ffffff',
            paper_bgcolor='white',
            xaxis=dict(
                title=dict(
                    text="Quantidade de Registros",
                    font=dict(color='#2c3e50', size=13, family='Arial, sans-serif')
                ),
                showgrid=True,
                gridcolor='rgba(230, 236, 240, 0.8)',
                gridwidth=1.5,
                tickfont=dict(color='#6c757d', size=11, family='Arial, sans-serif'),
                showline=False,
                zeroline=True,
                zerolinecolor='rgba(230, 236, 240, 0.8)',
                zerolinewidth=1.5
            ),
            yaxis=dict(
                title="",
                showgrid=False,
                tickfont=dict(color='#495057', size=10, family='Arial, sans-serif'),
                showline=False,
                categoryorder='array',
                categoryarray=category_array  # Invertido para maior no topo
            ),
            showlegend=False,
            margin=dict(l=180, r=120, t=20, b=60),  # Reduzir margem esquerda para dar mais espaço às barras
            hovermode='closest',
            font=dict(family='Arial, sans-serif', color='#495057'),
            bargap=0.4,
            barmode='group'
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
        contagem = contagem.sort_values('quantidade', ascending=False).head(20)
        
        # Truncar nomes longos para melhor visualização (máximo 50 caracteres)
        MAX_LABEL_LENGTH = 50
        servicos_labels = []
        servicos_full_names = contagem['servico'].tolist()
        
        for name in servicos_full_names:
            if len(name) > MAX_LABEL_LENGTH:
                servicos_labels.append(name[:MAX_LABEL_LENGTH] + "...")
            else:
                servicos_labels.append(name)
        
        # Criar gradiente de cores bonito (tons de verde-azul)
        n_items = len(contagem)
        colors = []
        # Gradiente de verde para azul
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
                # Interpolação entre as cores base
                color_idx = int((i / (n_items - 1)) * (len(base_colors) - 1))
                if color_idx >= len(base_colors) - 1:
                    r, g, b = base_colors[-1]
                else:
                    # Interpolação linear entre duas cores
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
            x=contagem['quantidade'],
            y=servicos_labels,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.9)', width=2),
                opacity=0.95
            ),
            text=[f"{val:,}".replace(",", ".") for val in contagem['quantidade']],
            textposition='outside',
            textfont=dict(color='#2c3e50', size=12, family='Arial, sans-serif'),
            hovertemplate='<b style="font-size: 14px;">%{customdata}</b><br>' +
                         '<span style="color: #41b6c4;">Formulários:</span> <b>%{x:,.0f}</b><extra></extra>',
            customdata=servicos_full_names,  # Armazenar nome completo para hover
            cliponaxis=False
        ))
        
        # Inverter ordem para mostrar maior no topo
        category_array = servicos_labels[::-1]
        
        fig.update_layout(
            template='plotly_white',
            height=450,
            plot_bgcolor='#ffffff',
            paper_bgcolor='white',
            xaxis=dict(
                title=dict(
                    text="Quantidade de Formulários",
                    font=dict(color='#2c3e50', size=13, family='Arial, sans-serif')
                ),
                showgrid=True,
                gridcolor='rgba(230, 236, 240, 0.8)',
                gridwidth=1.5,
                tickfont=dict(color='#6c757d', size=11, family='Arial, sans-serif'),
                showline=False,
                zeroline=True,
                zerolinecolor='rgba(230, 236, 240, 0.8)',
                zerolinewidth=1.5
            ),
            yaxis=dict(
                title="",
                showgrid=False,
                tickfont=dict(color='#495057', size=10, family='Arial, sans-serif'),
                showline=False,
                categoryorder='array',
                categoryarray=category_array  # Invertido para maior no topo
            ),
            showlegend=False,
            margin=dict(l=180, r=120, t=20, b=60),  # Reduzir margem esquerda para dar mais espaço às barras
            hovermode='closest',
            font=dict(family='Arial, sans-serif', color='#495057'),
            bargap=0.4
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
        contagem = contagem.sort_values('contagem_servico', ascending=False).head(20)
        
        # Truncar nomes longos para melhor visualização (máximo 50 caracteres)
        MAX_LABEL_LENGTH = 50
        fluxos_labels = []
        fluxos_full_names = contagem['fluxo'].tolist()
        
        for name in fluxos_full_names:
            if len(name) > MAX_LABEL_LENGTH:
                fluxos_labels.append(name[:MAX_LABEL_LENGTH] + "...")
            else:
                fluxos_labels.append(name)
        
        # Criar gradiente de cores bonito (tons de roxo/azul)
        n_items = len(contagem)
        colors = []
        # Gradiente de roxo para azul
        base_colors = [
            (155, 89, 182),   # Roxo claro
            (142, 68, 173),   # Roxo médio
            (102, 126, 234),  # Azul-roxo
            (52, 152, 219),   # Azul claro
            (41, 128, 185)    # Azul escuro
        ]
        
        if n_items == 0:
            colors = []
        elif n_items == 1:
            colors = [f'rgb({base_colors[0][0]}, {base_colors[0][1]}, {base_colors[0][2]})']
        else:
            for i in range(n_items):
                # Interpolação entre as cores base
                color_idx = int((i / (n_items - 1)) * (len(base_colors) - 1))
                if color_idx >= len(base_colors) - 1:
                    r, g, b = base_colors[-1]
                else:
                    # Interpolação linear entre duas cores
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
            x=contagem['contagem_servico'],
            y=fluxos_labels,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.9)', width=2),
                opacity=0.95
            ),
            text=[f"{val:,}".replace(",", ".") for val in contagem['contagem_servico']],
            textposition='outside',
            textfont=dict(color='#2c3e50', size=12, family='Arial, sans-serif'),
            hovertemplate='<b style="font-size: 14px;">%{customdata}</b><br>' +
                         '<span style="color: #3498db;">Serviços:</span> <b>%{x:,.0f}</b><extra></extra>',
            customdata=fluxos_full_names,  # Armazenar nome completo para hover
            cliponaxis=False
        ))
        
        # Inverter ordem para mostrar maior no topo
        category_array = fluxos_labels[::-1]
        
        fig.update_layout(
            template='plotly_white',
            height=450,
            plot_bgcolor='#ffffff',
            paper_bgcolor='white',
            xaxis=dict(
                title=dict(
                    text="Quantidade de Serviços",
                    font=dict(color='#2c3e50', size=13, family='Arial, sans-serif')
                ),
                showgrid=True,
                gridcolor='rgba(230, 236, 240, 0.8)',
                gridwidth=1.5,
                tickfont=dict(color='#6c757d', size=11, family='Arial, sans-serif'),
                showline=False,
                zeroline=True,
                zerolinecolor='rgba(230, 236, 240, 0.8)',
                zerolinewidth=1.5
            ),
            yaxis=dict(
                title="",
                showgrid=False,
                tickfont=dict(color='#495057', size=10, family='Arial, sans-serif'),
                showline=False,
                categoryorder='array',
                categoryarray=category_array  # Invertido para maior no topo
            ),
            showlegend=False,
            margin=dict(l=180, r=120, t=20, b=60),  # Reduzir margem esquerda para dar mais espaço às barras
            hovermode='closest',
            font=dict(family='Arial, sans-serif', color='#495057'),
            bargap=0.4
        )
        
        return fig
        
    except Exception as e:
        print(f"Erro ao criar gráfico de serviço por fluxo: {e}")
        import traceback
        traceback.print_exc()
        return _create_empty_figure("Erro ao processar dados")


def _create_detailed_table(df):
    """Criar tabela detalhada com: Fluxo, Qtd Srv por Fluxo, Serviço, Etapa (se disponível), Formulário"""
    if df.empty or 'fluxo' not in df.columns:
        return html.Div("Nenhum dado disponível", style={"padding": "20px", "textAlign": "center", "color": "#6c757d"})
    
    try:
        # Determinar colunas para agrupar (etapa é opcional)
        groupby_cols = ['fluxo', 'servico', 'formulario']
        if 'etapa' in df.columns:
            groupby_cols.insert(2, 'etapa')
        
        # Agrupar dados para a tabela
        df_table = df.groupby(groupby_cols).size().reset_index(name='qtd')
        
        # Calcular quantidade de serviços por fluxo
        servicos_por_fluxo = df.groupby('fluxo')['servico'].nunique().reset_index()
        servicos_por_fluxo.columns = ['fluxo', 'qtd_srv_fluxo']
        
        # Mesclar com dados principais
        df_table = df_table.merge(servicos_por_fluxo, on='fluxo', how='left')
        
        # Reordenar colunas (etapa é opcional)
        table_cols = ['fluxo', 'qtd_srv_fluxo', 'servico']
        if 'etapa' in df_table.columns:
            table_cols.append('etapa')
        table_cols.append('formulario')
        df_table = df_table[table_cols]
        
        # Ordenar por fluxo
        df_table = df_table.sort_values('fluxo')
        
        # OTIMIZAÇÃO: Limitar número de linhas processadas para melhor performance
        MAX_LINHAS_VISIVEIS = 15
        MAX_LINHAS_PROCESSAR = 200  # Processar no máximo 200 linhas (depois agrupar)
        
        # Calcular total antes de limitar
        total_servicos = df['servico'].nunique()
        
        # Limitar dados processados antes de criar HTML
        df_table_limited = df_table.head(MAX_LINHAS_PROCESSAR)
        
        # Criar tabela usando dbc.Table
        table_data = []
        
        # Header com estilo azul escuro e bordas arredondadas
        header_style = {
            "backgroundColor": "#1e3a5f",  # Azul escuro similar à imagem
            "color": "white",
            "padding": "14px 16px",
            "position": "sticky",
            "top": 0,
            "zIndex": 10,
            "fontWeight": "bold",
            "fontSize": "15px",
            "textAlign": "left",
            "border": "none"
        }
        
        header_cells = [
            html.Th("Fluxo", style=header_style),
            html.Th("Qtd Srv por Fluxo", style={**header_style, "textAlign": "center"}),
            html.Th("Serviço", style=header_style)
        ]
        if 'etapa' in df_table.columns:
            header_cells.append(html.Th("Etapa", style=header_style))
        header_cells.append(html.Th("Formulário", style=header_style))
        
        header = html.Thead([
            html.Tr(header_cells)
        ], style={"position": "sticky", "top": 0, "zIndex": 10})
        
        # Body com melhor estilo e tamanho de texto
        body_rows = []
        
        cell_style = {
            "padding": "12px 16px",
            "border": "1px solid #dee2e6",
            "fontSize": "14px",
            "color": "#212529"
        }
        
        for idx, row in df_table_limited.iterrows():
            row_cells = [
                html.Td(str(row['fluxo']), style={**cell_style}),
                html.Td(str(int(row['qtd_srv_fluxo'])), style={**cell_style, "textAlign": "center"}),
                html.Td(str(row['servico']), style={**cell_style})
            ]
            if 'etapa' in df_table.columns:
                row_cells.append(html.Td(str(row['etapa']) if pd.notna(row['etapa']) else "", style={**cell_style}))
            row_cells.append(html.Td(str(row['formulario']) if pd.notna(row['formulario']) else "", style={**cell_style}))
            
            body_rows.append(
                html.Tr(row_cells, style={
                    "backgroundColor": "#ffffff" if idx % 2 == 0 else "#f8f9fa",
                    "borderBottom": "1px solid #dee2e6"
                })
            )
        
        # Footer com total
        footer_style = {
            "padding": "14px 16px",
            "border": "1px solid #dee2e6",
            "backgroundColor": "#e9ecef",
            "fontWeight": "bold",
            "fontSize": "15px"
        }
        
        footer_cells = [
            html.Td("Total", style={**footer_style}),
            html.Td(str(total_servicos), style={**footer_style, "textAlign": "center"}),
            html.Td("", style={**footer_style})
        ]
        if 'etapa' in df_table.columns:
            footer_cells.append(html.Td("", style={**footer_style}))
        footer_cells.append(html.Td("", style={**footer_style}))
        
        footer = html.Tfoot([
            html.Tr(footer_cells)
        ])
        
        table = dbc.Table([
            header,
            html.Tbody(body_rows),
            footer
        ], bordered=False, hover=True, responsive=True, striped=False, 
        style={
            "marginBottom": 0,
            "fontSize": "14px",
            "width": "100%",
            "borderCollapse": "separate",
            "borderSpacing": 0,
            "borderRadius": "8px",
            "overflow": "hidden"
        })
        
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
                "borderRadius": "8px",
                "display": "block",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
            }
        )
        
        return tabela_com_scroll
        
    except Exception as e:
        print(f"Erro ao criar tabela detalhada: {e}")
        import traceback
        traceback.print_exc()
        return html.Div(f"Erro ao criar tabela: {str(e)}", style={"padding": "20px", "color": "#dc3545"})
