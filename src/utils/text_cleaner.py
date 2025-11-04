# src/utils/text_cleaner.py
"""
Utilitários para limpeza e normalização de texto com problemas de encoding
"""
import re
import unicodedata
import pandas as pd

def fix_encoding_issues(text):
    """
    Corrige problemas comuns de encoding em português.
    
    Args:
        text: String com possível problema de encoding
        
    Returns:
        String corrigida
    """
    if pd.isna(text) or text is None:
        return text
    
    text = str(text)
    
    # Dicionário de correções comuns de encoding português
    encoding_fixes = {
        # Problemas comuns de encoding português
        'Ã£o': 'ão',
        'Ã£O': 'ÃO',
        'Ã£': 'ã',
        'Ã ': 'á',
        'Ã¡': 'á',
        'Ã©': 'é',
        'Ãª': 'ê',
        'Ã³': 'ó',
        'Ã´': 'ô',
        'Ãµ': 'õ',
        'Ãº': 'ú',
        'Ã§': 'ç',
        'Ã€': 'À',
        'Ã‰': 'É',
        'Ã"': 'Ó',
        'Ã•': 'Õ',
        'Ãš': 'Ú',
        'Ã‡': 'Ç',
        # Casos específicos encontrados
        'ÃONCIA': 'ÊNCIA',
        'ÃODICA': 'ÉDICA',
        'Ã Ã O': 'ÇÃO',
        'ÃOO': 'ÃO',
        'Ã Ã_O': 'ÇÃO',
        'Ã DICA': 'ÉDICA',
        # Duplicações
        'ÃOÃO': 'ÇÃO',
        'ÃOVEL': 'ÓVEL',
        # Espaços problemáticos
        'Ã Ã': 'Ã',
        'Ã Ã': 'Ã',
    }
    
    # Mapeamento direto de caracteres problemáticos para corretos
    # Isso corrige problemas onde latin1 foi interpretado como utf-8
    # IMPORTANTE: Não substituir 'Ã' isoladamente, pois pode fazer parte de padrões maiores
    char_replacements = {
        # Caracteres acentuados comuns
        'Ã£': 'ã', 'Ã¡': 'á', 'Ã©': 'é', 'Ãª': 'ê', 'Ã­': 'í',
        'Ã³': 'ó', 'Ã´': 'ô', 'Ãµ': 'õ', 'Ãº': 'ú', 'Ã§': 'ç',
        'Ã€': 'À', 'Ã‰': 'É', 'Ã"': 'Ó', 'Ã•': 'Õ',
        'Ãš': 'Ú', 'Ã‡': 'Ç',
        # Casos específicos de duplicação ou combinação
        'Ã£o': 'ão', 'Ã£O': 'ÃO',
    }
    
    # Aplicar substituições de caracteres primeiro (exceto 'Ã' isolado)
    for wrong_char, correct_char in char_replacements.items():
        text = text.replace(wrong_char, correct_char)
    
    # Ordem importante: corrigir padrões mais específicos primeiro
    # Corrigir padrões com múltiplos caracteres problemáticos
    text = text.replace('ÃOÃO', 'ÇÃO')
    text = text.replace('ÃONCIA', 'ÊNCIA')
    text = text.replace('ÃODICA', 'ÉDICA')
    text = text.replace('ÃOVEL', 'ÓVEL')
    
    # Corrigir padrões com espaços
    text = text.replace('Ã Ã O', 'ÇÃO')
    text = text.replace('Ã Ã_O', 'ÇÃO')
    text = text.replace('Ã Ã', 'Ã')
    text = text.replace('Ã DICA', 'ÉDICA')
    text = text.replace('ÃOO', 'ÃO')
    
    # Corrigir padrões específicos encontrados nos dados (ordem específica primeiro)
    # Padrões com "ÃO" duplicado ou malformado
    text = text.replace('SOLICITAÃOÃO', 'SOLICITAÇÃO')
    text = text.replace('REQUISIÃOÃO', 'REQUISIÇÃO')
    text = text.replace('INSCRIÃOÃO', 'INSCRIÇÃO')
    text = text.replace('AUTORIZAÃOÃO', 'AUTORIZAÇÃO')
    text = text.replace('OCORRÃONCIA', 'OCORRÊNCIA')
    text = text.replace('CONSULTA_MÃODICA', 'CONSULTA_MÉDICA')
    text = text.replace('CONSULTA MÃODICA', 'CONSULTA MÉDICA')
    text = text.replace('IMÃOVEL', 'IMÓVEL')
    text = text.replace('EVENTO_PÃOBLICO', 'EVENTO_PÚBLICO')
    text = text.replace('EVENTO PÃOBLICO', 'EVENTO PÚBLICO')
    text = text.replace('SERVIÃO', 'SERVIÇO')
    text = text.replace('ALVARA', 'ALVARÁ')
    
    # Corrigir "CIDADÃO" e variações (ordem importante: mais específico primeiro)
    text = text.replace('CIDADÃOÃO', 'CIDADÃO')
    text = text.replace('CIDADÃÃO', 'CIDADÃO')
    text = text.replace('CIDADÃ O', 'CIDADÃO')
    text = text.replace('CIDADÃ_O', 'CIDADÃO')
    
    # Corrigir padrões em fluxos (FLX_)
    if text.startswith('FLX_'):
        text = text.replace('FLX_SOLICITAÃ Ã O_DE_VAGA_ESCOLAR', 'FLX_SOLICITAÇÃO_DE_VAGA_ESCOLAR')
        # Corrigir CIDADÃO em diferentes variações de encoding
        text = text.replace('FLX_SERVIÃO_DE_ATENDIMENTO_AO_CIDADÃOÃO', 'FLX_SERVIÇO_DE_ATENDIMENTO_AO_CIDADÃO')
        text = text.replace('FLX_SERVIÃO_DE_ATENDIMENTO_AO_CIDADÃÃO', 'FLX_SERVIÇO_DE_ATENDIMENTO_AO_CIDADÃO')
        text = text.replace('FLX_SERVIÃO_DE_ATENDIMENTO_AO_CIDADÃO', 'FLX_SERVIÇO_DE_ATENDIMENTO_AO_CIDADÃO')
        text = text.replace('FLX_SERVIÃO_DE_ATENDIMENTO_AO_CIDADÃ O', 'FLX_SERVIÇO_DE_ATENDIMENTO_AO_CIDADÃO')
        text = text.replace('FLX_SERVIÃO_DE_ATENDIMENTO_AO_CIDADÃ_O', 'FLX_SERVIÇO_DE_ATENDIMENTO_AO_CIDADÃO')
        text = text.replace('FLX_REQUISIÃOÃO_DE_DOCUMENTOS', 'FLX_REQUISIÇÃO_DE_DOCUMENTOS')
        text = text.replace('FLX_REGISTRO_DE_OCORRÃONCIA', 'FLX_REGISTRO_DE_OCORRÊNCIA')
        text = text.replace('FLX_INSCRIÃ Ã O_EM_PROGRAMA_SOCIAL', 'FLX_INSCRIÇÃO_EM_PROGRAMA_SOCIAL')
        text = text.replace('FLX_EMISSÃOO_DE_GUIA_DE_PAGAMENTO', 'FLX_EMISSÃO_DE_GUIA_DE_PAGAMENTO')
        text = text.replace('FLX_CERTIDÃO_DE_IMÃOVEL', 'FLX_CERTIDÃO_DE_IMÓVEL')
        text = text.replace('FLX_CADASTRO_DE_CARTA_DE_SERVIÃO', 'FLX_CADASTRO_DE_CARTA_DE_SERVIÇO')
        text = text.replace('FLX_AUTORIZAÃ Ã_O_DE_EVENTO_PÃOBLICO', 'FLX_AUTORIZAÇÃO_DE_EVENTO_PÚBLICO')
        text = text.replace('FLX_ALVARA_DE_FUNCIONAMENTO', 'FLX_ALVARÁ_DE_FUNCIONAMENTO')
        text = text.replace('FLX_AGENDAMENTO_DE_CONSULTA_MÃ DICA', 'FLX_AGENDAMENTO_DE_CONSULTA_MÉDICA')
    
    # Aplicar outras correções do dicionário
    for wrong, correct in encoding_fixes.items():
        if wrong in text and wrong not in ['Ã', 'ÃOÃO', 'ÃONCIA', 'ÃODICA', 'ÃOVEL', 'Ã Ã O', 'Ã Ã_O', 'Ã DICA', 'ÃOO', 'ALVARA']:
            text = text.replace(wrong, correct)
    
    # Limpar espaços múltiplos e caracteres estranhos
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remover caracteres não imprimíveis
    text = ''.join(char for char in text if char.isprintable() or char in ['\n', '\t'])
    
    return text


def clean_dataframe_text_columns(df, columns=None):
    """
    Limpa colunas de texto de um DataFrame aplicando correções de encoding.
    
    Args:
        df: DataFrame para limpar
        columns: Lista de colunas para limpar. Se None, limpa todas as colunas de texto
        
    Returns:
        DataFrame com texto limpo
    """
    if df.empty:
        return df
    
    df_clean = df.copy()
    
    # Identificar colunas de texto
    if columns is None:
        text_columns = df_clean.select_dtypes(include=['object']).columns.tolist()
    else:
        text_columns = [col for col in columns if col in df_clean.columns]
    
    # Colunas específicas que sabemos que contêm texto
    text_fields = ['servico', 'fluxo', 'formulario', 'etapa', 'executor', 
                   'nomeCampo', 'legenda', 'valor', 'beneficiario', 'nomeCampoFilho',
                   'legendaCampoFilho', 'valorDominio']
    
    # Adicionar colunas específicas se existirem
    for col in text_fields:
        if col in df_clean.columns and col not in text_columns:
            text_columns.append(col)
    
    print(f"Limpando {len(text_columns)} colunas de texto...")
    
    # Aplicar limpeza em cada coluna
    for col in text_columns:
        if col in df_clean.columns:
            try:
                df_clean[col] = df_clean[col].apply(fix_encoding_issues)
            except Exception as e:
                print(f"Aviso: Erro ao limpar coluna {col}: {e}")
    
    return df_clean

