"""
Orquestador principal de grafos para el sistema de agentes IA
Maneja el flujo completo desde detección de intenciones hasta respuesta final
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from services.ai.routing import bot_orchestrator, BotType, ResponseType
from services.ai.nodes import AgentNodeFactory
from services.ai.cost_tracker import cost_tracker
from services.ai.config import ai_config
from services.chats.chatService import create_message_service, get_messages_service
from schemas.chats.chatSchemas import MessageCreate, MessageSender

logger = logging.getLogger(__name__)

class GraphOrchestrator:
    """
    Orquestador principal que maneja todo el flujo del sistema de grafos
    """
    
    def __init__(self):
        self.bot_orchestrator = bot_orchestrator
        self.agent_nodes = {}  # Cache de nodos de agentes
        self.active_conversations = {}  # Conversaciones activas
        
    async def initialize(self):
        """Inicializa el orquestador y sus dependencias"""
        try:
            # Inicializar tracker de costos
            await cost_tracker.init_redis()
            
            # Pre-cargar nodos de agentes más usados
            await self._preload_common_agents()
            
            logger.info("Orquestador de grafos inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando orquestador: {str(e)}")
            raise
    
    async def _preload_common_agents(self):
        """Pre-carga agentes más comunes para reducir latencia"""
        common_agents = ["sales_assistant", "general_assistant"]
        
        for agent_type in common_agents:
            try:
                await self._get_agent_node(agent_type)
                logger.info(f"Agente {agent_type} pre-cargado")
            except Exception as e:
                logger.warning(f"No se pudo pre-cargar agente {agent_type}: {str(e)}")
    
    async def _get_agent_node(self, agent_type: str):
        """Obtiene o crea un nodo de agente específico"""
        if agent_type not in self.agent_nodes:
            try:
                self.agent_nodes[agent_type] = AgentNodeFactory.create_node(agent_type)
                logger.info(f"Nodo de agente {agent_type} creado")
            except Exception as e:
                logger.error(f"Error creando nodo {agent_type}: {str(e)}")
                raise
        
        return self.agent_nodes[agent_type]
    
    async def process_message(self,
                            message: str,
                            bot_type: BotType,
                            chat_id: int,
                            user_id: Optional[int] = None,
                            save_to_chat: bool = True,
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Procesa un mensaje completo a través del sistema de grafos
        """
        start_time = datetime.now()
        
        try:
            # 1. Routing inicial - Detectar intención y determinar flujo
            routing_result = self.bot_orchestrator.process_message(
                message=message,
                bot_type=bot_type,
                chat_id=chat_id,
                user_id=user_id,
                context=context
            )
            
            logger.info(f"Intent detectado: {routing_result['intent']} (confianza: {routing_result['confidence']:.2f})")
            
            # 2. Construir respuesta base
            response = {
                "chat_id": chat_id,
                "user_id": user_id,
                "bot_type": bot_type.value,
                "message": message,
                "intent": routing_result["intent"],
                "confidence": routing_result["confidence"],
                "detected_keywords": routing_result["detected_keywords"],
                "response_type": routing_result["response_type"],
                "timestamp": start_time.isoformat(),
                "processing_steps": []
            }
            
            # 3. Manejar según tipo de respuesta
            if routing_result["response_type"] == ResponseType.DIRECT_RESPONSE.value:
                # Respuesta directa sin agente
                response.update({
                    "response": routing_result.get("direct_response", ""),
                    "followup_suggestions": routing_result.get("followup_suggestions", []),
                    "agent_used": None,
                    "requires_agent": False,
                    "cost": 0.0
                })
                response["processing_steps"].append("direct_response_generated")
                
            elif routing_result["response_type"] == ResponseType.AGENT_REQUIRED.value:
                # Requiere procesamiento por agente
                agent_type = routing_result.get("suggested_agent", "general_assistant")
                agent_response = await self._process_with_agent(
                    message=message,
                    agent_type=agent_type,
                    chat_id=chat_id,
                    user_id=user_id,
                    context=routing_result.get("agent_context", {})
                )
                
                response.update({
                    "response": agent_response["response"],
                    "agent_used": agent_type,
                    "requires_agent": True,
                    "cost": agent_response.get("cost", 0.0),
                    "model_used": agent_response.get("model_used"),
                    "response_time": agent_response.get("response_time", 0.0),
                    # Campos adicionales del agente sin duplicar 'response'
                    "products": agent_response.get("products", []),
                    "context_used": agent_response.get("context_used", False),
                    "success": agent_response.get("success", True)
                })
                response["processing_steps"].append(f"agent_{agent_type}_processed")
                
            elif routing_result["response_type"] == ResponseType.ESCALATE_TO_HUMAN.value:
                # Escalamiento a humano
                response.update({
                    "response": routing_result.get("direct_response", ""),
                    "escalated_to_human": True,
                    "agent_used": None,
                    "requires_agent": False,
                    "cost": 0.0
                })
                response["processing_steps"].append("escalated_to_human")
                
                # Aquí se podría integrar con sistema de tickets o notificaciones
                await self._notify_human_escalation(chat_id, message, user_id)
            
            # 4. Guardar conversación en base de datos si está habilitado
            if save_to_chat:
                try:
                    await self._save_conversation_to_db(
                        chat_id=chat_id,
                        user_message=message,
                        bot_response=response["response"],
                        metadata=response
                    )
                    response["processing_steps"].append("conversation_saved")
                except Exception as e:
                    logger.warning(f"No se pudo guardar conversación: {str(e)}")
            
            # 5. Calcular tiempo total de procesamiento
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            response["total_processing_time"] = total_time
            
            # 6. Verificar límites de costo
            cost_limits = await cost_tracker.check_cost_limits()
            response["cost_limits"] = cost_limits
            
            if cost_limits["daily"]["exceeded"] or cost_limits["monthly"]["exceeded"]:
                logger.warning(f"Límite de costo excedido: {cost_limits}")
                response["cost_limit_warning"] = True
            
            logger.info(f"Mensaje procesado exitosamente en {total_time:.2f}s")
            return response
            
        except Exception as e:
            error_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error procesando mensaje: {str(e)}")
            
            return {
                "chat_id": chat_id,
                "user_id": user_id,
                "bot_type": bot_type.value,
                "message": message,
                "error": str(e),
                "response": "Disculpa, estoy experimentando dificultades técnicas. ¿Podrías intentar de nuevo?",
                "success": False,
                "processing_time": error_time,
                "timestamp": start_time.isoformat()
            }
    
    async def _process_with_agent(self,
                                 message: str,
                                 agent_type: str,
                                 chat_id: int,
                                 user_id: Optional[int] = None,
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Procesa mensaje con un agente específico
        """
        try:
            # Obtener nodo del agente
            agent_node = await self._get_agent_node(agent_type)
            
            # Cargar historial de conversación como contexto
            conversation_history = await self._get_conversation_history(chat_id)
            
            # Combinar contexto existente con historial
            full_context = context or {}
            if conversation_history:
                full_context["conversation_history"] = conversation_history
                full_context["has_conversation_history"] = True
            else:
                full_context["has_conversation_history"] = False
            
            # Procesar mensaje con contexto completo
            agent_result = await agent_node.process_message(
                message=message,
                chat_id=chat_id,
                user_id=user_id,
                include_product_search=True,
                context=full_context
            )
            
            # Enriquecer con información adicional
            agent_result["cost"] = await self._calculate_message_cost(agent_result)
            agent_result["agent_type"] = agent_type
            agent_result["context_used"] = bool(conversation_history)
            
            return agent_result
            
        except Exception as e:
            logger.error(f"Error procesando con agente {agent_type}: {str(e)}")
            return {
                "response": f"Error procesando con agente {agent_type}: {str(e)}",
                "success": False,
                "error": str(e),
                "agent_type": agent_type,
                "cost": 0.0,
                "context_used": False
            }
    
    async def _calculate_message_cost(self, agent_result: Dict[str, Any]) -> float:
        """Calcula el costo de un mensaje procesado por agente"""
        try:
            # El costo ya debería estar calculado en el cost_tracker durante el procesamiento
            # Aquí podríamos hacer cálculos adicionales si fuera necesario
            return 0.0  # El tracking real se hace en los nodos
        except Exception as e:
            logger.warning(f"Error calculando costo: {str(e)}")
            return 0.0
    
    async def _get_conversation_history(self, chat_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene el historial reciente de conversación de un chat
        """
        try:
            logger.info(f"Intentando cargar historial para chat {chat_id}")
            
            # Obtener mensajes recientes del chat (excluyendo el mensaje actual)
            messages = get_messages_service(chat_id=chat_id, limit=limit)
            
            logger.info(f"Mensajes obtenidos de la BD: {len(messages) if messages else 0}")
            
            if not messages:
                logger.info(f"No hay mensajes en el historial para chat {chat_id}")
                return []
            
            # Convertir a formato esperado por los agentes
            conversation_history = []
            for msg in messages:
                logger.debug(f"Procesando mensaje: ID={msg.id}, sender={msg.sender}, body={msg.body[:50]}...")
                
                # msg es un objeto MessageResponse de Pydantic, acceder a atributos directamente
                role = "user" if msg.sender.value == "USER" else "assistant"
                conversation_history.append({
                    "role": role,
                    "content": msg.body,
                    "timestamp": msg.created_at.isoformat() if msg.created_at else None,
                    "message_id": msg.id
                })
            
            logger.info(f"Historial convertido: {len(conversation_history)} mensajes para chat {chat_id}")
            logger.debug(f"Últimos 2 mensajes del historial: {conversation_history[-2:] if len(conversation_history) >= 2 else conversation_history}")
            
            return conversation_history
            
        except Exception as e:
            logger.warning(f"Error cargando historial de conversación para chat {chat_id}: {str(e)}")
            logger.exception("Detalles del error:")
            return []
    
    async def _save_conversation_to_db(self,
                                      chat_id: int,
                                      user_message: str,
                                      bot_response: str,
                                      metadata: Dict[str, Any]):
        """
        Guarda la conversación en la base de datos
        """
        try:
            # Guardar mensaje del usuario
            user_msg = MessageCreate(
                chat_id=chat_id,
                sender=MessageSender.USER,
                body=user_message
            )
            create_message_service(user_msg)
            
            # Guardar respuesta del bot/agente  
            bot_msg = MessageCreate(
                chat_id=chat_id,
                sender=MessageSender.BOT,
                body=bot_response
            )
            create_message_service(bot_msg)
            
        except Exception as e:
            logger.error(f"Error guardando conversación: {str(e)}")
            raise
    
    async def _notify_human_escalation(self,
                                      chat_id: int,
                                      original_message: str,
                                      user_id: Optional[int] = None):
        """
        Notifica escalamiento a humano (implementación futura)
        """
        try:
            # Aquí se podría:
            # 1. Crear ticket en sistema de soporte
            # 2. Enviar notificación a agentes humanos
            # 3. Marcar conversación para revisión prioritaria
            
            logger.info(f"Escalamiento a humano para chat {chat_id}")
            
            # Por ahora, solo logging
            escalation_data = {
                "chat_id": chat_id,
                "user_id": user_id,
                "original_message": original_message,
                "timestamp": datetime.now().isoformat(),
                "reason": "automated_escalation"
            }
            
            # Se podría guardar en una tabla de escalaciones
            logger.info(f"Escalación registrada: {json.dumps(escalation_data)}")
            
        except Exception as e:
            logger.error(f"Error en escalamiento: {str(e)}")
    
    async def get_conversation_summary(self, chat_id: int) -> Dict[str, Any]:
        """
        Obtiene resumen de una conversación
        """
        try:
            # Obtener mensajes del chat
            messages = get_messages_service(chat_id)
            
            if not messages:
                return {
                    "chat_id": chat_id,
                    "message_count": 0,
                    "summary": "No hay mensajes en esta conversación"
                }
            
            # Analizar conversación
            user_messages = [msg for msg in messages if msg.is_from_user]
            bot_messages = [msg for msg in messages if not msg.is_from_user]
            
            # Extraer intenciones más comunes
            intents = []
            total_cost = 0.0
            agents_used = set()
            
            for msg in bot_messages:
                if msg.metadata:
                    if "intent" in msg.metadata:
                        intents.append(msg.metadata["intent"])
                    if "cost" in msg.metadata:
                        total_cost += float(msg.metadata.get("cost", 0))
                    if "agent_used" in msg.metadata and msg.metadata["agent_used"]:
                        agents_used.add(msg.metadata["agent_used"])
            
            # Determinar intención principal
            if intents:
                main_intent = max(set(intents), key=intents.count)
            else:
                main_intent = "unknown"
            
            return {
                "chat_id": chat_id,
                "message_count": len(messages),
                "user_messages": len(user_messages),
                "bot_messages": len(bot_messages),
                "main_intent": main_intent,
                "all_intents": list(set(intents)),
                "agents_used": list(agents_used),
                "total_cost": round(total_cost, 6),
                "first_message": messages[0].created_at.isoformat() if messages else None,
                "last_message": messages[-1].created_at.isoformat() if messages else None,
                "conversation_active": (datetime.now() - messages[-1].created_at).total_seconds() < 3600 if messages else False
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de conversación: {str(e)}")
            return {
                "chat_id": chat_id,
                "error": str(e),
                "summary": "Error obteniendo resumen"
            }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """
        Obtiene métricas del sistema completo
        """
        try:
            # Métricas de routing
            routing_stats = self.bot_orchestrator.get_routing_stats()
            
            # Métricas de costos
            daily_summary = await cost_tracker.get_cost_summary("daily")
            monthly_summary = await cost_tracker.get_cost_summary("monthly")
            
            # Límites de costo
            cost_limits = await cost_tracker.check_cost_limits()
            
            # Estado de agentes
            agent_status = {}
            for agent_type in AgentNodeFactory.get_available_agent_types():
                agent_status[agent_type] = {
                    "loaded": agent_type in self.agent_nodes,
                    "config": ai_config.get_agent_config(agent_type).dict() if ai_config.get_agent_config(agent_type) else None
                }
            
            return {
                "routing_stats": routing_stats,
                "cost_summary": {
                    "daily": daily_summary.dict(),
                    "monthly": monthly_summary.dict(),
                    "limits": cost_limits
                },
                "agent_status": agent_status,
                "active_conversations": len(self.active_conversations),
                "system_health": "healthy",
                "ai_provider": ai_config.current_provider.value,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas del sistema: {str(e)}")
            return {
                "error": str(e),
                "system_health": "error",
                "timestamp": datetime.now().isoformat()
            }

# Instancia global del orquestador
graph_orchestrator = GraphOrchestrator()
