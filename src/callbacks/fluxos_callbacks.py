from dash import Input, Output, no_update
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import os
from src.utils.data_loader import stream_filtered_df
from src.utils.data_processor import calculate_kpis, calculate_padronizacao_por_fluxo, prepare_chart_data
from src.pages.fluxos import fluxos_layout
import dash_bootstrap_components as dbc
from dash import html

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

# REMOVIDO: Funções _get_tipo_componente, _is_padronizado e _create_fluxos_hierarquia_tree
# Agora usamos src.utils.data_processor que centraliza todo o processamento
# O gráfico de hierarquia foi movido para a página Biblioteca (biblioteca_callbacks.py)

def register_callbacks(app):
    @app.callback(
        Output("card-servicos-fluxo", "children"),
        Output("card-fluxos-fluxo", "children"),
        Output("media-campos-fluxo", "children"),
        Output("pct-fluxo-padronizado", "children"),
        Output("percentual-padronizacao-fluxo", "figure"),
        Output("contagem-servico-por-fluxo", "figure"),
        Output("padronizacao-por-fluxo-tabela", "children"),
        Input("filtered-data-store", "data"),
        prevent_initial_call=False,
        allow_duplicate=True
    )
    def update_fluxos(filtered_data_json):
        if filtered_data_json is None:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0", "0%", empty_fig, empty_fig, html.Div("Nenhum dado disponível")

        # Busca dados diretamente do cache usando os filtros
        filters = filtered_data_json
        df = stream_filtered_df(CSV_PATH,
                              filters.get("ano"), 
                              filters.get("fluxo"), 
                              filters.get("servico"), 
                              filters.get("formulario"))
        
        if df.empty:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0", "0%", empty_fig, empty_fig, html.Div("Nenhum dado disponível")

        try:
            # OTIMIZAÇÃO: Calcular KPIs usando função centralizada (dados já processados)
            kpis = calculate_kpis(df)
            
            # OTIMIZAÇÃO: Preparar dados para gráficos (amostragem se necessário)
            df_charts = prepare_chart_data(df, max_rows=50000)
            
            # Criar gráficos usando dados já processados
            fig_percentual_padronizacao = _create_fluxo_padronizacao_chart(df_charts)
            fig_contagem_servico_fluxo = _create_ranking_chart(df_charts)
            tabela_padronizacao = _create_padronizacao_tabela(df_charts)
            
            return str(kpis['qtd_servicos']), str(kpis['qtd_fluxos']), str(kpis['media_campos_fluxo']), kpis['pct_fluxo_padronizado'], fig_percentual_padronizacao, fig_contagem_servico_fluxo, tabela_padronizacao
            
        except Exception as e:
            print(f"Erro ao atualizar gráficos de fluxos: {e}")
            import traceback
            traceback.print_exc()
            empty_fig = _create_empty_figure("Erro ao carregar dados")
            return "0", "0", "0", "0%", empty_fig, empty_fig, html.Div(f"Erro: {str(e)}")

def _create_fluxo_padronizacao_chart(df):
    """Gráfico de barras horizontais - Percentual de Padronização por Fluxo"""
    if 'fluxo' not in df.columns:
        return _create_empty_figure("Dados não disponíveis")
    
    try:
        # OTIMIZAÇÃO: is_padronizado já existe no DataFrame processado
        if 'is_padronizado' not in df.columns:
            return _create_empty_figure("Dados não disponíveis")
        
        # Calcular percentual de padronização por fluxo
        padronizacao = df.groupby('fluxo').agg(
            total_campos=('is_padronizado', 'count'),
            campos_padronizados=('is_padronizado', 'sum')
        ).reset_index()
        
        padronizacao['percent_padronizado'] = (padronizacao['campos_padronizados'] / padronizacao['total_campos'] * 100).round(1)
        padronizacao = padronizacao.sort_values('percent_padronizado', ascending=True).tail(20)
        
        # Truncar nomes longos para melhor visualização (máximo 50 caracteres)
        MAX_LABEL_LENGTH = 50
        fluxos_labels = []
        fluxos_full_names = padronizacao['fluxo'].tolist()
        
        for name in fluxos_full_names:
            if len(name) > MAX_LABEL_LENGTH:
                fluxos_labels.append(name[:MAX_LABEL_LENGTH] + "...")
            else:
                fluxos_labels.append(name)
        
        # Criar gradiente de cores baseado no percentual (vermelho para baixo, verde para alto)
        colors = []
        for pct in padronizacao['percent_padronizado']:
            if pct < 30:
                colors.append('#e74c3c')  # Vermelho
            elif pct < 50:
                colors.append('#f39c12')  # Laranja
            elif pct < 70:
                colors.append('#3498db')  # Azul
            elif pct < 90:
                colors.append('#2ecc71')  # Verde claro
            else:
                colors.append('#27ae60')  # Verde escuro
        
        # Criar gráfico de barras horizontais
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=padronizacao['percent_padronizado'],
            y=fluxos_labels,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.9)', width=2),
                opacity=0.95
            ),
            text=[f"{val:.1f}%" for val in padronizacao['percent_padronizado']],
            textposition='outside',
            textfont=dict(color='#2c3e50', size=12, family='Arial, sans-serif'),
            hovertemplate='<b style="font-size: 14px;">%{customdata}</b><br>' +
                         '<span style="color: #e74c3c;">% Padronização:</span> <b>%{x:.1f}%</b><extra></extra>',
            customdata=fluxos_full_names,
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
                    text="% Padronização",
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
                range=[0, 105]
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
        print(f"Erro ao criar gráfico de padronização: {e}")
        import traceback
        traceback.print_exc()
        return _create_empty_figure("Erro ao processar dados")

def _create_ranking_chart(df):
    """Gráfico de barras horizontais - Análise de Fluxos por Serviços (Contagem de serviço)"""
    if 'fluxo' not in df.columns or 'servico' not in df.columns:
        return _create_empty_figure("Dados não disponíveis")
    
    try:
        # Agrupar por fluxo e contar serviços únicos
        ranking = df.groupby('fluxo')['servico'].nunique().reset_index()
        ranking.columns = ['fluxo', 'contagem_servico']
        ranking = ranking.sort_values('contagem_servico', ascending=False).head(20)
        
        # Truncar nomes longos para melhor visualização (máximo 50 caracteres)
        MAX_LABEL_LENGTH = 50
        fluxos_labels = []
        fluxos_full_names = ranking['fluxo'].tolist()
        
        for name in fluxos_full_names:
            if len(name) > MAX_LABEL_LENGTH:
                fluxos_labels.append(name[:MAX_LABEL_LENGTH] + "...")
            else:
                fluxos_labels.append(name)
        
        # Criar gradiente de cores bonito (tons de roxo/azul)
        n_items = len(ranking)
        colors = []
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
            x=ranking['contagem_servico'],
            y=fluxos_labels,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.9)', width=2),
                opacity=0.95
            ),
            text=[f"{val:,}".replace(",", ".") for val in ranking['contagem_servico']],
            textposition='outside',
            textfont=dict(color='#2c3e50', size=12, family='Arial, sans-serif'),
            hovertemplate='<b style="font-size: 14px;">%{customdata}</b><br>' +
                         '<span style="color: #3498db;">Serviços:</span> <b>%{x:,.0f}</b><extra></extra>',
            customdata=fluxos_full_names,
            cliponaxis=False
        ))
        
        # Inverter ordem para mostrar maior no topo
        category_array = fluxos_labels[::-1]
        
        # Altura da tabela: header(50) + 15 linhas(48px cada) + footer(50) = 820px
        fig.update_layout(
            template='plotly_white',
            height=820,
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
                zerolinewidth=1.5,
                range=[0, ranking['contagem_servico'].max() * 1.15]
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
        print(f"Erro ao criar gráfico de contagem de serviço: {e}")
        import traceback
        traceback.print_exc()
        return _create_empty_figure("Erro ao processar dados")

def _create_padronizacao_tabela(df):
    """Criar tabela de padronização por fluxo usando a fórmula do PowerBI"""
    if df.empty or 'fluxo' not in df.columns or 'nomeCampo' not in df.columns:
        return html.Div("Nenhum dado disponível", style={"padding": "20px", "textAlign": "center", "color": "#6c757d"})
    
    try:
        # Criar cópia para não modificar o original
        df_work = df.copy()
        
        # OTIMIZAÇÃO: is_padronizado já existe no DataFrame processado
        # Não precisa recalcular
        
        # Agrupar dados para a tabela
        # Campos do Formulário = quantidade de campos únicos por fluxo
        # Campos Padronizados = quantidade de campos únicos padronizados por fluxo
        # (contar campos únicos onde is_padronizado = 1)
        
        # Agrupar por fluxo e contar campos únicos
        campos_por_fluxo = df_work.groupby('fluxo').agg(
            Campos_Formulario=('nomeCampo', 'nunique')
        ).reset_index()
        
        # Para campos padronizados, filtrar apenas os padronizados e contar únicos por fluxo
        df_padronizados = df_work[df_work['is_padronizado'] == 1]
        if not df_padronizados.empty:
            campos_padronizados_por_fluxo = df_padronizados.groupby('fluxo').agg(
                Campos_Padronizados=('nomeCampo', 'nunique')
            ).reset_index()
        else:
            campos_padronizados_por_fluxo = pd.DataFrame(columns=['fluxo', 'Campos_Padronizados'])
        
        # Fazer merge dos dados
        padronizacao_por_fluxo = campos_por_fluxo.merge(
            campos_padronizados_por_fluxo, 
            on='fluxo', 
            how='left'
        ).fillna(0)
        
        # Converter para int
        padronizacao_por_fluxo['Campos_Padronizados'] = padronizacao_por_fluxo['Campos_Padronizados'].astype(int)
        
        padronizacao_por_fluxo.columns = ['Fluxo', 'Campos do Formulário', 'Campos Padronizados']
        padronizacao_por_fluxo['% Padronização do Fluxo'] = (
            padronizacao_por_fluxo['Campos Padronizados'] / padronizacao_por_fluxo['Campos do Formulário'] * 100
        ).round(1)
        
        # Ordenar por percentual (decrescente)
        padronizacao_por_fluxo = padronizacao_por_fluxo.sort_values('% Padronização do Fluxo', ascending=False)
        
        # Adicionar linha de total
        total_campos = padronizacao_por_fluxo['Campos do Formulário'].sum()
        total_padronizados = padronizacao_por_fluxo['Campos Padronizados'].sum()
        pct_total = (total_padronizados / total_campos * 100).round(1) if total_campos > 0 else 0
        
        # Criar tabela usando dbc.Table com estilo similar à overview
        # Header com posição sticky e estilo melhorado
        header_style = {
            "backgroundColor": "#1e3a5f",
            "color": "white",
            "padding": "12px 16px",
            "position": "sticky",
            "top": 0,
            "zIndex": 10,
            "fontWeight": "bold",
            "fontSize": "13px",
            "textAlign": "left",
            "border": "none",
            "whiteSpace": "nowrap"
        }
        
        header = html.Thead([
            html.Tr([
                html.Th("Fluxo", style=header_style),
                html.Th("Campos do Formulário", style={**header_style, "textAlign": "center"}),
                html.Th("Campos Padronizados", style={**header_style, "textAlign": "center"}),
                html.Th("% Padronização", style={**header_style, "textAlign": "center"})
            ])
        ], style={"position": "sticky", "top": 0, "zIndex": 10})
        
        # Body com melhor estilo e tamanho de texto
        body_rows = []
        MAX_LINHAS_VISIVEIS = 15
        
        cell_style = {
            "padding": "12px 16px",
            "border": "1px solid #dee2e6",
            "fontSize": "13px",
            "color": "#212529",
            "whiteSpace": "nowrap",
            "overflow": "hidden",
            "textOverflow": "ellipsis"
        }
        
        for idx, row in padronizacao_por_fluxo.iterrows():
            # Truncar nome do fluxo se muito longo
            fluxo_text = str(row['Fluxo'])
            if len(fluxo_text) > 60:
                fluxo_text = fluxo_text[:57] + "..."
            
            body_rows.append(
                html.Tr([
                    html.Td(fluxo_text, style={**cell_style, "maxWidth": "300px"}),
                    html.Td(str(int(row['Campos do Formulário'])), style={**cell_style, "textAlign": "center"}),
                    html.Td(str(int(row['Campos Padronizados'])), style={**cell_style, "textAlign": "center"}),
                    html.Td(f"{row['% Padronização do Fluxo']:.1f}%", style={**cell_style, "textAlign": "center"})
                ], style={
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
            "fontSize": "14px"
        }
        
        footer = html.Tfoot([
            html.Tr([
                html.Td("Total", style={**footer_style}),
                html.Td(str(int(total_campos)), style={**footer_style, "textAlign": "center"}),
                html.Td(str(int(total_padronizados)), style={**footer_style, "textAlign": "center"}),
                html.Td(f"{pct_total:.1f}%", style={**footer_style, "textAlign": "center"})
            ])
        ])
        
        table = dbc.Table([
            header,
            html.Tbody(body_rows),
            footer
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
        
        # Calcular altura e envolver em div com scroll
        altura_linha = 48
        altura_header = 50
        altura_footer = 50
        altura_total = altura_header + (MAX_LINHAS_VISIVEIS * altura_linha) + altura_footer
        
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
        print(f"Erro ao criar tabela de padronização: {e}")
        import traceback
        traceback.print_exc()
        return html.Div(f"Erro ao criar tabela: {str(e)}", style={"padding": "20px", "color": "#dc3545"})

