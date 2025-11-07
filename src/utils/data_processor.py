"""
Módulo para processamento e enriquecimento de dados.
Centraliza toda a lógica de transformação de dados.
"""
import pandas as pd
from typing import Dict, Any, Optional

# Prefixos padronizados para identificação de campos
PADRAO_PREFIXOS = ["TXT_", "CBO_", "CHK_", "RAD_", "BTN_", "TAB_", "ICO_", 
                   "IMG_", "LBL_", "DAT_", "NUM_", "TEL_", "EML_", "URL_"]

def is_padronizado(nome_campo: str) -> int:
    """
    Verifica se um campo é padronizado baseado em prefixos.
    Adaptado da fórmula PowerBI.
    
    Padronizado = 1 se:
    - LEFT([nomeCampo], 3) IN {"TXT", "CBO", "RAD", "CHK"} OU
    - LEFT([nomeCampo], 5) IN {"CPF_", "CNP_", "CEP_", "TEL_", "EMA_"} OU
    - Começa com algum prefixo em PADRAO_PREFIXOS
    
    Args:
        nome_campo: Nome do campo
        
    Returns:
        1 se padronizado, 0 caso contrário
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
    
    # Verificar outros prefixos padronizados
    for prefixo in PADRAO_PREFIXOS:
        if nome_campo_str.startswith(prefixo):
            return 1
    
    return 0

def get_tipo_componente(nome_campo: str) -> str:
    """
    Determina o tipo de componente baseado no prefixo do nomeCampo.
    Adaptado da fórmula PowerBI Categorias_Campos1.
    
    Args:
        nome_campo: Nome do campo
        
    Returns:
        Tipo de componente identificado
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
        if prefixo_4 == "CPF_":
            return "CPF"
        elif prefixo_4 == "CNP_":
            return "CNPJ"
        elif prefixo_4 == "CEP_":
            return "CEP"
        elif prefixo_4 == "TEL_":
            return "Telefone"
        elif prefixo_4 == "EMA_":
            return "Email"
    
    # Mapeamento simplificado para outros casos
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
    
    for prefixo, tipo in tipo_componente_map.items():
        if nome_campo_str.startswith(prefixo):
            return tipo
    
    return "Outros/Sem Padrão"

def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriquece o DataFrame com colunas calculadas.
    
    Args:
        df: DataFrame original
        
    Returns:
        DataFrame enriquecido com colunas: is_padronizado, tipo_componente
    """
    if df.empty:
        return df
    
    df_enriched = df.copy()
    
    # Adicionar coluna is_padronizado se nomeCampo existir
    if 'nomeCampo' in df_enriched.columns:
        df_enriched['is_padronizado'] = df_enriched['nomeCampo'].apply(is_padronizado)
        df_enriched['tipo_componente'] = df_enriched['nomeCampo'].apply(get_tipo_componente)
    
    return df_enriched

def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula KPIs principais do DataFrame.
    
    Args:
        df: DataFrame processado
        
    Returns:
        Dicionário com KPIs calculados
    """
    kpis = {
        'qtd_fluxos': 0,
        'qtd_servicos': 0,
        'qtd_formularios': 0,
        'qtd_etapas': 0,
        'qtd_campos_distintos': 0,
        'qtd_campos_padronizados': 0,
        'pct_campos_padrao': "0%",
        'media_campos_fluxo': 0,
        'media_campos_formulario': 0,
        'pct_fluxo_padronizado': "0%"
    }
    
    if df.empty:
        return kpis
    
    # KPIs básicos
    if 'fluxo' in df.columns:
        kpis['qtd_fluxos'] = df['fluxo'].nunique()
        if 'nomeCampo' in df.columns:
            kpis['media_campos_fluxo'] = round(df.groupby('fluxo')['nomeCampo'].nunique().mean(), 2)
    
    if 'servico' in df.columns:
        kpis['qtd_servicos'] = df['servico'].nunique()
    
    if 'formulario' in df.columns:
        kpis['qtd_formularios'] = df['formulario'].nunique()
        if 'nomeCampo' in df.columns:
            kpis['media_campos_formulario'] = round(df.groupby('formulario')['nomeCampo'].nunique().mean(), 2)
    
    if 'etapa' in df.columns:
        kpis['qtd_etapas'] = df['etapa'].nunique()
    
    # KPIs de campos padronizados
    if 'nomeCampo' in df.columns:
        kpis['qtd_campos_distintos'] = df['nomeCampo'].nunique()
        
        if 'is_padronizado' in df.columns:
            kpis['qtd_campos_padronizados'] = df[df['is_padronizado'] == 1]['nomeCampo'].nunique()
            if kpis['qtd_campos_distintos'] > 0:
                pct = (kpis['qtd_campos_padronizados'] / kpis['qtd_campos_distintos']) * 100
                kpis['pct_campos_padrao'] = f"{pct:.2f}%"
    
    # Calcular percentual de padronização por fluxo (média)
    if 'fluxo' in df.columns and 'nomeCampo' in df.columns and 'is_padronizado' in df.columns:
        percentuais_fluxos = []
        for fluxo in df['fluxo'].unique():
            df_fluxo = df[df['fluxo'] == fluxo]
            total_campos_unicos = df_fluxo['nomeCampo'].nunique()
            
            if total_campos_unicos > 0:
                campos_padronizados_unicos = df_fluxo[df_fluxo['is_padronizado'] == 1]['nomeCampo'].nunique()
                pct_fluxo = (campos_padronizados_unicos / total_campos_unicos) * 100
                percentuais_fluxos.append(pct_fluxo)
        
        if percentuais_fluxos:
            pct_medio = sum(percentuais_fluxos) / len(percentuais_fluxos)
            kpis['pct_fluxo_padronizado'] = f"{pct_medio:.1f}%"
    
    return kpis

def calculate_padronizacao_por_fluxo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula percentual de padronização por fluxo.
    
    Args:
        df: DataFrame com coluna is_padronizado
        
    Returns:
        DataFrame com fluxo e percentual de padronização
    """
    if df.empty or 'fluxo' not in df.columns or 'is_padronizado' not in df.columns:
        return pd.DataFrame(columns=['fluxo', 'pct_padronizacao'])
    
    percentuais = []
    for fluxo in df['fluxo'].unique():
        df_fluxo = df[df['fluxo'] == fluxo]
        total_campos_unicos = df_fluxo['nomeCampo'].nunique()
        
        if total_campos_unicos > 0:
            campos_padronizados_unicos = df_fluxo[df_fluxo['is_padronizado'] == 1]['nomeCampo'].nunique()
            pct = (campos_padronizados_unicos / total_campos_unicos) * 100
            percentuais.append({'fluxo': fluxo, 'pct_padronizacao': pct})
    
    return pd.DataFrame(percentuais)

def prepare_chart_data(df: pd.DataFrame, max_rows: int = 50000) -> pd.DataFrame:
    """
    Prepara dados para gráficos (amostragem se necessário).
    
    Args:
        df: DataFrame processado
        max_rows: Número máximo de linhas para gráficos
        
    Returns:
        DataFrame preparado para gráficos
    """
    if df.empty:
        return df
    
    if len(df) > max_rows:
        return df.sample(n=max_rows, random_state=42)
    
    return df

