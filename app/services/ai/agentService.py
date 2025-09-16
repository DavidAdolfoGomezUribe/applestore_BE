import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import requests
from sentence_transformers import SentenceTransformer

# Langroid imports
from langroid import ChatAgent, ChatAgentConfig
from langroid.language_models import OpenAIGPTConfig
from langroid.utils.configuration import set_global, Settings

from schemas.ai.agentSchemas import (
    AgentRequest, AgentResponse, AgentRole, ProductRecommendation, 
    ConversationContext, AgentConfiguration, SearchQuery
)

logger = logging.getLogger(__name__)

class QdrantSearchService:
    """Servicio para búsquedas semánticas en Qdrant"""
    
    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
        self.collection_name = os.getenv("QDRANT_COLLECTION", "products_kb")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def search_products(self, query: str, limit: int = 5, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Busca productos similares usando búsqueda vectorial
        """
        try:
            # Generar embedding de la consulta
            query_vector = self.model.encode(query).tolist()
            
            search_payload = {
                "vector": query_vector,
                "limit": limit,
                "score_threshold": threshold,
                "with_payload": True
            }
            
            url = f"{self.qdrant_url}/collections/{self.collection_name}/points/search"
            response = requests.post(url, json=search_payload)
            response.raise_for_status()
            
            results = response.json().get("result", [])
            return [{"score": r["score"], "product": r["payload"]} for r in results]
            
        except Exception as e:
            logger.error(f"Error en búsqueda de productos: {str(e)}")
            return []

class AIAgentService:
    """Servicio principal del agente de IA usando Langroid"""
    
    def __init__(self):
        self.search_service = QdrantSearchService()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.default_config = AgentConfiguration()
        
        # Configurar Langroid
        if self.openai_api_key:
            # Configurar el modelo OpenAI para Langroid
            self.llm_config = OpenAIGPTConfig(
                chat_model="gpt-3.5-turbo",
                api_key=self.openai_api_key,
                temperature=0.7,
                max_tokens=500
            )
        else:
            logger.warning("OpenAI API key no encontrada. El agente funcionará en modo simulado.")
            self.llm_config = None
        
        # Inicializar agentes especializados
        self._init_specialized_agents()
        
    def _init_specialized_agents(self):
        """Inicializa agentes especializados para diferentes roles"""
        self.agents = {}
        
        if not self.llm_config:
            logger.warning("No se pueden inicializar agentes Langroid sin API key")
            return
            
        try:
            # Agente de ventas
            sales_config = ChatAgentConfig(
                llm=self.llm_config,
                name="AppleStoreSalesAgent",
                system_message=self._get_system_message(AgentRole.SALES_ASSISTANT)
            )
            self.agents[AgentRole.SALES_ASSISTANT] = ChatAgent(sales_config)
            
            # Agente experto en productos
            expert_config = ChatAgentConfig(
                llm=self.llm_config,
                name="AppleStoreExpertAgent", 
                system_message=self._get_system_message(AgentRole.PRODUCT_EXPERT)
            )
            self.agents[AgentRole.PRODUCT_EXPERT] = ChatAgent(expert_config)
            
            # Agente de soporte técnico
            support_config = ChatAgentConfig(
                llm=self.llm_config,
                name="AppleStoreSupportAgent",
                system_message=self._get_system_message(AgentRole.TECHNICAL_SUPPORT)
            )
            self.agents[AgentRole.TECHNICAL_SUPPORT] = ChatAgent(support_config)
            
            # Agente general
            general_config = ChatAgentConfig(
                llm=self.llm_config,
                name="AppleStoreGeneralAgent",
                system_message=self._get_system_message(AgentRole.GENERAL_ASSISTANT)
            )
            self.agents[AgentRole.GENERAL_ASSISTANT] = ChatAgent(general_config)
            
            logger.info("Agentes Langroid inicializados correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando agentes Langroid: {str(e)}")
            self.agents = {}
    
    def _get_system_message(self, role: AgentRole) -> str:
        """Obtiene el mensaje del sistema para cada rol usando Langroid"""
        base_context = """
        Eres un asistente especializado de Apple Store. Tienes acceso a información detallada sobre productos Apple y puedes ayudar a los clientes con sus consultas.
        
        PRODUCTOS DISPONIBLES:
        - iPhone (múltiples modelos con diferentes especificaciones)
        - Mac (MacBook Air, MacBook Pro, iMac, Mac Studio, Mac Pro)
        - iPad (iPad, iPad Air, iPad Pro, iPad mini)
        - Apple Watch (diferentes series y tamaños)
        - AirPods y accesorios
        
        INSTRUCCIONES:
        - Responde en español
        - Sé amigable y profesional
        - Proporciona información precisa y útil
        - Haz preguntas clarificadoras cuando sea necesario
        - Sugiere productos basándote en las necesidades del cliente
        - Menciona especificaciones relevantes cuando sea apropiado
        """
        
        role_specific = {
            AgentRole.SALES_ASSISTANT: """
            ROL: ASISTENTE DE VENTAS
            - Tu objetivo principal es ayudar a los clientes a encontrar el producto Apple perfecto
            - Entiende las necesidades específicas del cliente (uso, presupuesto, preferencias)
            - Recomienda productos apropiados con justificaciones claras
            - Ayuda con comparaciones entre modelos
            - Proporciona información sobre precios y opciones de financiamiento
            - Facilita el proceso de compra
            """,
            
            AgentRole.PRODUCT_EXPERT: """
            ROL: EXPERTO EN PRODUCTOS
            - Proporciona información técnica detallada y especificaciones
            - Explica las diferencias entre modelos y generaciones
            - Ayuda con comparaciones técnicas complejas
            - Responde preguntas específicas sobre rendimiento y capacidades
            - Conoce en profundidad todas las líneas de productos Apple
            """,
            
            AgentRole.TECHNICAL_SUPPORT: """
            ROL: SOPORTE TÉCNICO
            - Ayuda con problemas técnicos y configuración
            - Proporciona guías paso a paso para resolución de problemas
            - Asiste con compatibilidad entre dispositivos
            - Explica características técnicas de manera clara
            - Sugiere soluciones y workarounds
            """,
            
            AgentRole.GENERAL_ASSISTANT: """
            ROL: ASISTENTE GENERAL
            - Responde consultas generales sobre Apple y sus productos
            - Proporciona información sobre servicios y políticas
            - Direcciona a especialistas cuando sea necesario
            - Mantiene una experiencia de cliente excelente
            - Maneja consultas variadas con versatilidad
            """
        }
        
        return base_context + role_specific.get(role, role_specific[AgentRole.SALES_ASSISTANT])
        
    def _build_system_prompt(self, role: AgentRole, context: Optional[ConversationContext] = None) -> str:
        """
        Construye el prompt del sistema basado en el rol del agente
        """
        base_prompt = """Eres un asistente de ventas experto para Apple Store. Tu objetivo es ayudar a los clientes a encontrar los productos Apple perfectos para sus necesidades."""
        
        role_prompts = {
            AgentRole.SALES_ASSISTANT: """
                Como asistente de ventas de Apple Store, tu función es:
                - Entender las necesidades del cliente
                - Recomendar productos Apple apropiados
                - Proporcionar información detallada sobre especificaciones
                - Ayudar en el proceso de compra
                - Ser amigable, profesional y servicial
                
                Siempre considera el presupuesto del cliente y sus casos de uso específicos.
            """,
            AgentRole.PRODUCT_EXPERT: """
                Como experto en productos Apple, tu función es:
                - Proporcionar información técnica detallada
                - Comparar diferentes modelos y especificaciones
                - Explicar las ventajas y características únicas
                - Ayudar en decisiones técnicas complejas
                
                Usa tu conocimiento profundo de la línea de productos Apple.
            """,
            AgentRole.TECHNICAL_SUPPORT: """
                Como soporte técnico de Apple, tu función es:
                - Resolver problemas técnicos
                - Guiar en configuraciones y uso
                - Proporcionar troubleshooting
                - Recomendar soluciones
                
                Sé claro, paso a paso y paciente en tus explicaciones.
            """,
            AgentRole.GENERAL_ASSISTANT: """
                Como asistente general de Apple Store, tu función es:
                - Responder preguntas generales sobre Apple
                - Proporcionar información sobre servicios
                - Direccionar a especialistas cuando sea necesario
                - Mantener una experiencia de cliente excelente
            """
        }
        
        system_prompt = base_prompt + role_prompts.get(role, role_prompts[AgentRole.SALES_ASSISTANT])
        
        if context and context.user_preferences:
            system_prompt += f"\n\nPreferencias del usuario: {json.dumps(context.user_preferences, indent=2)}"
            
        return system_prompt
    
    def _extract_product_recommendations(self, user_message: str, context: Optional[ConversationContext] = None) -> List[ProductRecommendation]:
        """
        Extrae recomendaciones de productos basadas en el mensaje del usuario
        """
        try:
            # Buscar productos relevantes usando Qdrant
            search_results = self.search_service.search_products(user_message, limit=5, threshold=0.3)
            
            recommendations = []
            for result in search_results:
                product = result["product"]
                confidence = result["score"]
                
                recommendation = ProductRecommendation(
                    product_id=product.get("id"),
                    name=product.get("name", "Producto Apple"),
                    category=product.get("category", "Apple"),
                    price=float(product.get("price", 0)),
                    confidence_score=confidence,
                    reason=f"Coincidencia basada en tu consulta (confianza: {confidence:.2f})",
                    specifications=product.get("specifications")
                )
                recommendations.append(recommendation)
            
            return recommendations[:3]  # Límite de 3 recomendaciones
            
        except Exception as e:
            logger.error(f"Error extrayendo recomendaciones: {str(e)}")
            return []
    
    def _generate_ai_response(self, request: AgentRequest, config: AgentConfiguration) -> str:
        """
        Genera respuesta usando Langroid ChatAgent
        """
        try:
            # Obtener el agente apropiado para el rol
            agent = self.agents.get(request.agent_role)
            
            if not agent:
                logger.warning(f"Agente para rol {request.agent_role} no disponible, usando respuesta simulada")
                return self._generate_fallback_response(request)
            
            # Construir el contexto para Langroid
            context_message = ""
            if request.conversation_history:
                context_message = "\n\nCONTEXTO DE CONVERSACIÓN:\n"
                for msg in request.conversation_history[-5:]:  # Últimos 5 mensajes
                    role_label = "Cliente" if msg.role.value == "user" else "Asistente"
                    context_message += f"{role_label}: {msg.content}\n"
            
            # Agregar información de productos encontrados
            product_context = ""
            search_results = self.search_service.search_products(request.message, limit=3)
            if search_results:
                product_context = "\n\nPRODUCTOS RELEVANTES ENCONTRADOS:\n"
                for result in search_results:
                    product = result["product"]
                    product_context += f"- {product.get('name', 'Producto')}: ${product.get('price', 'N/A')} "
                    product_context += f"({product.get('category', 'Apple')})\n"
            
            # Mensaje completo para el agente
            full_message = request.message + context_message + product_context
            
            # Generar respuesta con Langroid
            response = agent.llm_response(full_message)
            
            # Limpiar y formatear la respuesta
            cleaned_response = response.content if hasattr(response, 'content') else str(response)
            
            return cleaned_response.strip()
            
        except Exception as e:
            logger.error(f"Error generando respuesta con Langroid: {str(e)}")
            return self._generate_fallback_response(request)
    
    def _generate_fallback_response(self, request: AgentRequest) -> str:
        """
        Genera respuesta de fallback cuando Langroid no está disponible
        """
        user_message = request.message.lower()
        
        if any(word in user_message for word in ["iphone", "teléfono", "móvil", "celular"]):
            return "Te ayudo con la selección del iPhone perfecto para ti. Basándome en tus necesidades, he encontrado algunas opciones que podrían interesarte. ¿Qué uso principal le darás al teléfono?"
        
        elif any(word in user_message for word in ["mac", "macbook", "imac", "computadora", "laptop"]):
            return "Excelente elección considerar un Mac. Los equipos Mac son perfectos para productividad, creatividad y rendimiento. ¿Para qué tipo de tareas necesitas la computadora principalmente?"
        
        elif any(word in user_message for word in ["ipad", "tablet"]):
            return "El iPad es una herramienta increíblemente versátil. Desde trabajo hasta entretenimiento y creatividad. Te ayudo a encontrar el modelo perfecto según tus necesidades."
        
        elif any(word in user_message for word in ["watch", "reloj", "apple watch"]):
            return "El Apple Watch es el compañero perfecto para tu iPhone. Te ayuda con fitness, salud, notificaciones y mucho más. ¿Qué características son más importantes para ti?"
        
        elif any(word in user_message for word in ["precio", "costo", "presupuesto", "barato", "económico"]):
            return "Entiendo que el presupuesto es importante. Apple ofrece opciones para diferentes rangos de precio. ¿Podrías decirme cuál es tu presupuesto aproximado y qué tipo de producto te interesa?"
        
        else:
            return "¡Hola! Soy tu asistente de Apple Store. Estoy aquí para ayudarte a encontrar el producto Apple perfecto para tus necesidades. ¿En qué puedo ayudarte hoy? ¿Te interesa algún iPhone, Mac, iPad, Apple Watch o accesorios?"
        
        if any(word in user_message for word in ["iphone", "teléfono", "móvil", "celular"]):
            return "Te ayudo con la selección del iPhone perfecto para ti. Basándome en tus necesidades, he encontrado algunas opciones que podrían interesarte. ¿Qué uso principal le darás al teléfono?"
        
        elif any(word in user_message for word in ["mac", "macbook", "imac", "computadora", "laptop"]):
            return "Excelente elección considerar un Mac. Los equipos Mac son perfectos para productividad, creatividad y rendimiento. ¿Para qué tipo de tareas necesitas la computadora principalmente?"
        
        elif any(word in user_message for word in ["ipad", "tablet"]):
            return "El iPad es una herramienta increíblemente versátil. Desde trabajo hasta entretenimiento y creatividad. Te ayudo a encontrar el modelo perfecto según tus necesidades."
        
        elif any(word in user_message for word in ["watch", "reloj", "apple watch"]):
            return "El Apple Watch es el compañero perfecto para tu iPhone. Te ayuda con fitness, salud, notificaciones y mucho más. ¿Qué características son más importantes para ti?"
        
        elif any(word in user_message for word in ["precio", "costo", "presupuesto", "barato", "económico"]):
            return "Entiendo que el presupuesto es importante. Apple ofrece opciones para diferentes rangos de precio. ¿Podrías decirme cuál es tu presupuesto aproximado y qué tipo de producto te interesa?"
        
        else:
            return "¡Hola! Soy tu asistente de Apple Store. Estoy aquí para ayudarte a encontrar el producto Apple perfecto para tus necesidades. ¿En qué puedo ayudarte hoy? ¿Te interesa algún iPhone, Mac, iPad, Apple Watch o accessorios?"
    
    def process_request(self, request: AgentRequest, config: Optional[AgentConfiguration] = None) -> AgentResponse:
        """
        Procesa una solicitud del agente y genera una respuesta completa
        """
        if config is None:
            config = self.default_config
        
        try:
            # Extraer contexto de conversación si está disponible
            context = ConversationContext()
            if request.context:
                context = ConversationContext(**request.context)
            
            # Generar recomendaciones de productos
            recommendations = self._extract_product_recommendations(request.message, context)
            
            # Generar respuesta del agente
            ai_response = self._generate_ai_response(request, config)
            
            # Calcular confianza (simplificado)
            confidence = 0.8 if recommendations else 0.6
            
            # Generar sugerencias de seguimiento
            follow_up_suggestions = self._generate_follow_up_suggestions(request.message, recommendations)
            
            response = AgentResponse(
                response=ai_response,
                agent_role=request.agent_role,
                recommendations=recommendations,
                confidence=confidence,
                sources=["Qdrant Vector Search", "Apple Product Database"],
                follow_up_suggestions=follow_up_suggestions,
                metadata={
                    "request_id": datetime.now().isoformat(),
                    "processing_time": "~1.2s",
                    "model_used": "apple_store_assistant_v1"
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error procesando solicitud del agente: {str(e)}")
            # Respuesta de fallback
            return AgentResponse(
                response="Disculpa, estoy experimentando algunas dificultades técnicas. ¿Podrías intentar reformular tu pregunta?",
                agent_role=request.agent_role,
                confidence=0.3,
                metadata={"error": str(e)}
            )
    
    def _generate_follow_up_suggestions(self, user_message: str, recommendations: List[ProductRecommendation]) -> List[str]:
        """
        Genera sugerencias de seguimiento basadas en el contexto
        """
        suggestions = []
        
        if recommendations:
            suggestions.append("¿Te gustaría conocer más detalles sobre alguna de estas opciones?")
            suggestions.append("¿Quieres que compare las especificaciones de estos productos?")
        
        user_message_lower = user_message.lower()
        
        if "precio" in user_message_lower or "costo" in user_message_lower:
            suggestions.append("¿Te interesa conocer las opciones de financiamiento disponibles?")
        
        if any(word in user_message_lower for word in ["uso", "trabajo", "estudios"]):
            suggestions.append("¿Podrías contarme más sobre el uso específico que le darás?")
        
        if not suggestions:
            suggestions = [
                "¿Hay alguna característica específica que te interese más?",
                "¿Tienes alguna preferencia de color o almacenamiento?",
                "¿Te gustaría ver accesorios complementarios?"
            ]
        
        return suggestions[:3]

# Instancia global del servicio
ai_agent_service = AIAgentService()
