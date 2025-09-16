from fastapi import APIRouter, HTTPException, Query, status, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime

from schemas.ai.agentSchemas import (
    AgentRequest, 
    AgentResponse, 
    AgentConfiguration,
    GraphMessage,
    AgentDirectMessage,
    ProviderSwitchRequest
)
from services.ai.orchestrator import graph_orchestrator
from services.ai.routing import BotType
from services.ai.config import ai_config, AIProvider, ModelType
from services.ai.cost_tracker import cost_tracker, CostSummary
from services.ai.nodes import AgentNodeFactory
from services.chats.chatService import get_chat_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai-agent",
    tags=["🤖 AI Agent System"],
    responses={404: {"description": "No encontrado"}},
)

# ========== ENDPOINTS PRINCIPALES DEL SISTEMA DE GRAFOS ==========

@router.post(
    "/process",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="� Procesar mensaje por sistema de grafos",
    description="""
    **Endpoint principal del sistema de agentes IA con arquitectura de grafos.**
    
    Este endpoint:
    1. **Detecta la intención** del mensaje automáticamente
    2. **Decide el flujo apropiado**: respuesta directa, agente específico, o escalamiento
    3. **Procesa con el agente adecuado** si es necesario
    4. **Rastrea costos** en tiempo real
    5. **Guarda la conversación** en la base de datos
    
    **Tipos de bot soportados:**
    - `whatsapp_bot`: Para integración con WhatsApp
    - `web_chat_bot`: Para chat de la página web
    - `telegram_bot`: Para integración con Telegram
    
    **Detección inteligente de intenciones:**
    - Saludos y despedidas
    - Consultas de productos
    - Preguntas de precios
    - Soporte técnico
    - Comparaciones
    - Intención de compra
    - Quejas (escalamiento automático)
    """
)
async def process_message(message_data: GraphMessage):
    """
    Procesa mensaje a través del sistema completo de grafos
    """
    try:
        # Verificar que el chat existe si se especifica
        if message_data.chat_id:
            chat = get_chat_service(message_data.chat_id)
            if not chat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Chat con ID {message_data.chat_id} no encontrado"
                )
        
        # Procesar con el orquestador
        result = await graph_orchestrator.process_message(
            message=message_data.message,
            bot_type=message_data.bot_type,
            chat_id=message_data.chat_id,
            user_id=message_data.user_id,
            save_to_chat=message_data.save_to_chat,
            context=message_data.context
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando mensaje: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando mensaje: {str(e)}"
        )

@router.post(
    "/agent/direct",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="🎯 Mensaje directo a agente específico",
    description="""
    Envía mensaje directamente a un agente específico, saltando la detección de intenciones.
    
    **Agentes disponibles:**
    - `sales_assistant`: Asistente de ventas
    - `technical_support`: Soporte técnico
    - `product_expert`: Experto en productos
    - `general_assistant`: Asistente general
    
    Útil para:
    - Testing de agentes específicos
    - Cuando ya conoces el tipo de consulta
    - Integración con sistemas que manejan routing propio
    """
)
async def direct_agent_message(message_data: AgentDirectMessage):
    """
    Envía mensaje directamente a un agente específico
    """
    try:
        # Verificar que el tipo de agente existe
        if message_data.agent_type not in AgentNodeFactory.get_available_agent_types():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de agente no válido: {message_data.agent_type}"
            )
        
        # Procesar con agente específico
        result = await graph_orchestrator._process_with_agent(
            message=message_data.message,
            agent_type=message_data.agent_type,
            chat_id=message_data.chat_id,
            user_id=message_data.user_id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en mensaje directo a agente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando con agente: {str(e)}"
        )

# ========== ENDPOINTS DE CONFIGURACIÓN Y GESTIÓN ==========

@router.get(
    "/config",
    response_model=Dict[str, Any],
    summary="⚙️ Configuración actual del sistema",
    description="Obtiene la configuración completa del sistema de agentes IA."
)
async def get_system_config():
    """Obtiene configuración actual del sistema"""
    try:
        return {
            "current_provider": ai_config.current_provider.value,
            "available_providers": [p.value for p in AIProvider],
            "agent_configs": {
                agent_type: config.dict() 
                for agent_type, config in ai_config.agent_configs.items()
            },
            "cost_tracking_enabled": ai_config.cost_tracking_enabled,
            "daily_cost_limit": ai_config.daily_cost_limit,
            "monthly_cost_limit": ai_config.monthly_cost_limit,
            "available_models": {
                provider.value: [model.value for model in ai_config.get_available_models(provider)]
                for provider in AIProvider
            }
        }
    except Exception as e:
        logger.error(f"Error obteniendo configuración: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo configuración: {str(e)}"
        )

@router.post(
    "/config/provider",
    summary="� Cambiar proveedor de IA",
    description="""
    Cambia el proveedor de IA del sistema (Gemini ↔ OpenAI).
    
    ⚠️ **Importante:** Este cambio afecta a todos los agentes y puede requerir
    reinicialización de nodos cargados en memoria.
    """
)
async def switch_ai_provider(switch_request: ProviderSwitchRequest):
    """Cambia el proveedor de IA del sistema"""
    try:
        old_provider = ai_config.current_provider
        ai_config.switch_provider(switch_request.provider)
        
        # Limpiar cache de nodos para forzar recreación con nuevo proveedor
        graph_orchestrator.agent_nodes.clear()
        
        return {
            "message": f"Proveedor cambiado de {old_provider.value} a {switch_request.provider.value}",
            "old_provider": old_provider.value,
            "new_provider": switch_request.provider.value,
            "agents_reloaded": True
        }
        
    except Exception as e:
        logger.error(f"Error cambiando proveedor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cambiando proveedor: {str(e)}"
        )

# ========== ENDPOINTS DE MÉTRICAS Y COSTOS ==========

@router.get(
    "/metrics",
    response_model=Dict[str, Any],
    summary="📊 Métricas del sistema",
    description="Obtiene métricas completas del sistema de agentes IA."
)
async def get_system_metrics():
    """Obtiene métricas completas del sistema"""
    try:
        metrics = await graph_orchestrator.get_system_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo métricas: {str(e)}"
        )

@router.get(
    "/costs/summary",
    response_model=CostSummary,
    summary="💰 Resumen de costos",
    description="Obtiene resumen de costos diarios o mensuales."
)
async def get_cost_summary(
    period: str = Query("daily", description="Período: 'daily' o 'monthly'")
):
    """Obtiene resumen de costos"""
    try:
        if period not in ["daily", "monthly"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Período debe ser 'daily' o 'monthly'"
            )
        
        summary = await cost_tracker.get_cost_summary(period)
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo resumen de costos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo resumen de costos: {str(e)}"
        )

@router.get(
    "/costs/limits",
    response_model=Dict[str, Any],
    summary="⚠️ Estado de límites de costo",
    description="Verifica si se han excedido los límites de costo diarios/mensuales."
)
async def check_cost_limits():
    """Verifica límites de costo"""
    try:
        limits = await cost_tracker.check_cost_limits()
        return limits
    except Exception as e:
        logger.error(f"Error verificando límites: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verificando límites: {str(e)}"
        )

# ========== ENDPOINTS DE CONVERSACIONES ==========

@router.get(
    "/conversation/{chat_id}/summary",
    response_model=Dict[str, Any],
    summary="💬 Resumen de conversación",
    description="Obtiene resumen y análisis de una conversación específica."
)
async def get_conversation_summary(chat_id: int):
    """Obtiene resumen de una conversación"""
    try:
        summary = await graph_orchestrator.get_conversation_summary(chat_id)
        return summary
    except Exception as e:
        logger.error(f"Error obteniendo resumen de conversación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo resumen: {str(e)}"
        )

# ========== ENDPOINTS DE UTILIDAD ==========

@router.get(
    "/agents/types",
    response_model=List[str],
    summary="🤖 Tipos de agentes disponibles",
    description="Lista todos los tipos de agentes disponibles en el sistema."
)
async def get_agent_types():
    """Obtiene tipos de agentes disponibles"""
    return AgentNodeFactory.get_available_agent_types()

@router.get(
    "/bot-types",
    response_model=List[str],
    summary="🤖 Tipos de bots soportados",
    description="Lista tipos de bots soportados para integración."
)
async def get_bot_types():
    """Obtiene tipos de bots soportados"""
    return [bot_type.value for bot_type in BotType]

@router.get(
    "/health",
    summary="🏥 Estado de salud del sistema",
    description="Verifica el estado de salud de todos los componentes del sistema de IA."
)
async def system_health_check():
    """Verifica estado de salud del sistema"""
    try:
        health_status = {
            "status": "healthy",
            "components": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Verificar Qdrant
        try:
            from services.ai.nodes import BaseAgentNode
            test_node = BaseAgentNode(ai_config.get_agent_config("general_assistant"))
            test_results = await test_node.search_products("test", limit=1)
            health_status["components"]["qdrant"] = "✅ Conectado"
        except Exception as e:
            health_status["components"]["qdrant"] = f"❌ Error: {str(e)}"
            health_status["status"] = "degraded"
        
        # Verificar Redis (costos)
        try:
            daily_cost = await cost_tracker.get_daily_cost()
            health_status["components"]["redis"] = "✅ Conectado"
            health_status["daily_cost"] = daily_cost
        except Exception as e:
            health_status["components"]["redis"] = f"⚠️ Error: {str(e)}"
        
        # Verificar configuración de agentes
        try:
            agent_count = len(ai_config.agent_configs)
            health_status["components"]["agents"] = f"✅ {agent_count} agentes configurados"
            health_status["loaded_agents"] = len(graph_orchestrator.agent_nodes)
        except Exception as e:
            health_status["components"]["agents"] = f"❌ Error: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Verificar API keys
        if ai_config.current_provider == AIProvider.GEMINI:
            health_status["components"]["ai_provider"] = "✅ Gemini configurado" if ai_config.gemini_api_key else "❌ API key faltante"
        elif ai_config.current_provider == AIProvider.OPENAI:
            health_status["components"]["ai_provider"] = "✅ OpenAI configurado" if ai_config.openai_api_key else "❌ API key faltante"
        
        health_status["current_provider"] = ai_config.current_provider.value
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Inicialización del sistema al importar el módulo
@router.on_event("startup")
async def startup_event():
    """Inicializa el sistema al arrancar"""
    try:
        await graph_orchestrator.initialize()
        logger.info("Sistema de agentes IA inicializado correctamente")
    except Exception as e:
        logger.error(f"Error inicializando sistema de agentes: {str(e)}")
        # No fallar el startup, pero log el error
