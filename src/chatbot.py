# src/chatbot.py - Módulo do Chatbot
import requests
import json

def gerar_resposta(mensagem: str) -> str:
    """
    Gera uma resposta do chatbot baseada na mensagem do usuário.
    
    Args:
        mensagem (str): A mensagem enviada pelo usuário
        
    Returns:
        str: A resposta gerada pelo chatbot
    """
    if not mensagem or mensagem.strip() == "":
        return "Por favor, digite uma mensagem válida."
    
    mensagem_lower = mensagem.lower().strip()
    
    # Respostas baseadas em palavras-chave para governança de dados
    if any(palavra in mensagem_lower for palavra in ["governança", "governance", "dados", "data"]):
        return "A governança de dados é fundamental para garantir a qualidade, segurança e conformidade dos dados da organização. Como posso ajudá-lo com questões específicas de governança?"
    
    elif any(palavra in mensagem_lower for palavra in ["qualidade", "quality", "qualidade dos dados"]):
        return "A qualidade dos dados envolve precisão, completude, consistência e confiabilidade. Implementamos processos de validação e monitoramento contínuo para manter alta qualidade."
    
    elif any(palavra in mensagem_lower for palavra in ["compliance", "conformidade", "lgpd", "gdpr"]):
        return "O compliance garante que os dados sejam tratados de acordo com regulamentações como LGPD e GDPR. Temos políticas e procedimentos específicos para cada regulamentação."
    
    elif any(palavra in mensagem_lower for palavra in ["metadados", "metadata", "catalog", "catálogo"]):
        return "Os metadados são informações sobre os dados - origem, estrutura, transformações. Nosso catálogo de dados centraliza essas informações para facilitar descoberta e governança."
    
    elif any(palavra in mensagem_lower for palavra in ["segurança", "security", "acesso", "access"]):
        return "A segurança dos dados inclui controle de acesso, criptografia e auditoria. Implementamos níveis de acesso baseados em roles e monitoramento contínuo de atividades."
    
    elif any(palavra in mensagem_lower for palavra in ["dashboard", "relatório", "report", "métricas", "metrics"]):
        return "Nossos dashboards fornecem visão em tempo real da qualidade dos dados, uso de sistemas e conformidade. Você pode explorar diferentes visualizações e filtros."
    
    elif any(palavra in mensagem_lower for palavra in ["ajuda", "help", "como usar", "tutorial"]):
        return "Posso ajudá-lo com questões sobre governança de dados, qualidade, compliance e uso dos dashboards. Digite sua pergunta específica para obter informações detalhadas."
    
    else:
        return "Entendi sua pergunta. Para questões sobre governança de dados, posso ajudar com: qualidade dos dados, compliance, metadados, segurança, dashboards e relatórios. Pode ser mais específico?"

def testar_conectividade() -> bool:
    """
    Testa se o chatbot está funcionando corretamente.
    
    Returns:
        bool: True se funcionando, False caso contrário
    """
    try:
        resposta = gerar_resposta("teste")
        return len(resposta) > 0
    except Exception as e:
        print(f"Erro ao testar chatbot: {e}")
        return False

if __name__ == "__main__":
    # Teste básico do chatbot
    print("Testando chatbot...")
    if testar_conectividade():
        print("✅ Chatbot funcionando corretamente!")
    else:
        print("❌ Erro no chatbot")
