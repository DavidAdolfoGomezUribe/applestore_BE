"""
Configuración central para el sistema de agentes IA
Maneja diferentes proveedores (Gemini, OpenAI) y tracking de costos
"""
import os
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AIProvider(str, Enum):
    """Proveedores de IA disponibles"""
    GEMINI = "gemini"
    OPENAI = "openai"

class ModelType(str, Enum):
    """Tipos de modelos disponibles"""
    # Gemini models
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    
    # OpenAI models
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4O = "gpt-4o"
    

class CostConfig(BaseModel):
    """Configuración de costos por modelo"""
    input_cost_per_1k_tokens: float
    output_cost_per_1k_tokens: float
    max_tokens: int
    context_window: int

class AgentConfig(BaseModel):
    """Configuración de un agente específico"""
    name: str
    description: str
    provider: AIProvider
    model: ModelType
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=4000)
    system_prompt: str
    cost_config: CostConfig
    enabled: bool = True

class AIConfiguration:
    """Configuración central del sistema de IA"""
    
    def __init__(self):
        # Configurar provider primero
        self.current_provider = AIProvider(os.getenv("DEFAULT_AI_PROVIDER", "gemini"))
        
        # API Keys
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Redis para tracking de costos
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Configuración de costos
        self.cost_tracking_enabled = os.getenv("COST_TRACKING_ENABLED", "true").lower() == "true"
        self.daily_cost_limit = float(os.getenv("DAILY_COST_LIMIT", "50.0"))
        self.monthly_cost_limit = float(os.getenv("MONTHLY_COST_LIMIT", "1000.0"))
        
        # Configurar después de que current_provider esté definido
        self.setup_cost_configs()
        self.setup_agent_configs()
    
    def setup_cost_configs(self):
        """Configuración de costos por modelo (precios actualizados 2024)"""
        self.cost_configs = {
            # Gemini (precios aproximados)
            ModelType.GEMINI_PRO: CostConfig(
                input_cost_per_1k_tokens=0.0005,
                output_cost_per_1k_tokens=0.0015,
                max_tokens=8192,
                context_window=32000
            ),
            ModelType.GEMINI_1_5_PRO: CostConfig(
                input_cost_per_1k_tokens=0.0025,
                output_cost_per_1k_tokens=0.0075,
                max_tokens=8192,
                context_window=1000000
            ),
            ModelType.GEMINI_1_5_FLASH: CostConfig(
                input_cost_per_1k_tokens=0.00035,
                output_cost_per_1k_tokens=0.00105,
                max_tokens=8192,
                context_window=1000000
            ),
            
            # OpenAI
            ModelType.GPT_3_5_TURBO: CostConfig(
                input_cost_per_1k_tokens=0.0005,
                output_cost_per_1k_tokens=0.0015,
                max_tokens=4096,
                context_window=16385
            ),
            ModelType.GPT_4: CostConfig(
                input_cost_per_1k_tokens=0.03,
                output_cost_per_1k_tokens=0.06,
                max_tokens=4096,
                context_window=8192
            ),
            ModelType.GPT_4_TURBO: CostConfig(
                input_cost_per_1k_tokens=0.01,
                output_cost_per_1k_tokens=0.03,
                max_tokens=4096,
                context_window=128000
            ),
            ModelType.GPT_4O: CostConfig(
                input_cost_per_1k_tokens=0.005,
                output_cost_per_1k_tokens=0.015,
                max_tokens=4096,
                context_window=128000
            )
            

        }
    
    def setup_agent_configs(self):
        """Configuración de agentes especializados"""
        self.agent_configs = {
            "sales_assistant": AgentConfig(
                name="Asistente de Ventas",
                description="Agente especializado en ventas y recomendaciones de productos Apple",
                provider=self.current_provider,
                model=ModelType.GEMINI_1_5_FLASH if self.current_provider == AIProvider.GEMINI else ModelType.GPT_3_5_TURBO,
                temperature=0.7,
                max_tokens=800,
                system_prompt="""Eres un experto asistente de ventas de Apple Store. Tu objetivo es:
                1. Entender las necesidades del cliente
                2. Recomendar productos Apple apropiados
                3. Proporcionar información clara sobre especificaciones
                4. Ayudar en decisiones de compra
                5. Ser amigable, profesional y persuasivo
                
                Siempre considera el presupuesto y casos de uso del cliente.
                Usa búsqueda semántica para encontrar productos relevantes.
                Mantén un tono conversacional y servicial.""",
                cost_config=self.cost_configs[ModelType.GEMINI_1_5_FLASH if self.current_provider == AIProvider.GEMINI else ModelType.GPT_3_5_TURBO]
            ),
            
            "technical_support": AgentConfig(
                name="Soporte Técnico",
                description="Agente especializado en soporte técnico y resolución de problemas",
                provider=self.current_provider,
                model=ModelType.GEMINI_PRO if self.current_provider == AIProvider.GEMINI else ModelType.GPT_4,
                temperature=0.3,
                max_tokens=1200,
                system_prompt="""Eres un especialista en soporte técnico de Apple. Tu función es:
                1. Diagnosticar problemas técnicos
                2. Proporcionar soluciones paso a paso
                3. Explicar procedimientos técnicos claramente
                4. Recomendar configuraciones óptimas
                5. Ser paciente y educativo
                
                Usa lenguaje técnico apropiado pero accesible.
                Siempre proporciona instrucciones claras y verificables.""",
                cost_config=self.cost_configs[ModelType.GEMINI_PRO if self.current_provider == AIProvider.GEMINI else ModelType.GPT_4]
            ),
            
            "product_expert": AgentConfig(
                name="Experto en Productos",
                description="Agente especializado en conocimiento profundo de productos Apple",
                provider=self.current_provider,
                model=ModelType.GEMINI_1_5_PRO if self.current_provider == AIProvider.GEMINI else ModelType.GPT_4_TURBO,
                temperature=0.4,
                max_tokens=1000,
                system_prompt="""Eres un experto en toda la línea de productos Apple. Tu especialidad es:
                1. Conocimiento técnico detallado de especificaciones
                2. Comparaciones precisas entre modelos
                3. Historial y evolución de productos
                4. Características únicas y ventajas competitivas
                5. Compatibilidad entre productos del ecosistema Apple
                
                Proporciona información precisa, actualizada y técnicamente correcta.
                Usa datos específicos cuando sea posible.""",
                cost_config=self.cost_configs[ModelType.GEMINI_1_5_PRO if self.current_provider == AIProvider.GEMINI else ModelType.GPT_4_TURBO]
            ),
            
            "general_assistant": AgentConfig(
                name="Asistente General",
                description="Agente de propósito general para consultas diversas",
                provider=self.current_provider,
                model=ModelType.GEMINI_1_5_FLASH if self.current_provider == AIProvider.GEMINI else ModelType.GPT_3_5_TURBO,
                temperature=0.8,
                max_tokens=600,
                system_prompt="""Eres un asistente general de Apple Store. Tu función es:
                1. Responder preguntas generales sobre Apple
                2. Proporcionar información sobre servicios
                3. Direccionar a especialistas cuando sea necesario
                4. Mantener conversaciones amigables
                5. Manejar consultas variadas
                
                Sé útil, amigable y eficiente.
                Reconoce cuándo derivar a un especialista.""",
                cost_config=self.cost_configs[ModelType.GEMINI_1_5_FLASH if self.current_provider == AIProvider.GEMINI else ModelType.GPT_3_5_TURBO]
            )
        }
    
    def get_agent_config(self, agent_type: str) -> Optional[AgentConfig]:
        """Obtiene configuración de un agente específico"""
        return self.agent_configs.get(agent_type)
    
    def get_cost_config(self, model: ModelType) -> Optional[CostConfig]:
        """Obtiene configuración de costos para un modelo"""
        return self.cost_configs.get(model)
    
    def switch_provider(self, new_provider: AIProvider):
        """Cambia el proveedor de IA y actualiza configuraciones"""
        self.current_provider = new_provider
        
        # Actualizar modelos en configuraciones de agentes
        model_mapping = {
            AIProvider.GEMINI: {
                "sales_assistant": ModelType.GEMINI_1_5_FLASH,
                "technical_support": ModelType.GEMINI_PRO,
                "product_expert": ModelType.GEMINI_1_5_PRO,
                "general_assistant": ModelType.GEMINI_1_5_FLASH
            },
            AIProvider.OPENAI: {
                "sales_assistant": ModelType.GPT_3_5_TURBO,
                "technical_support": ModelType.GPT_4,
                "product_expert": ModelType.GPT_4_TURBO,
                "general_assistant": ModelType.GPT_3_5_TURBO
            }
        }
        
        if new_provider in model_mapping:
            for agent_type, model in model_mapping[new_provider].items():
                if agent_type in self.agent_configs:
                    self.agent_configs[agent_type].provider = new_provider
                    self.agent_configs[agent_type].model = model
                    self.agent_configs[agent_type].cost_config = self.cost_configs[model]
        
        logger.info(f"Proveedor de IA cambiado a: {new_provider.value}")
    
    def get_available_models(self, provider: AIProvider) -> list[ModelType]:
        """Obtiene modelos disponibles para un proveedor"""
        if provider == AIProvider.GEMINI:
            return [ModelType.GEMINI_PRO, ModelType.GEMINI_PRO_VISION, 
                   ModelType.GEMINI_1_5_PRO, ModelType.GEMINI_1_5_FLASH]
        elif provider == AIProvider.OPENAI:
            return [ModelType.GPT_3_5_TURBO, ModelType.GPT_4, 
                   ModelType.GPT_4_TURBO, ModelType.GPT_4O]
        elif provider == AIProvider.ANTHROPIC:
            return [ModelType.CLAUDE_3_HAIKU, ModelType.CLAUDE_3_SONNET, 
                   ModelType.CLAUDE_3_OPUS]
        return []

# Instancia global de configuración
ai_config = AIConfiguration()
