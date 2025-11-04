from dash import Input, Output, no_update
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from src.utils.data_cache import get_filtered_data, get_sampled_data_for_charts
from src.pages.fluxos import fluxos_layout
import dash_bootstrap_components as dbc
from dash import html

def _get_tipo_componente(nome_campo: str) -> str:
    """
    Determina o tipo de componente baseado nos prefixos do nomeCampo.
    Adaptado da fórmula PowerBI Categorias_Campos1.
    """
    if pd.isna(nome_campo) or str(nome_campo) == 'nan':
        return "Outros/Sem Padrão"
    
    nome_campo_str = str(nome_campo)
    
    # Prefixos de 3 letras
    if len(nome_campo_str) >= 3:
        prefixo_3 = nome_campo_str[:3]
        if prefixo_3 == "LBL":
            return "Label"
        elif prefixo_3 == "TXT":
            return "TextBox"
        elif prefixo_3 == "TXA":
            return "Textarea"
        elif prefixo_3 == "CHK":
            return "CheckBox"
        elif prefixo_3 == "RAD":
            return "RadioButton"
        elif prefixo_3 == "CBO":
            return "Combobox"
        elif prefixo_3 == "IMG":
            return "Imagem"
        elif prefixo_3 == "DT_":
            return "Data"
        elif prefixo_3 == "LNK":
            return "Hiperlink"
        elif prefixo_3 == "ARQ":
            return "Arquivo"
        elif prefixo_3 == "MAP":
            return "Mapa"
        elif prefixo_3 == "ENT":
            return "Entidade"
        elif prefixo_3 == "FT_":
            return "Foto"
        elif prefixo_3 == "PLT":
            return "Planta"
        elif prefixo_3 == "BTN":
            return "Button"
        elif prefixo_3 == "GRD":
            return "Grid"
        elif prefixo_3 == "CSM":
            return "Consumo"
        elif prefixo_3 == "AGD":
            return "Agendamento"
        elif prefixo_3 == "FLX":
            return "Fluxo"
    
    # Prefixos de 4 letras
    if len(nome_campo_str) >= 4:
        prefixo_4 = nome_campo_str[:4]
        if prefixo_4 == "MULT":
            return "Múltiplos"
        elif prefixo_4 == "CMIE":
            return "Campos Integrados"
        elif prefixo_4 == "CLAS":
            return "Classificação"
        elif prefixo_4 == "BTI_":
            return "Botão de Integração"
        elif prefixo_4 == "UORG":
            return "Sigla"
    
    # Prefixos de 5 letras
    if len(nome_campo_str) >= 5:
        prefixo_5 = nome_campo_str[:5]
        if prefixo_5 == "NUM_":
            return "Numérico"
        elif prefixo_5 == "VAL_":
            return "Valor Monetário"
        elif prefixo_5 == "ID_":
            return "Identificador"
        elif prefixo_5 == "OBS_":
            return "Observação"
        elif prefixo_5 == "DESC":
            return "Descrição"
        elif prefixo_5 == "END_":
            return "Endereço"
        elif prefixo_5 == "TEL_":
            return "Telefone"
        elif prefixo_5 == "EMA_":
            return "E-mail"
        elif prefixo_5 == "CPF_":
            return "CPF"
        elif prefixo_5 == "CNP_":
            return "CNPJ"
        elif prefixo_5 == "CEP_":
            return "CEP"
        elif prefixo_5 == "URL_":
            return "URL"
        elif prefixo_5 == "GEO_":
            return "Georreferência"
        elif prefixo_5 == "ASS_":
            return "Assinatura"
        elif prefixo_5 == "TAB_":
            return "Tabela"
        elif prefixo_5 == "CON_":
            return "Contato"
        elif prefixo_5 == "PRO_":
            return "Produto"
        elif prefixo_5 == "SER_":
            return "Serviço"
    
    return "Outros/Sem Padrão"

def _is_padronizado(nome_campo: str) -> int:
    """
    Determina se um campo é padronizado baseado na fórmula PowerBI.
    Padronizado = 1 se:
    - LEFT([nomeCampo], 3) IN {"TXT", "CBO", "RAD", "CHK"} OU
    - LEFT([nomeCampo], 5) IN {"CPF_", "CNP_", "CEP_", "TEL_", "EMA_"}
    Padronizado = 0 caso contrário
    """
    if pd.isna(nome_campo) or str(nome_campo) == 'nan':
        return 0
    
    nome_campo_str = str(nome_campo)
    
    # Verificar prefixos de 3 letras (sem underscore)
    if len(nome_campo_str) >= 3:
        prefixo_3 = nome_campo_str[:3]
        if prefixo_3 in ["TXT", "CBO", "RAD", "CHK"]:
            return 1
    
    # Verificar prefixos de 5 letras (com underscore)
    if len(nome_campo_str) >= 5:
        prefixo_5 = nome_campo_str[:5]
        if prefixo_5 in ["CPF_", "CNP_", "CEP_", "TEL_", "EMA_"]:
            return 1
    
    return 0

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
        Output("card-servicos-fluxo", "children"),
        Output("card-fluxos-fluxo", "children"),
        Output("media-campos-fluxo", "children"),
        Output("pct-fluxo-padronizado", "children"),
        Output("percentual-padronizacao-fluxo", "figure"),
        Output("contagem-servico-por-fluxo", "figure"),
        Output("padronizacao-por-fluxo-tabela", "children"),
        Output("fluxos-hierarquia-tree", "figure"),  # Adicionar este output
        Input("filtered-data-store", "data"),
        prevent_initial_call=False,
        allow_duplicate=True
    )
    def update_fluxos(filtered_data_json):
        if filtered_data_json is None:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0", "0%", empty_fig, empty_fig, html.Div("Nenhum dado disponível"), empty_fig

        # Busca dados diretamente do cache usando os filtros
        filters = filtered_data_json
        
        # Usa dados enriquecidos para TODOS os cálculos (incluindo cards)
        # Isso garante que os dados sejam consistentes entre cards, gráficos e tabela
        # Primeiro obtém dados filtrados
        df = get_filtered_data("data/meu_arquivo.csv", 
                              filters.get("ano"), 
                              filters.get("fluxo"), 
                              filters.get("servico"), 
                              filters.get("formulario"))
        
        # Aplica enriquecimento de dados usando get_sampled_data_for_charts
        # Mas sem amostragem para garantir todos os dados (sample_size muito grande)
        df = get_sampled_data_for_charts("data/meu_arquivo.csv", 
                                        filters.get("ano"), 
                                        filters.get("fluxo"), 
                                        filters.get("servico"), 
                                        filters.get("formulario"),
                                        sample_size=999999999,  # Valor muito grande para não amostrar
                                        enrich_data=True)
        
        if df.empty:
            empty_fig = _create_empty_figure("Nenhum dado disponível")
            return "0", "0", "0", "0%", empty_fig, empty_fig, html.Div("Nenhum dado disponível"), empty_fig

        try:
            qtd_servicos = df['servico'].nunique() if 'servico' in df.columns else 0
            qtd_fluxos = df['fluxo'].nunique() if 'fluxo' in df.columns else 0
            media_campos_fluxo = round(df.groupby('fluxo')['nomeCampo'].nunique().mean(), 2) if 'fluxo' in df.columns and 'nomeCampo' in df.columns else 0
            
            # Calcular padronização usando a fórmula do PowerBI
            # O card deve mostrar a média dos percentuais de padronização por fluxo
            # calculada como: campos únicos padronizados / campos únicos totais por fluxo
            if 'nomeCampo' in df.columns:
                df["is_padronizado"] = df["nomeCampo"].apply(_is_padronizado)
                
                # Calcular percentual de padronização por fluxo (baseado em campos únicos)
                percentuais_fluxos = []
                
                for fluxo in df['fluxo'].unique():
                    df_fluxo = df[df['fluxo'] == fluxo]
                    total_campos_unicos = df_fluxo['nomeCampo'].nunique()
                    
                    if total_campos_unicos > 0:
                        # Filtrar apenas campos padronizados e contar únicos
                        campos_padronizados_unicos = df_fluxo[df_fluxo['is_padronizado'] == 1]['nomeCampo'].nunique()
                        pct_fluxo = (campos_padronizados_unicos / total_campos_unicos) * 100
                        percentuais_fluxos.append(pct_fluxo)
                
                # Calcular média dos percentuais
                if percentuais_fluxos:
                    pct_medio = sum(percentuais_fluxos) / len(percentuais_fluxos)
                    pct_fluxo_padronizado = f"{pct_medio:.1f}%"
                else:
                    pct_fluxo_padronizado = "0%"
            else:
                pct_fluxo_padronizado = "0%"

            # Usa os mesmos dados enriquecidos para gráficos
            df_charts = df.copy()
            
            # Adicionar coluna is_padronizado ao df_charts também
            if 'nomeCampo' in df_charts.columns:
                df_charts["is_padronizado"] = df_charts["nomeCampo"].apply(_is_padronizado)
            
            fig_percentual_padronizacao = _create_fluxo_padronizacao_chart(df_charts)
            fig_contagem_servico_fluxo = _create_ranking_chart(df_charts)
            tabela_padronizacao = _create_padronizacao_tabela(df_charts)
            fig_hierarquia = _create_fluxos_hierarquia_tree(df_charts)  # Adicionar esta linha
            
            return str(qtd_servicos), str(qtd_fluxos), str(media_campos_fluxo), pct_fluxo_padronizado, fig_percentual_padronizacao, fig_contagem_servico_fluxo, tabela_padronizacao, fig_hierarquia
            
        except Exception as e:
            print(f"Erro ao atualizar gráficos de fluxos: {e}")
            import traceback
            traceback.print_exc()
            empty_fig = _create_empty_figure("Erro ao carregar dados")
            return "0", "0", "0", "0%", empty_fig, empty_fig, html.Div(f"Erro: {str(e)}"), empty_fig

def _create_fluxo_padronizacao_chart(df):
    """Gráfico de barras horizontais - Percentual de Padronização por Fluxo"""
    if 'fluxo' not in df.columns:
        return _create_empty_figure("Dados não disponíveis")
    
    try:
        # Verificar se is_padronizado existe, caso contrário calcular
        if 'is_padronizado' not in df.columns and 'nomeCampo' in df.columns:
            df["is_padronizado"] = df["nomeCampo"].apply(_is_padronizado)
        
        if 'is_padronizado' not in df.columns:
            return _create_empty_figure("Dados não disponíveis")
        
        # Calcular percentual de padronização por fluxo
        padronizacao = df.groupby('fluxo').agg(
            total_campos=('is_padronizado', 'count'),
            campos_padronizados=('is_padronizado', 'sum')
        ).reset_index()
        
        padronizacao['percent_padronizado'] = (padronizacao['campos_padronizados'] / padronizacao['total_campos'] * 100).round(1)
        padronizacao = padronizacao.sort_values('percent_padronizado', ascending=True).tail(20)
        
        # Criar gráfico de barras horizontais
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=padronizacao['fluxo'],
            x=padronizacao['percent_padronizado'],
            orientation='h',
            marker=dict(
                color=padronizacao['percent_padronizado'],
                colorscale=['#fee5d9', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15'],
                showscale=False,
                line=dict(color='#ffffff', width=1)
            ),
            text=[f"{val:.1f}%" for val in padronizacao['percent_padronizado']],
            textposition='outside',
            textfont=dict(color='#495057', size=12)
        ))
        
        fig.update_layout(
            template='plotly_white',
            height=450,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                title="% Padronização",
                showgrid=True,
                gridcolor='#e9ecef',
                tickfont=dict(color='#495057'),
                titlefont=dict(color='#495057'),
                range=[0, 105]
            ),
            yaxis=dict(
                title="Fluxo",
                showgrid=False,
                tickfont=dict(color='#495057'),
                titlefont=dict(color='#495057')
            ),
            showlegend=False,
            margin=dict(l=300, r=50, t=20, b=50)
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
        ranking = ranking.sort_values('contagem_servico', ascending=True).tail(20)  # ascending=True para barras horizontais (maior no topo)
        
        # Criar gráfico de barras horizontais
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=ranking['fluxo'],
            x=ranking['contagem_servico'],
            orientation='h',  # Barras horizontais
            marker=dict(
                color='#495057',
                line=dict(color='#ffffff', width=1)
            ),
            text=ranking['contagem_servico'],
            textposition='outside',
            textfont=dict(color='#495057', size=12)
        ))
        
        # Altura da tabela: header(50) + 15 linhas(48px cada) + footer(50) = 820px
        # Ajustar margens para que a altura visual seja igual à tabela
        fig.update_layout(
            template='plotly_white',
            height=820,  # Altura correspondente à tabela de padronização (50 + 15*48 + 50 = 820px)
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                title="Contagem de serviço",
                showgrid=True,
                gridcolor='#e9ecef',
                gridwidth=1,
                tickfont=dict(color='#495057'),
                titlefont=dict(color='#495057'),
                range=[0, ranking['contagem_servico'].max() * 1.15]  # Espaço para labels
            ),
            yaxis=dict(
                title="fluxo",
                showgrid=False,
                tickfont=dict(color='#495057', size=10),
                titlefont=dict(color='#495057')
            ),
            showlegend=False,
            margin=dict(l=300, r=80, t=50, b=50),  # Margem esquerda maior para nomes dos fluxos
            autosize=False
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
        
        # Marcar quais campos são padronizados usando a fórmula do PowerBI
        df_work["is_padronizado"] = df_work["nomeCampo"].apply(_is_padronizado)
        
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
        # Header com posição sticky
        header = html.Thead([
            html.Tr([
                html.Th("Fluxo", style={"backgroundColor": "#495057", "color": "white", "padding": "12px", "position": "sticky", "top": 0, "zIndex": 10}),
                html.Th("Campos do Formulário", style={"backgroundColor": "#495057", "color": "white", "padding": "12px", "position": "sticky", "top": 0, "zIndex": 10, "textAlign": "center"}),
                html.Th("Campos Padronizados", style={"backgroundColor": "#495057", "color": "white", "padding": "12px", "position": "sticky", "top": 0, "zIndex": 10, "textAlign": "center"}),
                html.Th("% Padronização do Fluxo", style={"backgroundColor": "#495057", "color": "white", "padding": "12px", "position": "sticky", "top": 0, "zIndex": 10, "textAlign": "center"})
            ])
        ], style={"position": "sticky", "top": 0, "zIndex": 10})
        
        # Body
        body_rows = []
        MAX_LINHAS_VISIVEIS = 15
        
        for idx, row in padronizacao_por_fluxo.iterrows():
            body_rows.append(
                html.Tr([
                    html.Td(str(row['Fluxo']), style={"padding": "10px", "border": "1px solid #dee2e6"}),
                    html.Td(str(int(row['Campos do Formulário'])), style={"padding": "10px", "border": "1px solid #dee2e6", "textAlign": "center"}),
                    html.Td(str(int(row['Campos Padronizados'])), style={"padding": "10px", "border": "1px solid #dee2e6", "textAlign": "center"}),
                    html.Td(f"{row['% Padronização do Fluxo']:.1f}%", style={"padding": "10px", "border": "1px solid #dee2e6", "textAlign": "center"})
                ], style={"backgroundColor": "#ffffff" if idx % 2 == 0 else "#f8f9fa"})
            )
        
        # Footer com total
        footer = html.Tfoot([
            html.Tr([
                html.Td("Total", style={"padding": "12px", "border": "1px solid #dee2e6", 
                      "backgroundColor": "#e9ecef", "fontWeight": "bold"}),
                html.Td(str(int(total_campos)), style={"padding": "12px", "border": "1px solid #dee2e6", 
                      "backgroundColor": "#e9ecef", "fontWeight": "bold", "textAlign": "center"}),
                html.Td(str(int(total_padronizados)), style={"padding": "12px", "border": "1px solid #dee2e6", 
                      "backgroundColor": "#e9ecef", "fontWeight": "bold", "textAlign": "center"}),
                html.Td(f"{pct_total:.1f}%", style={"padding": "12px", "border": "1px solid #dee2e6", 
                      "backgroundColor": "#e9ecef", "fontWeight": "bold", "textAlign": "center"})
            ])
        ])
        
        table = dbc.Table([
            header,
            html.Tbody(body_rows),
            footer
        ], bordered=True, hover=True, responsive=True, striped=False, 
        style={"marginBottom": 0, "fontSize": "14px", "width": "100%"})
        
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
                "borderRadius": "4px",
                "display": "block"
            }
        )
        
        return tabela_com_scroll
        
    except Exception as e:
        print(f"Erro ao criar tabela de padronização: {e}")
        import traceback
        traceback.print_exc()
        return html.Div(f"Erro ao criar tabela: {str(e)}", style={"padding": "20px", "color": "#dc3545"})

