"""
Sistema de detección de intenciones y routing para bots
Maneja triggers y decide qué agente usar o si responder directamente
"""
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

class IntentType(str, Enum):
    """Tipos de intenciones detectables"""
    GREETING = "greeting"
    PRODUCT_INQUIRY = "product_inquiry"
    PRICE_QUESTION = "price_question"
    TECHNICAL_SUPPORT = "technical_support"
    COMPARISON = "comparison"
    PURCHASE_INTENT = "purchase_intent"
    COMPLAINT = "complaint"
    GENERAL_INFO = "general_info"
    GOODBYE = "goodbye"
    UNKNOWN = "unknown"

class BotType(str, Enum):
    """Tipos de bots disponibles"""
    WHATSAPP_BOT = "whatsapp_bot"
    WEB_CHAT_BOT = "web_chat_bot"
    TELEGRAM_BOT = "telegram_bot"

class ResponseType(str, Enum):
    """Tipos de respuesta"""
    DIRECT_RESPONSE = "direct_response"
    AGENT_REQUIRED = "agent_required"
    ESCALATE_TO_HUMAN = "escalate_to_human"

@dataclass
class TriggerRule:
    """Regla de trigger para detección de intenciones"""
    intent: IntentType
    keywords: List[str]
    patterns: List[str]
    confidence_boost: float = 0.0
    bot_specific: Optional[BotType] = None

@dataclass
class DirectResponse:
    """Respuesta directa sin necesidad de agente"""
    intent: IntentType
    response_templates: List[str]
    requires_product_data: bool = False
    followup_suggestions: List[str] = None

@dataclass
class IntentResult:
    """Resultado de detección de intención"""
    intent: IntentType
    confidence: float
    detected_keywords: List[str]
    suggested_agent: Optional[str] = None
    response_type: ResponseType = ResponseType.AGENT_REQUIRED

class IntentDetector:
    """Detector de intenciones y clasificador de mensajes"""
    
    def __init__(self):
        self.setup_triggers()
        self.setup_direct_responses()
        self.setup_agent_routing()
    
    def setup_triggers(self):
        """Configura reglas de triggers para cada intención"""
        self.trigger_rules = [
            # Saludos
            TriggerRule(
                intent=IntentType.GREETING,
                keywords=["hola", "buenos días", "buenas tardes", "buenas noches", "hey", "hello", "hi"],
                patterns=[r"\b(hola|hi|hello|hey)\b", r"buenos\s+(días|tardes|noches)"]
            ),
            
            # Consultas de productos
            TriggerRule(
                intent=IntentType.PRODUCT_INQUIRY,
                keywords=["iphone", "mac", "macbook", "ipad", "apple watch", "airpods", "producto", "modelo"],
                patterns=[r"\b(iphone|mac|ipad|watch|airpods)\b", r"qué\s+me\s+recomiendas?", r"necesito\s+un?"]
            ),
            
            # Preguntas de precio
            TriggerRule(
                intent=IntentType.PRICE_QUESTION,
                keywords=["precio", "costo", "vale", "cuesta", "barato", "económico", "presupuesto"],
                patterns=[r"\bcuánto\s+(cuesta|vale|es)", r"\bprecio\b", r"\bcosto\b", r"presupuesto"]
            ),
            
            # Soporte técnico
            TriggerRule(
                intent=IntentType.TECHNICAL_SUPPORT,
                keywords=["problema", "error", "no funciona", "ayuda", "configurar", "instalar", "actualizar"],
                patterns=[r"\bno\s+funciona\b", r"\bproblema\s+con\b", r"\berror\b", r"cómo\s+(configurar|instalar)"]
            ),
            
            # Comparaciones
            TriggerRule(
                intent=IntentType.COMPARISON,
                keywords=["comparar", "diferencia", "mejor", "vs", "versus", "entre"],
                patterns=[r"\bvs\b", r"\bversus\b", r"diferencia\s+entre", r"mejor\s+que", r"comparar"]
            ),
            
            # Intención de compra
            TriggerRule(
                intent=IntentType.PURCHASE_INTENT,
                keywords=["comprar", "adquirir", "pedido", "ordenar", "donde compro", "stock", "disponible"],
                patterns=[r"\bcomprar\b", r"\badquirir\b", r"hacer\s+pedido", r"está\s+disponible", r"en\s+stock"]
            ),
            
            # Quejas
            TriggerRule(
                intent=IntentType.COMPLAINT,
                keywords=["queja", "mal servicio", "problema", "insatisfecho", "devolver", "reembolso"],
                patterns=[r"\bqueja\b", r"mal\s+servicio", r"\bdevolver\b", r"\breembolso\b"]
            ),
            
            # Despedidas
            TriggerRule(
                intent=IntentType.GOODBYE,
                keywords=["adiós", "gracias", "hasta luego", "bye", "chao", "nos vemos"],
                patterns=[r"\b(adiós|bye|chao)\b", r"hasta\s+luego", r"nos\s+vemos", r"gracias\s+por"]
            ),
            
            # Información general
            TriggerRule(
                intent=IntentType.GENERAL_INFO,
                keywords=["horarios", "ubicación", "tienda", "contacto", "información", "apple store"],
                patterns=[r"\bhorarios?\b", r"\bubicación\b", r"\btienda\b", r"apple\s+store"]
            )
        ]
    
    def setup_direct_responses(self):
        """Configura respuestas directas que no requieren agentes"""
        self.direct_responses = {
            IntentType.GREETING: DirectResponse(
                intent=IntentType.GREETING,
                response_templates=[
                    "¡Hola! 👋 Bienvenido a Apple Store. ¿En qué puedo ayudarte hoy?",
                    "¡Buenos días! Soy tu asistente virtual de Apple. ¿Qué producto te interesa?",
                    "¡Hola! ¿Buscas algún producto Apple en particular o tienes alguna pregunta?"
                ],
                followup_suggestions=[
                    "Ver productos iPhone",
                    "Consultar sobre Mac",
                    "Información sobre iPad",
                    "Hablar con un especialista"
                ]
            ),
            
            IntentType.GOODBYE: DirectResponse(
                intent=IntentType.GOODBYE,
                response_templates=[
                    "¡Gracias por contactarnos! 😊 Si necesitas algo más, estaré aquí para ayudarte.",
                    "¡Hasta pronto! Espero haber sido de ayuda. No dudes en volver si tienes más preguntas.",
                    "¡Que tengas un excelente día! Gracias por elegir Apple Store. 🍎"
                ]
            ),
            
            IntentType.GENERAL_INFO: DirectResponse(
                intent=IntentType.GENERAL_INFO,
                response_templates=[
                    """📍 **Información de Apple Store:**
                    
🕒 **Horarios:** Lunes a Domingo 9:00 AM - 9:00 PM
📞 **Teléfono:** +1 (800) APL-CARE
💬 **Chat:** Disponible 24/7
🌐 **Web:** apple.com/mx
📧 **Email:** soporte@apple.com

¿Hay algo específico sobre nuestros servicios que te gustaría saber?"""
                ],
                followup_suggestions=[
                    "Ver ubicaciones de tiendas",
                    "Servicios disponibles",
                    "Programa una cita",
                    "Soporte técnico"
                ]
            )
        }
    
    def setup_agent_routing(self):
        """Configura routing hacia agentes específicos"""
        self.agent_routing = {
            IntentType.PRODUCT_INQUIRY: "sales_assistant",
            IntentType.PRICE_QUESTION: "sales_assistant", 
            IntentType.COMPARISON: "product_expert",
            IntentType.PURCHASE_INTENT: "sales_assistant",
            IntentType.TECHNICAL_SUPPORT: "technical_support",
            IntentType.COMPLAINT: "technical_support",
            IntentType.UNKNOWN: "general_assistant"
        }
    
    def detect_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> IntentResult:
        """
        Detecta la intención del mensaje
        """
        message_lower = message.lower()
        intent_scores = {}
        detected_keywords = []
        
        # Evaluar cada regla de trigger
        for rule in self.trigger_rules:
            score = 0.0
            rule_keywords = []
            
            # Puntaje por keywords
            for keyword in rule.keywords:
                if keyword.lower() in message_lower:
                    score += 1.0
                    rule_keywords.append(keyword)
            
            # Puntaje por patrones regex
            for pattern in rule.patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    score += 1.5  # Los patrones tienen más peso
                    
            # Aplicar boost de confianza
            score += rule.confidence_boost
            
            # Normalizar por cantidad de elementos evaluados
            max_possible = len(rule.keywords) + len(rule.patterns) * 1.5 + rule.confidence_boost
            if max_possible > 0:
                score = score / max_possible
            
            if score > 0:
                intent_scores[rule.intent] = score
                detected_keywords.extend(rule_keywords)
        
        # Determinar la intención con mayor puntaje
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
        else:
            best_intent = IntentType.UNKNOWN
            confidence = 0.0
        
        # Determinar tipo de respuesta y agente sugerido
        response_type = ResponseType.AGENT_REQUIRED
        suggested_agent = self.agent_routing.get(best_intent)
        
        # Si hay respuesta directa disponible y confianza alta
        if best_intent in self.direct_responses and confidence > 0.7:
            response_type = ResponseType.DIRECT_RESPONSE
            suggested_agent = None
        
        # Casos especiales que requieren escalamiento
        if best_intent == IntentType.COMPLAINT and confidence > 0.8:
            response_type = ResponseType.ESCALATE_TO_HUMAN
        
        return IntentResult(
            intent=best_intent,
            confidence=confidence,
            detected_keywords=list(set(detected_keywords)),
            suggested_agent=suggested_agent,
            response_type=response_type
        )
    
    def get_direct_response(self, intent: IntentType) -> Optional[DirectResponse]:
        """Obtiene respuesta directa para una intención"""
        return self.direct_responses.get(intent)

class BotOrchestrator:
    """Orquestador principal que maneja el flujo entre bots y agentes"""
    
    def __init__(self):
        self.intent_detector = IntentDetector()
        self.conversation_memory = {}  # Memoria por chat_id
        
    def process_message(self, 
                       message: str,
                       bot_type: BotType,
                       chat_id: int,
                       user_id: Optional[int] = None,
                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Procesa un mensaje y determina la respuesta apropiada
        """
        # Detectar intención
        intent_result = self.intent_detector.detect_intent(message, context)
        
        # Actualizar memoria de conversación
        if chat_id not in self.conversation_memory:
            self.conversation_memory[chat_id] = {
                "messages": [],
                "last_intent": None,
                "agent_context": {},
                "created_at": datetime.now()
            }
        
        self.conversation_memory[chat_id]["messages"].append({
            "message": message,
            "intent": intent_result.intent,
            "timestamp": datetime.now()
        })
        self.conversation_memory[chat_id]["last_intent"] = intent_result.intent
        
        # Construir respuesta
        response = {
            "message": message,
            "intent": intent_result.intent.value,
            "confidence": intent_result.confidence,
            "detected_keywords": intent_result.detected_keywords,
            "response_type": intent_result.response_type.value,
            "bot_type": bot_type.value,
            "chat_id": chat_id,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Manejar según tipo de respuesta
        if intent_result.response_type == ResponseType.DIRECT_RESPONSE:
            direct_response = self.intent_detector.get_direct_response(intent_result.intent)
            if direct_response:
                import random
                response["direct_response"] = random.choice(direct_response.response_templates)
                response["followup_suggestions"] = direct_response.followup_suggestions
                response["requires_agent"] = False
        
        elif intent_result.response_type == ResponseType.AGENT_REQUIRED:
            response["suggested_agent"] = intent_result.suggested_agent
            response["requires_agent"] = True
            response["agent_context"] = {
                "previous_intent": self.conversation_memory[chat_id].get("last_intent"),
                "conversation_length": len(self.conversation_memory[chat_id]["messages"]),
                "bot_type": bot_type.value
            }
        
        elif intent_result.response_type == ResponseType.ESCALATE_TO_HUMAN:
            response["escalate_to_human"] = True
            response["requires_agent"] = False
            response["direct_response"] = "He detectado que podrías necesitar asistencia especializada. Te voy a conectar con uno de nuestros representantes humanos que podrá ayudarte mejor."
        
        return response
    
    def get_conversation_context(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene contexto de conversación para un chat"""
        return self.conversation_memory.get(chat_id)
    
    def clear_conversation_memory(self, chat_id: int):
        """Limpia memoria de conversación para un chat"""
        if chat_id in self.conversation_memory:
            del self.conversation_memory[chat_id]
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de routing"""
        total_conversations = len(self.conversation_memory)
        intent_counts = {}
        
        for chat_data in self.conversation_memory.values():
            for msg_data in chat_data["messages"]:
                intent = msg_data["intent"]
                intent_counts[intent.value] = intent_counts.get(intent.value, 0) + 1
        
        return {
            "total_conversations": total_conversations,
            "intent_distribution": intent_counts,
            "most_common_intent": max(intent_counts, key=intent_counts.get) if intent_counts else None
        }

# Instancia global del orquestador
bot_orchestrator = BotOrchestrator()
