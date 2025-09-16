"""
Servicio de integración entre el agente IA y el sistema de chats
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from schemas.ai.agentSchemas import (
    AgentRequest, AgentResponse, ConversationMessage, MessageType, ConversationContext
)
from schemas.chats.chatSchemas import MessageResponse
from services.ai.agentService import ai_agent_service
from services.chats.chatService import get_messages_service, get_chat_service

logger = logging.getLogger(__name__)

class ChatAgentIntegration:
    """
    Servicio que integra el agente IA con el sistema de chats existente
    """
    
    def __init__(self):
        self.max_history_messages = 10  # Límite de mensajes de historial
    
    def _convert_chat_messages_to_conversation(self, chat_messages: List[MessageResponse]) -> List[ConversationMessage]:
        """
        Convierte mensajes del chat a formato de conversación del agente
        """
        conversation = []
        
        for msg in chat_messages:
            message_type = MessageType.USER if msg.is_from_user else MessageType.ASSISTANT
            
            conversation_msg = ConversationMessage(
                role=message_type,
                content=msg.content,
                timestamp=msg.created_at,
                metadata=msg.metadata
            )
            conversation.append(conversation_msg)
        
        return conversation
    
    def _extract_conversation_context(self, chat_id: int, conversation_history: List[ConversationMessage]) -> ConversationContext:
        """
        Extrae contexto de la conversación para mejorar las respuestas del agente
        """
        context = ConversationContext(chat_id=chat_id)
        
        if not conversation_history:
            return context
        
        # Extraer productos mencionados
        mentioned_products = []
        current_topic = None
        user_preferences = {}
        
        # Analizar mensajes recientes para extraer contexto
        recent_messages = conversation_history[-5:]  # Últimos 5 mensajes
        
        for msg in recent_messages:
            content_lower = msg.content.lower()
            
            # Detectar menciones de productos
            if any(product in content_lower for product in ["iphone", "mac", "ipad", "watch", "airpods"]):
                if "iphone" in content_lower:
                    current_topic = "iPhone"
                elif "mac" in content_lower or "macbook" in content_lower:
                    current_topic = "Mac"
                elif "ipad" in content_lower:
                    current_topic = "iPad"
                elif "watch" in content_lower:
                    current_topic = "Apple Watch"
                elif "airpods" in content_lower:
                    current_topic = "AirPods"
            
            # Detectar preferencias de presupuesto
            if any(word in content_lower for word in ["precio", "presupuesto", "costo", "barato", "económico"]):
                user_preferences["budget_conscious"] = True
            
            # Detectar nivel de experiencia técnica
            if any(word in content_lower for word in ["especificaciones", "técnico", "rendimiento", "procesador"]):
                user_preferences["technical_user"] = True
        
        context.current_topic = current_topic
        context.mentioned_products = mentioned_products
        context.user_preferences = user_preferences if user_preferences else None
        
        # Determinar etapa de la conversación
        if len(conversation_history) <= 2:
            context.conversation_stage = "initial"
        elif any("comprar" in msg.content.lower() for msg in recent_messages):
            context.conversation_stage = "purchase_intent"
        elif current_topic:
            context.conversation_stage = "product_focus"
        else:
            context.conversation_stage = "exploration"
        
        return context
    
    def get_agent_response_with_context(self, 
                                      message: str, 
                                      chat_id: int, 
                                      user_id: Optional[int] = None,
                                      include_history: bool = True) -> AgentResponse:
        """
        Obtiene respuesta del agente considerando el contexto del chat
        """
        try:
            conversation_history = []
            context = ConversationContext(chat_id=chat_id)
            
            if include_history:
                # Obtener historial de mensajes del chat
                try:
                    chat_messages = get_messages_service(chat_id)
                    if chat_messages:
                        # Tomar solo los mensajes más recientes
                        recent_messages = chat_messages[-self.max_history_messages:]
                        conversation_history = self._convert_chat_messages_to_conversation(recent_messages)
                        context = self._extract_conversation_context(chat_id, conversation_history)
                except Exception as e:
                    logger.warning(f"No se pudo obtener historial del chat {chat_id}: {str(e)}")
            
            # Crear request para el agente
            agent_request = AgentRequest(
                message=message,
                chat_id=chat_id,
                user_id=user_id,
                conversation_history=conversation_history,
                context=context.dict() if context else None
            )
            
            # Procesar con el agente
            response = ai_agent_service.process_request(agent_request)
            
            # Enriquecer respuesta con información del contexto
            if context and context.current_topic:
                if not response.metadata:
                    response.metadata = {}
                response.metadata["current_topic"] = context.current_topic
                response.metadata["conversation_stage"] = context.conversation_stage
            
            return response
            
        except Exception as e:
            logger.error(f"Error obteniendo respuesta con contexto: {str(e)}")
            # Fallback: respuesta sin contexto
            fallback_request = AgentRequest(message=message, chat_id=chat_id, user_id=user_id)
            return ai_agent_service.process_request(fallback_request)
    
    def suggest_conversation_starters(self, chat_id: int) -> List[str]:
        """
        Sugiere iniciadores de conversación basados en el historial del chat
        """
        try:
            chat_messages = get_messages_service(chat_id)
            
            if not chat_messages:
                # Chat nuevo - sugerencias generales
                return [
                    "¿Qué producto Apple te interesa?",
                    "¿Buscas algo específico hoy?",
                    "¿Te ayudo a encontrar el dispositivo perfecto para ti?"
                ]
            
            # Analizar historial para sugerir seguimientos
            last_messages = chat_messages[-3:]
            conversation_history = self._convert_chat_messages_to_conversation(last_messages)
            context = self._extract_conversation_context(chat_id, conversation_history)
            
            suggestions = []
            
            if context.current_topic:
                suggestions.append(f"¿Quieres saber más sobre {context.current_topic}?")
                suggestions.append(f"¿Te ayudo a comparar modelos de {context.current_topic}?")
            
            if context.conversation_stage == "product_focus":
                suggestions.append("¿Tienes alguna pregunta específica sobre las características?")
                suggestions.append("¿Te interesa conocer los accesorios disponibles?")
            elif context.conversation_stage == "purchase_intent":
                suggestions.append("¿Quieres información sobre opciones de pago?")
                suggestions.append("¿Te ayudo con la configuración inicial?")
            
            if not suggestions:
                suggestions = [
                    "¿Hay algo más en lo que pueda ayudarte?",
                    "¿Te interesa explorar otros productos?",
                    "¿Quieres que te ayude con alguna comparación?"
                ]
            
            return suggestions[:3]
            
        except Exception as e:
            logger.error(f"Error sugiriendo iniciadores: {str(e)}")
            return [
                "¿En qué más puedo ayudarte?",
                "¿Tienes alguna otra pregunta?",
                "¿Te interesa ver otros productos?"
            ]

# Instancia global del servicio de integración
chat_agent_integration = ChatAgentIntegration()
