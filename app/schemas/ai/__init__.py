# AI Schemas Package
"""
Esquemas de datos para el sistema de agentes de IA
"""

from .agentSchemas import (
    # Enums básicos
    AgentRole,
    MessageType,
    BotType,
    AIProvider,
    
    # Esquemas de conversación
    ConversationMessage,
    AgentRequest,
    AgentResponse,
    ProductRecommendation,
    ConversationContext,
    AgentConfiguration,
    
    # Esquemas de búsqueda
    SearchQuery,
    
    # Esquemas de integración
    ChatIntegrationRequest,
    ChatIntegrationResponse,
    
    # Esquemas específicos para rutas API
    GraphMessage,
    AgentDirectMessage,
    ProviderSwitchRequest
)

__all__ = [
    # Enums
    "AgentRole",
    "MessageType",
    "BotType", 
    "AIProvider",
    
    # Conversación
    "ConversationMessage",
    "AgentRequest",
    "AgentResponse",
    "ProductRecommendation",
    "ConversationContext",
    "AgentConfiguration",
    
    # Búsqueda
    "SearchQuery",
    
    # Integración
    "ChatIntegrationRequest",
    "ChatIntegrationResponse",
    
    # Rutas API
    "GraphMessage",
    "AgentDirectMessage", 
    "ProviderSwitchRequest"
]