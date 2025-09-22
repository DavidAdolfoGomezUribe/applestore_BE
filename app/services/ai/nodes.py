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
    
    async def search_products(self, query: str, limit: int = 10) -> List[Dict]:
        """Busca productos relevantes usando Qdrant con búsqueda híbrida"""
        try:
            logger.info(f"Iniciando búsqueda en Qdrant para: '{query}' (limit: {limit})")
            
            from qdrant_client import QdrantClient
            from qdrant_client.models import Filter, FieldCondition, MatchText, MatchAny
            import os
            
            # Configurar Qdrant
            qdrant_host = os.getenv("QDRANT_HOST", "localhost")
            qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
            collection_name = os.getenv("QDRANT_COLLECTION", "products_kb")
            
            logger.debug(f"Conectando a Qdrant: {qdrant_host}:{qdrant_port}, colección: {collection_name}")
            
            client = QdrantClient(host=qdrant_host, port=qdrant_port)
            
            # Verificar que la colección existe
            collections = client.get_collections()
            logger.debug(f"Colecciones disponibles: {[c.name for c in collections.collections]}")
            
            # Generar embedding para la consulta
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('intfloat/multilingual-e5-small')  # Mismo modelo usado en carga
            logger.debug("Generando embedding para la consulta")
            query_vector = model.encode(query).tolist()
            logger.debug(f"Vector generado de dimensión: {len(query_vector)}")
            
            # Preparar filtro de palabras clave para mejorar la búsqueda
            query_lower = query.lower()
            keywords = []
            
            # Extraer palabras clave importantes
            if "iphone" in query_lower:
                keywords.append("iphone")
            if "ipad" in query_lower:
                keywords.append("ipad")
            if "mac" in query_lower:
                keywords.append("mac")
            if "airpods" in query_lower:
                keywords.append("airpods")
            if "watch" in query_lower:
                keywords.append("watch")
            if "pro" in query_lower:
                keywords.append("pro")
            if "max" in query_lower:
                keywords.append("max")
            if "15" in query_lower:
                keywords.append("15")
            if "14" in query_lower:
                keywords.append("14")
            if "13" in query_lower:
                keywords.append("13")
                
            logger.debug(f"Palabras clave extraídas: {keywords}")
            
            # Realizar búsqueda principal con vectores
            logger.debug("Ejecutando búsqueda vectorial en Qdrant")
            search_result = client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit * 2,  # Obtener más resultados para filtrar después
                with_payload=True
            )
            
            logger.info(f"Qdrant devolvió {len(search_result)} resultados vectoriales")
            
            # Si tenemos palabras clave específicas, intentar búsqueda por filtro también
            if keywords:
                try:
                    logger.debug(f"Realizando búsqueda adicional por palabras clave: {keywords}")
                    
                    # Buscar productos que contengan las palabras clave en el nombre
                    keyword_results = []
                    for keyword in keywords:
                        keyword_search = client.search(
                            collection_name=collection_name,
                            query_vector=query_vector,
                            query_filter=Filter(
                                must=[
                                    FieldCondition(
                                        key="name",
                                        match=MatchText(text=keyword)
                                    )
                                ]
                            ),
                            limit=10,
                            with_payload=True
                        )
                        keyword_results.extend(keyword_search)
                    
                    logger.debug(f"Búsqueda por palabras clave encontró {len(keyword_results)} resultados adicionales")
                    
                    # Combinar resultados y eliminar duplicados
                    all_results = list(search_result) + keyword_results
                    seen_ids = set()
                    unique_results = []
                    
                    for result in all_results:
                        if result.id not in seen_ids:
                            seen_ids.add(result.id)
                            unique_results.append(result)
                            
                    search_result = unique_results[:limit]
                    logger.info(f"Resultados combinados y únicos: {len(search_result)}")
                    
                except Exception as e:
                    logger.warning(f"Error en búsqueda por palabras clave: {e}, usando solo búsqueda vectorial")
            
            # Formatear resultados
            products = []
            for i, point in enumerate(search_result):
                payload = point.payload
                product = {
                    "nombre": payload.get("name", ""),
                    "precio": payload.get("price", ""),
                    "descripcion": payload.get("description", ""),
                    "categoria": payload.get("category", ""),
                    "score": point.score
                }
                products.append(product)
                logger.debug(f"Producto {i+1}: {payload.get('name', '')} - Score: {point.score}")
            
            logger.info(f"Retornando {len(products)} productos formateados")
            return products
            
        except Exception as e:
            logger.error(f"Error en búsqueda de productos: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def format_products_for_context(self, products: List[Dict[str, Any]]) -> str:
        """Formatea productos para incluir en el contexto del agente"""
        logger.info(f"Formateando {len(products)} productos para contexto")
        
        if not products:
            logger.warning("No hay productos para formatear")
            return "No se encontraron productos relevantes."
        
        context = "Productos relevantes encontrados:\n\n"
        for i, product in enumerate(products[:3], 1):
            logger.debug(f"Formateando producto {i}: {product.get('nombre', 'Sin nombre')}")
            
            context += f"{i}. {product.get('nombre', 'Producto Apple')}\n"
            context += f"   - Categoría: {product.get('categoria', 'N/A')}\n"
            context += f"   - Precio: ${product.get('precio', 'N/A')}\n"
            context += f"   - Relevancia: {product.get('score', 0):.2f}\n"
            
            if product.get('descripcion'):
                context += f"   - Descripción: {product['descripcion'][:100]}...\n"
            
            context += "\n"
        
        logger.info(f"Contexto generado: {len(context)} caracteres")
        logger.debug(f"Contexto completo: {context[:200]}...")
        
        return context
        
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
                logger.info(f"Agregando contexto al prompt: {len(context)} caracteres")
                full_prompt += f"{context}\n\n"
            else:
                logger.warning("No hay contexto para agregar al prompt")
            
            full_prompt += f"Usuario: {message}\nAsistente:"
            
            logger.info(f"Prompt completo preparado: {len(full_prompt)} caracteres")
            logger.debug(f"Prompt final (primeros 500 chars): {full_prompt[:500]}...")
            
            # Generar respuesta
            response = self.gemini_model.generate_content(
                full_prompt,
                generation_config=self.generation_config
            )
            
            response_text = response.text if response.text else "No pude generar una respuesta."
            logger.info(f"Respuesta generada: {len(response_text)} caracteres")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error generando respuesta Gemini: {str(e)}")
            return f"Disculpa, hubo un error procesando tu consulta con Gemini: {str(e)}"
    
    def prepare_full_context(self, 
                           message: str,
                           product_context: Optional[str] = None,
                           conversation_history: Optional[List[Dict]] = None,
                           additional_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Prepara el contexto completo combinando historial, productos y contexto adicional
        """
        logger.info("Preparando contexto completo para el modelo")
        context_parts = []
        
        # Agregar historial de conversación si existe
        if conversation_history:
            logger.info(f"Agregando historial de {len(conversation_history)} mensajes al contexto")
            context_parts.append("=== HISTORIAL DE CONVERSACIÓN ===")
            for msg in conversation_history[-5:]:  # Solo últimos 5 mensajes
                role = "Usuario" if msg.get("role") == "user" else "Asistente"
                content = msg.get("content", "")
                context_parts.append(f"{role}: {content}")
            context_parts.append("=== FIN DEL HISTORIAL ===\n")
            logger.debug(f"Contexto de historial preparado: {len(context_parts)} líneas")
        else:
            logger.info("No hay historial de conversación para agregar al contexto")
        
        # Agregar contexto de productos si existe
        if product_context:
            logger.info("Agregando contexto de productos al prompt")
            logger.debug(f"Contexto de productos: {product_context[:200]}...")
            context_parts.append("=== PRODUCTOS RELACIONADOS ===")
            context_parts.append(product_context)
            context_parts.append("=== FIN DE PRODUCTOS ===\n")
        else:
            logger.warning("No hay contexto de productos para agregar")
        
        # Agregar contexto adicional si existe
        if additional_context:
            user_preferences = additional_context.get("user_preferences")
            if user_preferences:
                context_parts.append("=== PREFERENCIAS DEL USUARIO ===")
                context_parts.append(str(user_preferences))
                context_parts.append("=== FIN DE PREFERENCIAS ===\n")
        
        final_context = "\n".join(context_parts) if context_parts else None
        logger.info(f"Contexto final preparado: {len(final_context) if final_context else 0} caracteres")
        
        return final_context

    async def process_message(self, 
                            message: str, 
                            chat_id: Optional[int] = None,
                            user_id: Optional[int] = None,
                            include_product_search: bool = True,
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Procesa un mensaje y genera respuesta completa
        """
        start_time = time.time()
        
        try:
            product_context = None
            products = []
            
            # Búsqueda de productos si está habilitada
            if include_product_search:
                logger.info(f"Realizando búsqueda de productos para: '{message}'")
                products = await self.search_products(message)
                logger.info(f"Productos encontrados: {len(products)}")
                
                if products:
                    logger.debug(f"Primeros 2 productos: {products[:2]}")
                    product_context = self.format_products_for_context(products)
                    logger.info(f"Contexto de productos generado: {len(product_context)} caracteres")
                else:
                    logger.warning("No se encontraron productos relevantes")
            
            # Preparar contexto completo
            full_context = self.prepare_full_context(
                message=message,
                product_context=product_context,
                conversation_history=context.get("conversation_history", []) if context else [],
                additional_context=context
            )
            
            # Generar respuesta según proveedor
            if self.config.provider == AIProvider.OPENAI:
                response_text = await self.generate_response_openai(message, full_context)
            elif self.config.provider == AIProvider.GEMINI:
                response_text = await self.generate_response_gemini(message, full_context)
            else:
                response_text = "Proveedor de IA no soportado actualmente."
            
            response_time = time.time() - start_time
            
            # Tracking de costos
            await cost_tracker.track_usage(
                agent_type=self.config.name.lower().replace(" ", "_"),
                model=self.config.model,
                provider=self.config.provider,
                input_text=f"{full_context or ''}\n{message}",
                output_text=response_text,
                response_time=response_time,
                chat_id=chat_id,
                user_id=user_id,
                success=True
            )
            
            return {
                "response": response_text,
                "products": products,
                "context_used": bool(full_context),
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
