"""
Nodos base para agentes especializados usando Langroid
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

import langroid as lr
from langroid.language_models.openai_gpt import OpenAIGPTConfig
from langroid.language_models.base import LLMConfig
import google.generativeai as genai

from services.ai.config import ai_config, AIProvider, ModelType, AgentConfig
from services.ai.cost_tracker import cost_tracker
from services.qdrant.vector_sync_service import convert_for_qdrant
from sentence_transformers import SentenceTransformer
import requests
import os

logger = logging.getLogger(__name__)

class BaseAgentNode:
    """Nodo base para todos los agentes especializados"""
    
    def __init__(self, agent_config: AgentConfig):
        self.config = agent_config
        self.agent = None
        self.llm_config = None
        self.setup_llm()
        self.setup_agent()
        
        # Para búsqueda semántica
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
        self.collection_name = os.getenv("QDRANT_COLLECTION", "products_kb")
    
    def setup_llm(self):
        """Configura el modelo de lenguaje según el proveedor"""
        try:
            if self.config.provider == AIProvider.OPENAI:
                self.llm_config = OpenAIGPTConfig(
                    chat_model=self.config.model.value,
                    api_key=ai_config.openai_api_key,
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens,
                    timeout=30
                )
            
            elif self.config.provider == AIProvider.GEMINI:
                # Para Gemini, configuraremos manualmente
                genai.configure(api_key=ai_config.gemini_api_key)
                self.gemini_model = genai.GenerativeModel(self.config.model.value)
                
                # Configuración personalizada para Gemini
                self.generation_config = genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens,
                )
                
        except Exception as e:
            logger.error(f"Error configurando LLM: {str(e)}")
            raise
    
    def setup_agent(self):
        """Configura el agente Langroid"""
        try:
            if self.config.provider == AIProvider.OPENAI:
                # Usar Langroid estándar para OpenAI
                self.agent = lr.ChatAgent(
                    lr.ChatAgentConfig(
                        name=self.config.name,
                        llm=self.llm_config,
                        system_message=self.config.system_prompt,
                    )
                )
            else:
                # Para Gemini, usaremos una implementación custom
                self.agent = None  # Manejaremos directamente
                
        except Exception as e:
            logger.error(f"Error configurando agente: {str(e)}")
            raise
    
    async def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Busca productos usando Qdrant"""
        try:
            query_vector = self.embedding_model.encode(query).tolist()
            
            search_payload = {
                "vector": query_vector,
                "limit": limit,
                "score_threshold": 0.3,
                "with_payload": True
            }
            
            url = f"{self.qdrant_url}/collections/{self.collection_name}/points/search"
            response = requests.post(url, json=search_payload, timeout=10)
            response.raise_for_status()
            
            results = response.json().get("result", [])
            return [{"score": r["score"], "product": r["payload"]} for r in results]
            
        except Exception as e:
            logger.error(f"Error en búsqueda de productos: {str(e)}")
            return []
    
    def format_products_for_context(self, products: List[Dict[str, Any]]) -> str:
        """Formatea productos para incluir en el contexto del agente"""
        if not products:
            return "No se encontraron productos relevantes."
        
        context = "Productos relevantes encontrados:\n\n"
        for i, item in enumerate(products[:3], 1):
            product = item["product"]
            score = item["score"]
            
            context += f"{i}. {product.get('name', 'Producto Apple')}\n"
            context += f"   - Categoría: {product.get('category', 'N/A')}\n"
            context += f"   - Precio: ${product.get('price', 'N/A')}\n"
            context += f"   - Relevancia: {score:.2f}\n"
            
            if product.get('specifications'):
                specs = product['specifications']
                if isinstance(specs, dict):
                    context += f"   - Especificaciones clave: {', '.join(list(specs.keys())[:3])}\n"
            
            context += "\n"
        
        return context
    
    async def generate_response_openai(self, message: str, context: Optional[str] = None) -> str:
        """Genera respuesta usando OpenAI via Langroid"""
        try:
            if not self.agent:
                raise Exception("Agente OpenAI no configurado")
            
            # Preparar mensaje con contexto
            full_message = message
            if context:
                full_message = f"{context}\n\nConsulta del usuario: {message}"
            
            # Generar respuesta
            response = self.agent.llm_response(full_message)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            logger.error(f"Error generando respuesta OpenAI: {str(e)}")
            return f"Disculpa, hubo un error procesando tu consulta: {str(e)}"
    
    async def generate_response_gemini(self, message: str, context: Optional[str] = None) -> str:
        """Genera respuesta usando Gemini directamente"""
        try:
            if not hasattr(self, 'gemini_model'):
                raise Exception("Modelo Gemini no configurado")
            
            # Preparar prompt completo
            full_prompt = f"{self.config.system_prompt}\n\n"
            if context:
                full_prompt += f"{context}\n\n"
            full_prompt += f"Usuario: {message}\nAsistente:"
            
            # Generar respuesta
            response = self.gemini_model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )
            
            return response.text if response.text else "No pude generar una respuesta."
            
        except Exception as e:
            logger.error(f"Error generando respuesta Gemini: {str(e)}")
            return f"Disculpa, hubo un error procesando tu consulta con Gemini: {str(e)}"
    
    async def process_message(self, 
                            message: str, 
                            chat_id: Optional[int] = None,
                            user_id: Optional[int] = None,
                            include_product_search: bool = True) -> Dict[str, Any]:
        """
        Procesa un mensaje y genera respuesta completa
        """
        start_time = time.time()
        
        try:
            context = None
            products = []
            
            # Búsqueda de productos si está habilitada
            if include_product_search:
                products = await self.search_products(message)
                if products:
                    context = self.format_products_for_context(products)
            
            # Generar respuesta según proveedor
            if self.config.provider == AIProvider.OPENAI:
                response_text = await self.generate_response_openai(message, context)
            elif self.config.provider == AIProvider.GEMINI:
                response_text = await self.generate_response_gemini(message, context)
            else:
                response_text = "Proveedor de IA no soportado actualmente."
            
            response_time = time.time() - start_time
            
            # Tracking de costos
            await cost_tracker.track_usage(
                agent_type=self.config.name.lower().replace(" ", "_"),
                model=self.config.model,
                provider=self.config.provider,
                input_text=f"{context or ''}\n{message}",
                output_text=response_text,
                response_time=response_time,
                chat_id=chat_id,
                user_id=user_id,
                success=True
            )
            
            return {
                "response": response_text,
                "products": products,
                "context_used": context is not None,
                "response_time": response_time,
                "agent_type": self.config.name,
                "model_used": self.config.model.value,
                "success": True
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            error_message = f"Error procesando mensaje: {str(e)}"
            
            # Tracking de error
            await cost_tracker.track_usage(
                agent_type=self.config.name.lower().replace(" ", "_"),
                model=self.config.model,
                provider=self.config.provider,
                input_text=message,
                output_text="",
                response_time=response_time,
                chat_id=chat_id,
                user_id=user_id,
                success=False,
                error_message=str(e)
            )
            
            logger.error(f"Error en {self.config.name}: {str(e)}")
            return {
                "response": "Disculpa, estoy experimentando dificultades técnicas. ¿Podrías reformular tu pregunta?",
                "products": [],
                "context_used": False,
                "response_time": response_time,
                "agent_type": self.config.name,
                "model_used": self.config.model.value,
                "success": False,
                "error": str(e)
            }

class SalesAssistantNode(BaseAgentNode):
    """Nodo especializado en ventas"""
    
    def __init__(self):
        agent_config = ai_config.get_agent_config("sales_assistant")
        super().__init__(agent_config)
    
    async def process_message(self, message: str, **kwargs) -> Dict[str, Any]:
        """Procesa mensaje con enfoque en ventas"""
        result = await super().process_message(message, **kwargs)
        
        # Enriquecer con lógica específica de ventas
        if result["success"] and result["products"]:
            # Agregar llamadas a la acción
            result["response"] += "\n\n¿Te gustaría conocer más detalles sobre alguno de estos productos o prefieres que te ayude a comparar opciones?"
            
            # Agregar información de disponibilidad (simulada)
            for product in result["products"]:
                product["availability"] = "En stock"
                product["shipping"] = "Envío gratis"
        
        return result

class TechnicalSupportNode(BaseAgentNode):
    """Nodo especializado en soporte técnico"""
    
    def __init__(self):
        agent_config = ai_config.get_agent_config("technical_support")
        super().__init__(agent_config)
    
    async def process_message(self, message: str, **kwargs) -> Dict[str, Any]:
        """Procesa mensaje con enfoque técnico"""
        result = await super().process_message(message, **kwargs)
        
        # Enriquecer con lógica específica de soporte
        if result["success"]:
            # Agregar recursos de ayuda
            result["help_resources"] = [
                "📞 Soporte telefónico: 800-APL-CARE",
                "💬 Chat en vivo disponible 24/7",
                "📖 Consulta nuestra base de conocimientos",
                "🔧 Programa una cita en Apple Store"
            ]
        
        return result

class ProductExpertNode(BaseAgentNode):
    """Nodo especializado en conocimiento de productos"""
    
    def __init__(self):
        agent_config = ai_config.get_agent_config("product_expert")
        super().__init__(agent_config)
    
    async def process_message(self, message: str, **kwargs) -> Dict[str, Any]:
        """Procesa mensaje con enfoque en expertise de productos"""
        result = await super().process_message(message, **kwargs)
        
        # Enriquecer con comparaciones detalladas
        if result["success"] and len(result["products"]) > 1:
            result["comparison_available"] = True
            result["response"] += "\n\n¿Te gustaría que haga una comparación detallada entre estos modelos?"
        
        return result

class GeneralAssistantNode(BaseAgentNode):
    """Nodo de asistente general"""
    
    def __init__(self):
        agent_config = ai_config.get_agent_config("general_assistant")
        super().__init__(agent_config)
    
    async def process_message(self, message: str, **kwargs) -> Dict[str, Any]:
        """Procesa mensaje con enfoque general"""
        result = await super().process_message(message, **kwargs)
        
        # Agregar sugerencias de especialistas
        if result["success"]:
            message_lower = message.lower()
            specialists = []
            
            if any(word in message_lower for word in ["problema", "error", "no funciona", "ayuda técnica"]):
                specialists.append("🔧 Especialista en Soporte Técnico")
            
            if any(word in message_lower for word in ["comprar", "precio", "recomendar", "mejor opción"]):
                specialists.append("💼 Especialista en Ventas")
            
            if any(word in message_lower for word in ["especificaciones", "comparar", "diferencias"]):
                specialists.append("🎯 Experto en Productos")
            
            if specialists:
                result["specialist_suggestions"] = specialists
        
        return result

# Factory para crear nodos
class AgentNodeFactory:
    """Factory para crear diferentes tipos de nodos de agentes"""
    
    @staticmethod
    def create_node(agent_type: str) -> BaseAgentNode:
        """Crea un nodo según el tipo especificado"""
        node_mapping = {
            "sales_assistant": SalesAssistantNode,
            "technical_support": TechnicalSupportNode,
            "product_expert": ProductExpertNode,
            "general_assistant": GeneralAssistantNode
        }
        
        node_class = node_mapping.get(agent_type)
        if not node_class:
            raise ValueError(f"Tipo de agente no soportado: {agent_type}")
        
        return node_class()
    
    @staticmethod
    def get_available_agent_types() -> List[str]:
        """Retorna tipos de agentes disponibles"""
        return list(ai_config.agent_configs.keys())
