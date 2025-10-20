# config.py - Configurações do Dash Governança

DESIGN_CONFIG = {
    "primary_color": "#2E86AB",
    "secondary_color": "#A23B72", 
    "background_color": "#F8F9FA",
    "text_color": "#212529",
    "border_color": "#DEE2E6",
    "success_color": "#28A745",
    "warning_color": "#FFC107",
    "danger_color": "#DC3545",
    "info_color": "#17A2B8",
    "light_color": "#F8F9FA",
    "dark_color": "#343A40",
    "font_family": "Arial, sans-serif",
    "border_radius": "8px",
    "box_shadow": "0 2px 4px rgba(0,0,0,0.1)",
    "title_color": "#212529",
    "card_background_color": "#FFFFFF"
}

# Configurações do chatbot
CHATBOT_CONFIG = {
    "max_tokens": 150,
    "temperature": 0.7,
    "model_name": "gpt-3.5-turbo",
    "system_prompt": "Você é um assistente de governança de dados. Responda de forma clara e objetiva sobre questões relacionadas a governança, qualidade de dados e compliance."
}

# Configurações da aplicação
APP_CONFIG = {
    "title": "Dash Governança v3",
    "debug": True,
    "port": 8050,
    "flask_port": 5000
}
