# src/callbacks/__init__.py - Registro de todos os callbacks
from dash import Dash
from .overview_callbacks import register_callbacks as register_overview_callbacks
from .fluxos_callbacks import register_callbacks as register_fluxos_callbacks
from .formularios_callbacks import register_callbacks as register_formularios_callbacks
from .campos_callbacks import register_callbacks as register_campos_callbacks

def register_all(app: Dash):
    """
    Registra todos os callbacks da aplicação.
    
    Args:
        app (Dash): Instância da aplicação Dash
    """
    register_overview_callbacks(app)
    register_fluxos_callbacks(app)
    register_formularios_callbacks(app)
    register_campos_callbacks(app)
