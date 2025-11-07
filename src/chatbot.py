# =============================================================================
# src/chatbot.py - Chatbot Inteligente com OpenAI e Análise de Dados CSV
# =============================================================================
# Este módulo implementa um chatbot especializado em governança de dados que:
# - Integra com OpenAI API para respostas inteligentes
# - Analisa dados do CSV em tempo real
# - Mantém contexto e memória por sessão
# - Fornece respostas específicas sobre formulários, fluxos e campos
# =============================================================================

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

# Importações para análise de dados
import pandas as pd

# Importações para OpenAI
from openai import OpenAI
from dotenv import load_dotenv

# Importações do projeto para acesso aos dados
from src.utils.data_cache import load_data_once, get_filtered_data

# =============================================================================
# CONFIGURAÇÃO E INICIALIZAÇÃO
# =============================================================================

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração de logging para debug
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Inicializa cliente OpenAI se a chave estiver disponível
# Se não houver chave, o sistema usará fallback (modo sem OpenAI)
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key) if openai_api_key else None

if not client:
    logger.warning("⚠️ OpenAI API Key não configurada. Sistema funcionará em modo fallback.")

# Memória de contexto por sessão (armazena histórico de conversas)
# Estrutura: {session_id: [lista de mensagens]}
contexto_sessoes: Dict[str, List[Dict]] = {}

# Caminho do arquivo CSV com os dados
CSV_PATH = "data/meu_arquivo.csv"

# Limite máximo de mensagens no histórico por sessão
MAX_HISTORICO_MENSAGENS = 20

# =============================================================================
# FUNÇÕES DE ANÁLISE DE DADOS
# =============================================================================

def analisar_dados_csv() -> Dict:
    """
    Analisa os dados do CSV para fornecer estatísticas detalhadas ao chatbot.
    
    Esta função realiza uma análise profunda:
    - Estatísticas gerais e métricas
    - Relacionamentos entre formulários, campos e fluxos
    - Análise de uso e frequência
    - Estatísticas de tempo e performance
    - Distribuição de dados
    
    Returns:
        Dict: Dicionário completo com estatísticas e análises dos dados
    """
    try:
        # Carrega o DataFrame completo usando o cache
        df = load_data_once(CSV_PATH)
        
        # Verifica se o DataFrame está vazio
        if df.empty:
            logger.warning("DataFrame vazio ao analisar dados CSV")
            return {}
        
        # =====================================================================
        # ESTATÍSTICAS GERAIS
        # =====================================================================
        total_formularios = df['formulario'].nunique() if 'formulario' in df.columns else 0
        total_campos = df['nomeCampo'].nunique() if 'nomeCampo' in df.columns else 0
        total_fluxos = df['fluxo'].nunique() if 'fluxo' in df.columns else 0
        total_servicos = df['servico'].nunique() if 'servico' in df.columns else 0
        total_registros = len(df)
        
        # =====================================================================
        # ANÁLISES DE USO E FREQUÊNCIA
        # =====================================================================
        # Formulários mais usados com detalhes
        formularios_mais_usados = {}
        formularios_detalhes = {}
        if 'formulario' in df.columns:
            formularios_group = df.groupby('formulario')
            formularios_mais_usados = (
                formularios_group.size()
                .sort_values(ascending=False)
                .head(10)
                .to_dict()
            )
            # Detalhes: campos por formulário
            for form in formularios_mais_usados.keys():
                campos_no_form = df[df['formulario'] == form]['nomeCampo'].nunique()
                formularios_detalhes[form] = {
                    'uso': formularios_mais_usados[form],
                    'campos': campos_no_form
                }
        
        # Campos mais comuns com detalhes
        campos_mais_comuns = {}
        campos_detalhes = {}
        if 'nomeCampo' in df.columns:
            campos_group = df.groupby('nomeCampo')
            campos_mais_comuns = (
                campos_group.size()
                .sort_values(ascending=False)
                .head(10)
                .to_dict()
            )
            # Detalhes: em quantos formulários cada campo aparece
            for campo in campos_mais_comuns.keys():
                formularios_com_campo = df[df['nomeCampo'] == campo]['formulario'].nunique()
                campos_detalhes[campo] = {
                    'uso': campos_mais_comuns[campo],
                    'formularios': formularios_com_campo
                }
        
        # Fluxos mais ativos com detalhes
        fluxos_mais_ativos = {}
        fluxos_detalhes = {}
        if 'fluxo' in df.columns:
            fluxos_group = df.groupby('fluxo')
            fluxos_mais_ativos = (
                fluxos_group.size()
                .sort_values(ascending=False)
                .head(10)
                .to_dict()
            )
            # Detalhes: formulários por fluxo
            for fluxo in fluxos_mais_ativos.keys():
                formularios_no_fluxo = df[df['fluxo'] == fluxo]['formulario'].nunique()
                fluxos_detalhes[fluxo] = {
                    'uso': fluxos_mais_ativos[fluxo],
                    'formularios': formularios_no_fluxo
                }
        
        # Serviços mais utilizados
        servicos_mais_usados = {}
        if 'servico' in df.columns:
            servicos_mais_usados = (
                df.groupby('servico')
                .size()
                .sort_values(ascending=False)
                .head(10)
                .to_dict()
            )
        
        # =====================================================================
        # MÉTRICAS E CÁLCULOS AVANÇADOS
        # =====================================================================
        # Média de campos por formulário
        media_campos_por_formulario = 0
        if total_formularios > 0 and 'formulario' in df.columns and 'nomeCampo' in df.columns:
            campos_por_form = df.groupby('formulario')['nomeCampo'].nunique()
            media_campos_por_formulario = round(campos_por_form.mean(), 2)
        
        # Média de formulários por fluxo
        media_formularios_por_fluxo = 0
        if total_fluxos > 0 and 'fluxo' in df.columns and 'formulario' in df.columns:
            forms_por_fluxo = df.groupby('fluxo')['formulario'].nunique()
            media_formularios_por_fluxo = round(forms_por_fluxo.mean(), 2)
        
        # =====================================================================
        # ANÁLISE DE TEMPO E PERFORMANCE (se disponível)
        # =====================================================================
        tempo_medio = None
        tempo_medio_inicio_fim = None
        if 'tempoTotal' in df.columns:
            tempo_medio = round(df['tempoTotal'].mean(), 2) if not df['tempoTotal'].isna().all() else None
        if 'tempoInicioFim' in df.columns:
            tempo_medio_inicio_fim = round(df['tempoInicioFim'].mean(), 2) if not df['tempoInicioFim'].isna().all() else None
        
        # =====================================================================
        # ANÁLISE DE STATUS (se disponível)
        # =====================================================================
        status_distribuicao = {}
        if 'status' in df.columns:
            status_distribuicao = df['status'].value_counts().to_dict()
        
        # =====================================================================
        # RELACIONAMENTOS E CORRELAÇÕES
        # =====================================================================
        # Formulário com mais campos
        formulario_mais_campos = None
        max_campos = 0
        if 'formulario' in df.columns and 'nomeCampo' in df.columns:
            campos_por_form = df.groupby('formulario')['nomeCampo'].nunique()
            if not campos_por_form.empty:
                formulario_mais_campos = campos_por_form.idxmax()
                max_campos = int(campos_por_form.max())
        
        # Retorna dicionário completo com todas as análises
        return {
            "total_formularios": total_formularios,
            "total_campos": total_campos,
            "total_fluxos": total_fluxos,
            "total_servicos": total_servicos,
            "total_registros": total_registros,
            "media_campos_por_formulario": media_campos_por_formulario,
            "media_formularios_por_fluxo": media_formularios_por_fluxo,
            "formularios_mais_usados": formularios_mais_usados,
            "formularios_detalhes": formularios_detalhes,
            "campos_mais_comuns": campos_mais_comuns,
            "campos_detalhes": campos_detalhes,
            "fluxos_mais_ativos": fluxos_mais_ativos,
            "fluxos_detalhes": fluxos_detalhes,
            "servicos_mais_usados": servicos_mais_usados,
            "tempo_medio": tempo_medio,
            "tempo_medio_inicio_fim": tempo_medio_inicio_fim,
            "status_distribuicao": status_distribuicao,
            "formulario_mais_campos": formulario_mais_campos,
            "max_campos_no_formulario": max_campos
        }
        
    except Exception as e:
        logger.error(f"Erro ao analisar dados CSV: {e}")
        return {}


def buscar_dados_especificos(pergunta: str, analise_dados: Optional[Dict] = None) -> Optional[str]:
    """
    Busca informações específicas nos dados baseado na pergunta do usuário.
    
    Esta função realiza busca inteligente:
    - Busca por nome exato de formulários, campos, fluxos
    - Busca parcial (contains)
    - Retorna informações detalhadas quando encontra
    - Usa análise de dados para contexto adicional
    
    Args:
        pergunta: Texto da pergunta do usuário
        analise_dados: Dicionário opcional com análises já calculadas (para performance)
        
    Returns:
        Optional[str]: Resposta formatada com dados encontrados ou None
    """
    try:
        # Carrega o DataFrame
        df = load_data_once(CSV_PATH)
        
        if df.empty:
            return None
        
        # Converte pergunta para minúsculas para busca case-insensitive
        pergunta_lower = pergunta.lower()
        
        # Se não recebeu análise, calcula rapidamente
        if analise_dados is None:
            analise_dados = analisar_dados_csv()
        
        # =====================================================================
        # BUSCA POR NOME ESPECÍFICO DE FORMULÁRIO
        # =====================================================================
        if 'formulario' in pergunta_lower or 'formulário' in pergunta_lower:
            if 'formulario' in df.columns:
                # Busca por nome exato ou parcial
                formularios_disponiveis = df['formulario'].unique().tolist()
                
                # Tenta encontrar correspondência exata ou parcial
                formulario_encontrado = None
                for form in formularios_disponiveis:
                    if form.lower() in pergunta_lower or pergunta_lower in form.lower():
                        formulario_encontrado = form
                        break
                
                if formulario_encontrado:
                    # Retorna detalhes específicos do formulário
                    detalhes = analise_dados.get('formularios_detalhes', {}).get(formulario_encontrado, {})
                    campos = detalhes.get('campos', df[df['formulario'] == formulario_encontrado]['nomeCampo'].nunique())
                    uso = detalhes.get('uso', len(df[df['formulario'] == formulario_encontrado]))
                    
                    return (
                        f"Formulário '{formulario_encontrado}': "
                        f"usado {uso} vezes, contém {campos} campos únicos."
                    )
                else:
                    # Lista todos os formulários se não encontrou específico
                    total = len(formularios_disponiveis)
                    principais = ', '.join(formularios_disponiveis[:5])
                    return f"Encontrei {total} formulário(s). Principais: {principais}"
        
        # =====================================================================
        # BUSCA POR NOME ESPECÍFICO DE CAMPO
        # =====================================================================
        if 'campo' in pergunta_lower:
            if 'nomeCampo' in df.columns:
                campos_disponiveis = df['nomeCampo'].dropna().unique().tolist()
                
                # Busca por nome exato ou parcial
                campo_encontrado = None
                for campo in campos_disponiveis:
                    if str(campo).lower() in pergunta_lower or pergunta_lower in str(campo).lower():
                        campo_encontrado = campo
                        break
                
                if campo_encontrado:
                    # Retorna detalhes específicos do campo
                    detalhes = analise_dados.get('campos_detalhes', {}).get(campo_encontrado, {})
                    formularios = detalhes.get('formularios', df[df['nomeCampo'] == campo_encontrado]['formulario'].nunique())
                    uso = detalhes.get('uso', len(df[df['nomeCampo'] == campo_encontrado]))
                    
                    return (
                        f"Campo '{campo_encontrado}': "
                        f"usado {uso} vezes, aparece em {formularios} formulário(s)."
                    )
                else:
                    total = len(campos_disponiveis)
                    principais = ', '.join([str(c) for c in campos_disponiveis[:5]])
                    return f"Encontrei {total} campo(s) único(s). Principais: {principais}"
        
        # =====================================================================
        # BUSCA POR NOME ESPECÍFICO DE FLUXO
        # =====================================================================
        if 'fluxo' in pergunta_lower:
            if 'fluxo' in df.columns:
                fluxos_disponiveis = df['fluxo'].dropna().unique().tolist()
                
                # Busca por nome exato ou parcial
                fluxo_encontrado = None
                for fluxo in fluxos_disponiveis:
                    if str(fluxo).lower() in pergunta_lower or pergunta_lower in str(fluxo).lower():
                        fluxo_encontrado = fluxo
                        break
                
                if fluxo_encontrado:
                    # Retorna detalhes específicos do fluxo
                    detalhes = analise_dados.get('fluxos_detalhes', {}).get(fluxo_encontrado, {})
                    formularios = detalhes.get('formularios', df[df['fluxo'] == fluxo_encontrado]['formulario'].nunique())
                    uso = detalhes.get('uso', len(df[df['fluxo'] == fluxo_encontrado]))
                    
                    return (
                        f"Fluxo '{fluxo_encontrado}': "
                        f"usado {uso} vezes, utiliza {formularios} formulário(s)."
                    )
                else:
                    total = len(fluxos_disponiveis)
                    principais = ', '.join([str(f) for f in fluxos_disponiveis[:5]])
                    return f"Encontrei {total} fluxo(s). Principais: {principais}"
        
        # =====================================================================
        # BUSCA POR SERVIÇOS
        # =====================================================================
        if 'servico' in pergunta_lower or 'serviço' in pergunta_lower:
            if 'servico' in df.columns:
                servicos_disponiveis = df['servico'].dropna().unique().tolist()
                total = len(servicos_disponiveis)
                principais = ', '.join([str(s) for s in servicos_disponiveis[:5]])
                return f"Encontrei {total} serviço(s). Principais: {principais}"
        
        return None
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados específicos: {e}")
        return None


# =============================================================================
# FUNÇÕES DE CONTEXTO E MEMÓRIA
# =============================================================================

def criar_contexto_sistema(analise_dados: Dict) -> str:
    """
    Cria um contexto detalhado e preciso para o OpenAI baseado nos dados analisados.
    
    Este contexto fornece informações completas sobre:
    - Estatísticas detalhadas do sistema
    - Formulários, campos e fluxos principais com detalhes
    - Relacionamentos entre dados
    - Métricas de performance
    - Instruções específicas para respostas precisas
    
    Args:
        analise_dados: Dicionário completo com estatísticas e análises
        
    Returns:
        str: Texto do contexto do sistema formatado e detalhado
    """
    contexto = f"""Você é um assistente especializado em Governança de Dados do Painel de Governança - Santos.

================================================================================
ESTATÍSTICAS GERAIS DO SISTEMA:
================================================================================
- Total de Registros: {analise_dados.get('total_registros', 0)}
- Total de Formulários Únicos: {analise_dados.get('total_formularios', 0)}
- Total de Campos Únicos: {analise_dados.get('total_campos', 0)}
- Total de Fluxos de Trabalho: {analise_dados.get('total_fluxos', 0)}
- Total de Serviços: {analise_dados.get('total_servicos', 0)}
- Média de Campos por Formulário: {analise_dados.get('media_campos_por_formulario', 0)}
- Média de Formulários por Fluxo: {analise_dados.get('media_formularios_por_fluxo', 0)}

================================================================================
FORMULÁRIOS MAIS UTILIZADOS (Top 10):
================================================================================
"""
    # Adiciona formulários com detalhes
    formularios_detalhes = analise_dados.get('formularios_detalhes', {})
    formularios_mais_usados = analise_dados.get('formularios_mais_usados', {})
    
    if formularios_mais_usados:
        for i, (formulario, uso) in enumerate(list(formularios_mais_usados.items())[:10], 1):
            detalhes = formularios_detalhes.get(formulario, {})
            campos = detalhes.get('campos', 'N/A')
            contexto += f"{i}. {formulario}\n"
            contexto += f"   - Usado: {uso} vezes\n"
            contexto += f"   - Campos únicos: {campos}\n\n"
    else:
        contexto += "Nenhum dado disponível\n\n"
    
    contexto += "================================================================================\n"
    contexto += "CAMPOS MAIS COMUNS (Top 10):\n"
    contexto += "================================================================================\n"
    
    # Adiciona campos com detalhes
    campos_detalhes = analise_dados.get('campos_detalhes', {})
    campos_mais_comuns = analise_dados.get('campos_mais_comuns', {})
    
    if campos_mais_comuns:
        for i, (campo, uso) in enumerate(list(campos_mais_comuns.items())[:10], 1):
            detalhes = campos_detalhes.get(campo, {})
            formularios = detalhes.get('formularios', 'N/A')
            contexto += f"{i}. {campo}\n"
            contexto += f"   - Ocorrências: {uso}\n"
            contexto += f"   - Aparece em: {formularios} formulário(s)\n\n"
    else:
        contexto += "Nenhum dado disponível\n\n"
    
    contexto += "================================================================================\n"
    contexto += "FLUXOS MAIS ATIVOS (Top 10):\n"
    contexto += "================================================================================\n"
    
    # Adiciona fluxos com detalhes
    fluxos_detalhes = analise_dados.get('fluxos_detalhes', {})
    fluxos_mais_ativos = analise_dados.get('fluxos_mais_ativos', {})
    
    if fluxos_mais_ativos:
        for i, (fluxo, uso) in enumerate(list(fluxos_mais_ativos.items())[:10], 1):
            detalhes = fluxos_detalhes.get(fluxo, {})
            formularios = detalhes.get('formularios', 'N/A')
            contexto += f"{i}. {fluxo}\n"
            contexto += f"   - Ocorrências: {uso}\n"
            contexto += f"   - Formulários utilizados: {formularios}\n\n"
    else:
        contexto += "Nenhum dado disponível\n\n"
    
    # Adiciona informações sobre formulário com mais campos
    if analise_dados.get('formulario_mais_campos'):
        contexto += "================================================================================\n"
        contexto += "DESTAQUES:\n"
        contexto += "================================================================================\n"
        contexto += f"Formulário com mais campos: {analise_dados.get('formulario_mais_campos')}\n"
        contexto += f"Total de campos: {analise_dados.get('max_campos_no_formulario', 0)}\n\n"
    
    # Adiciona métricas de tempo se disponíveis
    if analise_dados.get('tempo_medio'):
        contexto += "================================================================================\n"
        contexto += "MÉTRICAS DE PERFORMANCE:\n"
        contexto += "================================================================================\n"
        contexto += f"Tempo médio total: {analise_dados.get('tempo_medio')} unidades\n"
        if analise_dados.get('tempo_medio_inicio_fim'):
            contexto += f"Tempo médio início-fim: {analise_dados.get('tempo_medio_inicio_fim')} unidades\n"
        contexto += "\n"
    
    contexto += """================================================================================
FUNCIONALIDADES DO DASHBOARD:
================================================================================
1. Visão Geral: Análise geral de formulários, fluxos e campos com KPIs
2. Fluxos/Serviços: Análise detalhada de fluxos de trabalho e serviços
3. Formulários: Análise de formulários, seus campos e uso em fluxos
4. Campos: Análise detalhada de campos individuais e sua distribuição

================================================================================
INSTRUÇÕES CRÍTICAS PARA RESPOSTAS PRECISAS:
================================================================================
1. SEMPRE use os dados reais fornecidos acima quando responder perguntas
2. Se perguntarem sobre números específicos, use EXATAMENTE os valores dos dados
3. Quando mencionar formulários, campos ou fluxos, cite os nomes EXATOS dos dados
4. Forneça análises baseadas nos relacionamentos entre dados (ex: qual formulário tem mais campos)
5. Se não souber algo específico, seja honesto e diga que não tem essa informação
6. Use linguagem clara, profissional e técnica apropriada para governança de dados
7. Para perguntas sobre métricas, sempre cite os números exatos fornecidos
8. Relacione informações quando relevante (ex: "O formulário X tem Y campos e aparece em Z fluxos")
9. Se perguntarem sobre "quantos", "qual", "quais", use os dados reais da análise
10. Mantenha foco em governança de dados, qualidade, compliance e eficiência

================================================================================
EXEMPLOS DE RESPOSTAS PRECISAS:
================================================================================
- "Quantos formulários temos?" → Use o número exato de total_formularios
- "Qual formulário tem mais campos?" → Cite o formulario_mais_campos com o número exato
- "Quais são os formulários mais usados?" → Liste os formulários mais usados com seus números de uso
- "Quantos campos tem o formulário X?" → Use os dados de formularios_detalhes

IMPORTANTE: Sua precisão depende de usar os dados fornecidos acima. Sempre verifique os dados antes de responder.
"""
    
    return contexto


def limpar_contexto(session_id: str = "default"):
    """
    Limpa o histórico de contexto de uma sessão específica.
    
    Útil para reiniciar uma conversa ou limpar memória.
    
    Args:
        session_id: ID da sessão a ser limpa
    """
    if session_id in contexto_sessoes:
        del contexto_sessoes[session_id]
        logger.info(f"Contexto limpo para sessão: {session_id}")


# =============================================================================
# FUNÇÃO PRINCIPAL - GERAÇÃO DE RESPOSTAS
# =============================================================================

def gerar_resposta(mensagem: str, session_id: str = "default") -> str:
    """
    Função principal que gera resposta do chatbot usando OpenAI com contexto.
    
    Fluxo de execução:
    1. Valida a mensagem de entrada
    2. Analisa os dados do CSV para obter estatísticas
    3. Busca dados específicos relacionados à pergunta
    4. Cria contexto do sistema com informações relevantes
    5. Mantém histórico de conversa por sessão
    6. Chama OpenAI API para gerar resposta inteligente
    7. Atualiza histórico com nova conversa
    
    Se OpenAI não estiver disponível, usa modo fallback com respostas básicas.
    
    Args:
        mensagem: Mensagem do usuário
        session_id: ID da sessão para manter contexto (padrão: "default")
        
    Returns:
        str: Resposta do chatbot
    """
    # =========================================================================
    # VALIDAÇÃO DE ENTRADA
    # =========================================================================
    if not mensagem or mensagem.strip() == "":
        return "Por favor, digite uma mensagem válida."
    
    # Remove espaços em branco
    mensagem = mensagem.strip()
    
    # =========================================================================
    # VERIFICAÇÃO DE OPENAI
    # =========================================================================
    # Se OpenAI não estiver configurado, usa modo fallback
    if not client:
        logger.info("OpenAI não disponível, usando modo fallback")
        return gerar_resposta_fallback(mensagem)
    
    try:
        # =====================================================================
        # ANÁLISE DE DADOS
        # =====================================================================
        # Analisa dados do CSV para obter estatísticas
        logger.info(f"Analisando dados CSV para sessão: {session_id}")
        analise_dados = analisar_dados_csv()
        
        # Busca dados específicos relacionados à pergunta (passa análise para evitar recalcular)
        dados_especificos = buscar_dados_especificos(mensagem, analise_dados)
        
        # =====================================================================
        # PREPARAÇÃO DO CONTEXTO
        # =====================================================================
        # Cria contexto do sistema com informações do dashboard
        contexto_sistema = criar_contexto_sistema(analise_dados)
        
        # Inicializa histórico da sessão se não existir
        if session_id not in contexto_sessoes:
            contexto_sessoes[session_id] = []
            logger.info(f"Nova sessão criada: {session_id}")
        
        # Obtém histórico atual (últimas mensagens)
        historico = contexto_sessoes[session_id].copy()
        
        # =====================================================================
        # PREPARAÇÃO DAS MENSAGENS PARA OPENAI
        # =====================================================================
        # Estrutura de mensagens para OpenAI:
        # - system: Contexto do sistema e instruções
        # - user: Mensagens do usuário
        # - assistant: Respostas anteriores do assistente
        
        mensagens = [
            {"role": "system", "content": contexto_sistema}
        ]
        
        # Adiciona histórico recente (últimas 10 interações para não exceder limites)
        # Isso mantém contexto da conversa sem sobrecarregar o modelo
        for item in historico[-10:]:
            mensagens.append(item)
        
        # Adiciona dados específicos encontrados como contexto adicional
        if dados_especificos:
            mensagens.append({
                "role": "system",
                "content": f"DADOS ESPECÍFICOS ENCONTRADOS: {dados_especificos}"
            })
        
        # Adiciona mensagem atual do usuário
        mensagens.append({"role": "user", "content": mensagem})
        
        # =====================================================================
        # CHAMADA À API OPENAI
        # =====================================================================
        logger.info(f"Chamando OpenAI API para sessão: {session_id}")
        
        # =====================================================================
        # PARÂMETROS OTIMIZADOS PARA PRECISÃO
        # =====================================================================
        # Modelo: gpt-4o-mini é mais preciso e econômico que gpt-3.5-turbo
        # Temperature: 0.3 para respostas mais precisas e determinísticas
        # Max tokens: 800 para permitir respostas mais completas quando necessário
        # Top_p: 0.9 para foco em tokens mais prováveis (maior precisão)
        
        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-4o-mini"),  # Permite configurar via .env
            messages=mensagens,
            temperature=float(os.getenv("TEMPERATURE", "0.3")),  # Mais preciso (0.3 vs 0.7)
            max_tokens=int(os.getenv("MAX_TOKENS", "800")),  # Mais tokens para respostas completas
            top_p=0.9,  # Foco em tokens mais prováveis para maior precisão
            frequency_penalty=0.1,  # Reduz repetição
            presence_penalty=0.1  # Incentiva variedade quando necessário
        )
        
        # Extrai a resposta gerada
        resposta = response.choices[0].message.content
        
        # =====================================================================
        # ATUALIZAÇÃO DO HISTÓRICO
        # =====================================================================
        # Adiciona mensagem do usuário ao histórico
        contexto_sessoes[session_id].append({"role": "user", "content": mensagem})
        
        # Adiciona resposta do assistente ao histórico
        contexto_sessoes[session_id].append({"role": "assistant", "content": resposta})
        
        # Limita histórico para evitar consumo excessivo de memória
        # Mantém apenas as últimas MAX_HISTORICO_MENSAGENS mensagens
        if len(contexto_sessoes[session_id]) > MAX_HISTORICO_MENSAGENS:
            contexto_sessoes[session_id] = contexto_sessoes[session_id][-MAX_HISTORICO_MENSAGENS:]
            logger.info(f"Histórico limitado para {MAX_HISTORICO_MENSAGENS} mensagens na sessão: {session_id}")
        
        logger.info(f"Resposta gerada com sucesso para sessão: {session_id}")
        return resposta
        
    except Exception as e:
        # Em caso de erro, registra e usa modo fallback
        logger.error(f"Erro ao gerar resposta com OpenAI: {e}")
        return gerar_resposta_fallback(mensagem)


def gerar_resposta_fallback(mensagem: str) -> str:
    """
    Resposta fallback quando OpenAI não está disponível.
    
    Este modo fornece respostas básicas baseadas em palavras-chave
    e análise de dados do CSV, sem usar IA.
    
    Args:
        mensagem: Mensagem do usuário
        
    Returns:
        str: Resposta básica baseada em palavras-chave
    """
    mensagem_lower = mensagem.lower()
    
    # Analisa dados mesmo sem OpenAI
    analise_dados = analisar_dados_csv()
    dados_especificos = buscar_dados_especificos(mensagem)
    
    # Se encontrou dados específicos, retorna eles
    if dados_especificos:
        return dados_especificos
    
    # Respostas baseadas em palavras-chave
    respostas_base = {
        "governança": "A governança de dados é fundamental para garantir qualidade, segurança e conformidade dos dados organizacionais.",
        "formulário": f"Temos {analise_dados.get('total_formularios', 0)} formulário(s) no sistema.",
        "campo": f"Temos {analise_dados.get('total_campos', 0)} campo(s) único(s) no sistema.",
        "fluxo": f"Temos {analise_dados.get('total_fluxos', 0)} fluxo(s) de trabalho no sistema.",
        "serviço": f"Temos {analise_dados.get('total_servicos', 0)} serviço(s) no sistema.",
        "qualidade": "Qualidade de dados envolve precisão, completude, consistência e atualidade.",
        "compliance": "Compliance garante conformidade com regulamentações como LGPD e GDPR.",
        "segurança": "Segurança de dados inclui controle de acesso, criptografia e auditoria.",
    }
    
    # Procura por palavras-chave na mensagem
    for palavra, resposta in respostas_base.items():
        if palavra in mensagem_lower:
            return resposta
    
    # Resposta padrão genérica
    return (
        "Entendi sua pergunta. Posso ajudar com informações sobre formulários, "
        "fluxos, campos e serviços do dashboard. Como posso ajudar?"
    )


# =============================================================================
# FUNÇÃO DE TESTE
# =============================================================================

def testar_conectividade() -> bool:
    """
    Testa se o chatbot está funcionando corretamente.
    
    Útil para verificar se todas as dependências estão configuradas.
    
    Returns:
        bool: True se funcionando, False caso contrário
    """
    try:
        resposta = gerar_resposta("teste")
        return len(resposta) > 0
    except Exception as e:
        logger.error(f"Erro ao testar chatbot: {e}")
        return False


# =============================================================================
# EXECUÇÃO DIRETA (para testes)
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Testando Chatbot de Governança...")
    print("=" * 60)
    
    if testar_conectividade():
        print("✅ Chatbot funcionando corretamente!")
        
        # Teste com uma pergunta real
        print("\n" + "=" * 60)
        print("Teste de pergunta:")
        print("=" * 60)
        resposta = gerar_resposta("Quantos formulários temos no sistema?")
        print(f"Resposta: {resposta}")
    else:
        print("❌ Erro no chatbot")
