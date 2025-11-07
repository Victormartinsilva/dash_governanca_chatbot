from dash import Input, Output
import plotly.express as px
import pandas as pd
import json
import os
from src.utils.data_loader import stream_filtered_df
from src.utils.data_processor import calculate_kpis, prepare_chart_data
from src.pages.campos import campos_layout
import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objects as go

# Caminho do arquivo CSV
CSV_PATH = "data/meu_arquivo.csv"

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
        df = stream_filtered_df(CSV_PATH,
                              filters.get("ano"), 
                              filters.get("fluxo"), 
                              filters.get("servico"), 
                              filters.get("formulario"))

        if df.empty:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0%", empty_fig, empty_fig, None, empty_fig

        try:
            # OTIMIZAÇÃO: Calcular KPIs usando função centralizada (dados já processados)
            kpis = calculate_kpis(df)

            # OTIMIZAÇÃO: Preparar dados para gráficos (amostragem se necessário)
            df_charts = prepare_chart_data(df, max_rows=50000)
            
            # Criar gráficos usando dados já processados
            fig_top = _create_campos_mais_usados_chart(df_charts)
            fig_var = _create_campos_com_variacoes_chart(df_charts)
            fig_diversidade = _create_diversidade_campos_tipo_chart(df_charts)

            tabela_autoria = _create_tabela_autoria_dados(df_charts)

            return str(kpis['qtd_campos_distintos']), str(kpis['qtd_campos_padronizados']), kpis['pct_campos_padrao'], fig_top, fig_var, tabela_autoria, fig_diversidade
                   
        except Exception as e:
            print(f"Erro no callback: {e}")
            empty_fig = _create_empty_figure("Erro ao carregar dados")
            return "0", "0", "0%", empty_fig, empty_fig, None, empty_fig

def _create_campos_mais_usados_chart(df):
    if 'nomeCampo' not in df.columns:
        return _create_empty_figure("Dados de campos não disponíveis")
    
    try:
        top = df['nomeCampo'].value_counts().reset_index()
        top.columns = ['nomeCampo','qtd']
        top = top.sort_values('qtd', ascending=False).head(20)
        
        # Truncar nomes longos para melhor visualização (máximo 50 caracteres)
        MAX_LABEL_LENGTH = 50
        campos_labels = []
        campos_full_names = top['nomeCampo'].tolist()
        
        for name in campos_full_names:
            if len(name) > MAX_LABEL_LENGTH:
                campos_labels.append(name[:MAX_LABEL_LENGTH] + "...")
            else:
                campos_labels.append(name)
        
        # Criar gradiente de cores bonito (tons de azul corporativo)
        n_items = len(top)
        colors = []
        base_color = (46, 134, 171)  # RGB do #2E86AB
        
        for i in range(n_items):
            intensity = 0.6 + (0.4 * (n_items - i) / n_items)
            r, g, b = [int(c * intensity) for c in base_color]
            colors.append(f'rgb({r}, {g}, {b})')
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=top['qtd'],
            y=campos_labels,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.9)', width=2),
                opacity=0.95
            ),
            text=[f"{val:,}".replace(",", ".") for val in top['qtd']],
            textposition='outside',
            textfont=dict(color='#2c3e50', size=12, family='Arial, sans-serif'),
            hovertemplate='<b style="font-size: 14px;">%{customdata}</b><br>' +
                         '<span style="color: #2E86AB;">Quantidade:</span> <b>%{x:,.0f}</b><extra></extra>',
            customdata=campos_full_names,
            cliponaxis=False
        ))
        
        category_array = campos_labels[::-1]
        
        fig.update_layout(
            template='plotly_white',
            height=450,
            plot_bgcolor='#ffffff',
            paper_bgcolor='white',
            xaxis=dict(
                title=dict(
                    text="Quantidade de Ocorrências",
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
        print(f"Erro ao criar gráfico de campos mais usados: {e}")
        return _create_empty_figure("Erro ao processar dados")

def _create_campos_com_variacoes_chart(df):
    if 'nomeCampo' not in df.columns or 'legendaCampoFilho' not in df.columns:
        return _create_empty_figure("Dados de variação de campos não disponíveis")
    
    try:
        var = df.groupby('nomeCampo')['legendaCampoFilho'].nunique().reset_index(name='variacoes')
        var = var.sort_values('variacoes', ascending=False).head(20)
        
        # Truncar nomes longos para melhor visualização (máximo 50 caracteres)
        MAX_LABEL_LENGTH = 50
        campos_labels = []
        campos_full_names = var['nomeCampo'].tolist()
        
        for name in campos_full_names:
            if len(name) > MAX_LABEL_LENGTH:
                campos_labels.append(name[:MAX_LABEL_LENGTH] + "...")
            else:
                campos_labels.append(name)
        
        # Criar gradiente de cores bonito (tons de roxo/azul)
        n_items = len(var)
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
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=var['variacoes'],
            y=campos_labels,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.9)', width=2),
                opacity=0.95
            ),
            text=[f"{val:,}".replace(",", ".") for val in var['variacoes']],
            textposition='outside',
            textfont=dict(color='#2c3e50', size=12, family='Arial, sans-serif'),
            hovertemplate='<b style="font-size: 14px;">%{customdata}</b><br>' +
                         '<span style="color: #3498db;">Variações:</span> <b>%{x:,.0f}</b><extra></extra>',
            customdata=campos_full_names,
            cliponaxis=False
        ))
        
        category_array = campos_labels[::-1]
        
        fig.update_layout(
            template='plotly_white',
            height=450,
            plot_bgcolor='#ffffff',
            paper_bgcolor='white',
            xaxis=dict(
                title=dict(
                    text="Quantidade de Variações",
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
        print(f"Erro ao criar gráfico de campos com variações: {e}")
        return _create_empty_figure("Erro ao processar dados")

def _create_tabela_autoria_dados(df):
    if 'autor' not in df.columns or 'nomeCampo' not in df.columns:
        autoria_data = pd.DataFrame({'Autor': ["N/A"], 'Campos Criados': [0]})
    else:
        autoria_data = df.groupby('autor')['nomeCampo'].nunique().reset_index(name='Campos Criados')
        autoria_data.columns = ['Autor', 'Campos Criados']
        autoria_data = autoria_data.sort_values('Campos Criados', ascending=False).head(10)
    
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
        "textAlign": "left",
        "border": "none",
        "whiteSpace": "nowrap"
    }
    
    header = html.Thead([
        html.Tr([
            html.Th("Autor", style=header_style),
            html.Th("Campos Criados", style={**header_style, "textAlign": "center"})
        ])
    ], style={"position": "sticky", "top": 0, "zIndex": 10})
    
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
    
    for idx, (_, row) in enumerate(autoria_data.iterrows()):
        autor_text = str(row['Autor'])
        if len(autor_text) > 60:
            autor_text = autor_text[:57] + "..."
        
        body_rows.append(
            html.Tr([
                html.Td(autor_text, style={**cell_style, "maxWidth": "300px"}),
                html.Td(str(int(row['Campos Criados'])), style={**cell_style, "textAlign": "center"})
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
            "maxHeight": "450px",
            "overflowY": "auto",
            "overflowX": "auto",
            "border": "1px solid #dee2e6",
            "borderRadius": "8px",
            "display": "block",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
        }
    )
    
    return tabela_com_scroll

def _create_diversidade_campos_tipo_chart(df):
    # OTIMIZAÇÃO: Usar coluna tipo_componente já processada (não precisa calcular novamente)
    if 'tipo_componente' not in df.columns:
        return _create_empty_figure("Dados de tipo de campo não disponíveis")
    
    try:
        diversidade = df['tipo_componente'].value_counts().reset_index()
        diversidade.columns = ['Tipo de Componente', 'Quantidade']
        diversidade = diversidade.sort_values('Quantidade', ascending=False)
        
        # Criar gradiente de cores bonito (tons de verde-azul)
        n_items = len(diversidade)
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
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=diversidade['Tipo de Componente'],
            y=diversidade['Quantidade'],
            marker=dict(
                color=colors,
                line=dict(color='rgba(255, 255, 255, 0.9)', width=2),
                opacity=0.95
            ),
            text=[f"{val:,}".replace(",", ".") for val in diversidade['Quantidade']],
            textposition='outside',
            textfont=dict(color='#2c3e50', size=12, family='Arial, sans-serif'),
            hovertemplate='<b style="font-size: 14px;">%{x}</b><br>' +
                         '<span style="color: #41b6c4;">Quantidade:</span> <b>%{y:,.0f}</b><extra></extra>'
        ))
        
        fig.update_layout(
            template='plotly_white',
            height=450,
            plot_bgcolor='#ffffff',
            paper_bgcolor='white',
            xaxis=dict(
                title=dict(
                    text="Tipo de Componente",
                    font=dict(color='#2c3e50', size=13, family='Arial, sans-serif')
                ),
                showgrid=False,
                tickfont=dict(color='#495057', size=11, family='Arial, sans-serif'),
                tickangle=-45
            ),
            yaxis=dict(
                title=dict(
                    text="Quantidade",
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
            showlegend=False,
            margin=dict(l=60, r=60, t=40, b=120),
            hovermode='closest',
            font=dict(family='Arial, sans-serif', color='#495057'),
            bargap=0.4
        )
        
        return fig
    except Exception as e:
        print(f"Erro ao criar gráfico de diversidade: {e}")
        return _create_empty_figure("Erro ao processar dados")

