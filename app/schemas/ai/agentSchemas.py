from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Import de enums necesarios para los esquemas de rutas
try:
    from services.ai.routing import BotType
    from services.ai.config import AIProvider
except ImportError:
    # Fallback si hay imports circulares
    class BotType(str, Enum):
        WHATSAPP_BOT = "whatsapp_bot"
        WEB_CHAT_BOT = "web_chat_bot" 
        TELEGRAM_BOT = "telegram_bot"
    
    class AIProvider(str, Enum):
        GEMINI = "gemini"
        OPENAI = "openai"
        ANTHROPIC = "anthropic"

class AgentRole(str, Enum):
    """Roles disponibles para el agente de IA"""
    SALES_ASSISTANT = "sales_assistant"
    PRODUCT_EXPERT = "product_expert"
    TECHNICAL_SUPPORT = "technical_support"
    GENERAL_ASSISTANT = "general_assistant"

class MessageType(str, Enum):
    """Tipos de mensaje en la conversación"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ConversationMessage(BaseModel):
    """Esquema para un mensaje en la conversación"""
    role: MessageType
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentRequest(BaseModel):
    """Esquema para solicitudes al agente de IA"""
    message: str = Field(..., description="Mensaje del usuario")
    chat_id: Optional[int] = Field(None, description="ID del chat asociado")
    user_id: Optional[int] = Field(None, description="ID del usuario")
    agent_role: AgentRole = Field(AgentRole.SALES_ASSISTANT, description="Rol del agente")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")
    conversation_history: Optional[List[ConversationMessage]] = Field(None, description="Historial de conversación")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ProductRecommendation(BaseModel):
    """Esquema para recomendaciones de productos"""
    product_id: int
    name: str
    category: str
    price: float
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Puntuación de confianza de la recomendación")
    reason: str = Field(..., description="Razón de la recomendación")
    specifications: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    """Esquema para respuestas del agente de IA"""
    response: str = Field(..., description="Respuesta generada por el agente")
    agent_role: AgentRole
    recommendations: Optional[List[ProductRecommendation]] = Field(None, description="Productos recomendados")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza en la respuesta")
    sources: Optional[List[str]] = Field(None, description="Fuentes de información utilizadas")
    follow_up_suggestions: Optional[List[str]] = Field(None, description="Sugerencias de seguimiento")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadatos adicionales")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ConversationContext(BaseModel):
    """Esquema para el contexto de conversación"""
    chat_id: Optional[int] = None
    user_preferences: Optional[Dict[str, Any]] = None
    current_topic: Optional[str] = None
    mentioned_products: Optional[List[int]] = None
    user_intent: Optional[str] = None
    conversation_stage: Optional[str] = None

class AgentConfiguration(BaseModel):
    """Configuración del agente de IA"""
    role: AgentRole = AgentRole.SALES_ASSISTANT
    max_recommendations: int = Field(3, ge=1, le=10)
    use_conversation_history: bool = True
    enable_product_search: bool = True
    response_language: str = "es"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(500, ge=50, le=2000)

class SearchQuery(BaseModel):
    """Esquema para búsquedas semánticas"""
    query: str = Field(..., description="Consulta de búsqueda")
    category_filter: Optional[str] = Field(None, description="Filtro por categoría")
    price_range: Optional[Dict[str, float]] = Field(None, description="Rango de precios")
    limit: int = Field(5, ge=1, le=20, description="Número máximo de resultados")
    threshold: float = Field(0.5, ge=0.0, le=1.0, description="Umbral de similitud")

class ChatIntegrationRequest(BaseModel):
    """Esquema para integración con sistema de chats"""
    chat_id: int
    message: str
    agent_config: Optional[AgentConfiguration] = None
    
class ChatIntegrationResponse(BaseModel):
    """Respuesta de integración con chats"""
    chat_id: int
    message_id: int
    agent_response: AgentResponse
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# ========== ESQUEMAS ESPECÍFICOS PARA RUTAS API ==========

class GraphMessage(BaseModel):
    """Mensaje para procesar por el sistema de grafos"""
    message: str = Field(..., description="Mensaje del usuario")
    bot_type: BotType = Field(BotType.WEB_CHAT_BOT, description="Tipo de bot")
    chat_id: int = Field(..., description="ID del chat")
    user_id: Optional[int] = Field(None, description="ID del usuario")
    save_to_chat: bool = Field(True, description="Guardar conversación en BD")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")

class AgentDirectMessage(BaseModel):
    """Mensaje directo a un agente específico"""
    message: str = Field(..., description="Mensaje del usuario")
    agent_type: str = Field(..., description="Tipo de agente")
    chat_id: Optional[int] = Field(None, description="ID del chat")
    user_id: Optional[int] = Field(None, description="ID del usuario")
    include_product_search: bool = Field(True, description="Incluir búsqueda de productos")

class ProviderSwitchRequest(BaseModel):
    """Solicitud para cambiar proveedor de IA"""
    provider: AIProvider = Field(..., description="Nuevo proveedor")
