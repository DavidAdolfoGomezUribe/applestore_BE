# Sistema de Agentes de IA - Documentación

## Descripción General

El sistema de agentes de IA está diseñado con una arquitectura de grafos usando Langroid, proporcionando capacidades avanzadas de asistencia conversacional para el AppleStore Backend.

## Arquitectura del Sistema

### Componentes Principales

1. **Orchestrator** (`services/ai/orchestrator.py`)
   - Punto de entrada principal del sistema
   - Maneja el flujo completo de procesamiento de mensajes
   - Integra detección de intención, enrutamiento y tracking de costos

2. **Routing System** (`services/ai/routing.py`)
   - Detecta la intención del usuario usando patrones y triggers
   - Enruta mensajes al agente especializado apropiado
   - Maneja fallbacks inteligentes

3. **Agent Nodes** (`services/ai/nodes.py`)
   - Agentes especializados construidos con Langroid
   - Cada agente tiene capacidades específicas y contexto optimizado
   - Soporte para múltiples proveedores de IA (Gemini, OpenAI, Anthropic)

4. **Cost Tracker** (`services/ai/cost_tracker.py`)
   - Monitoreo en tiempo real de costos y tokens
   - Límites configurables diarios y mensuales
   - Métricas detalladas por agente y modelo

5. **Configuration** (`services/ai/config.py`)
   - Configuración centralizada de todos los componentes
   - Gestión de múltiples proveedores de IA
   - Configuración de costos y límites

## Tipos de Agentes

### 1. Sales Assistant (Asistente de Ventas)
- **Propósito**: Recomendaciones de productos y asistencia en ventas
- **Capacidades**:
  - Análisis de necesidades del cliente
  - Recomendaciones personalizadas de productos Apple
  - Información sobre especificaciones y compatibilidad
  - Asistencia en decisiones de compra

### 2. Product Expert (Experto en Productos)
- **Propósito**: Información técnica detallada sobre productos
- **Capacidades**:
  - Especificaciones técnicas completas
  - Comparativas entre productos
  - Análisis de compatibilidad
  - Recomendaciones basadas en uso específico

### 3. Technical Support (Soporte Técnico)
- **Propósito**: Resolución de problemas técnicos
- **Capacidades**:
  - Diagnóstico de problemas
  - Guías de solución paso a paso
  - Recomendaciones de mantenimiento
  - Escalación a soporte humano cuando sea necesario

### 4. General Assistant (Asistente General)
- **Propósito**: Asistencia general y fallback
- **Capacidades**:
  - Respuestas generales sobre Apple Store
  - Información sobre políticas y servicios
  - Redirección a agentes especializados
  - Manejo de consultas no clasificadas

## API Endpoints

### POST `/ai-agent/process`
Procesa un mensaje a través del sistema de grafos de agentes.

**Request Body:**
```json
{
  "message": "Necesito un iPhone para fotografía profesional",
  "chat_id": 123,
  "user_id": 456,
  "agent_role": "sales_assistant",
  "context": {
    "budget": 1500,
    "previous_purchases": ["MacBook Pro"]
  }
}
```

**Response:**
```json
{
  "response": "Te recomiendo el iPhone 15 Pro con sistema de cámaras avanzado...",
  "agent_role": "sales_assistant",
  "recommendations": [
    {
      "product_id": 1,
      "name": "iPhone 15 Pro",
      "category": "iPhone",
      "price": 1199.99,
      "confidence_score": 0.95,
      "reason": "Excelente para fotografía profesional con cámaras de 48MP"
    }
  ],
  "confidence": 0.92,
  "metadata": {
    "tokens_used": 150,
    "cost": 0.0023,
    "processing_time": 1.2
  }
}
```

### GET `/ai-agent/metrics`
Obtiene métricas de uso y costos del sistema.

**Response:**
```json
{
  "daily_metrics": {
    "date": "2025-09-15",
    "total_cost": 5.67,
    "total_requests": 234,
    "total_tokens": 45600,
    "breakdown_by_agent": {
      "sales_assistant": 3.45,
      "product_expert": 1.23,
      "technical_support": 0.89,
      "general_assistant": 0.10
    },
    "success_rate": 0.98
  }
}
```

## Configuración

### Variables de Entorno Requeridas

```bash
# Proveedor de IA por defecto
DEFAULT_AI_PROVIDER=gemini

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Redis para tracking
REDIS_URL=redis://redis:6379

# Límites de costos
COST_TRACKING_ENABLED=true
DAILY_COST_LIMIT=50.0
MONTHLY_COST_LIMIT=1000.0
```

### Obtener API Keys

1. **Gemini API**: https://makersuite.google.com/app/apikey
2. **OpenAI API**: https://platform.openai.com/account/api-keys
3. **Anthropic API**: https://console.anthropic.com/

## Integración con Sistema de Chats

El sistema se integra perfectamente con el sistema de chats existente:

```python
# Ejemplo de integración
from services.ai.orchestrator import graph_orchestrator

async def process_chat_message(chat_id: int, message: str, user_id: int):
    request = AgentRequest(
        message=message,
        chat_id=chat_id,
        user_id=user_id,
        agent_role=AgentRole.SALES_ASSISTANT
    )
    
    response = await graph_orchestrator.process_message(request)
    
    # Guardar respuesta en la base de datos
    await save_message_to_chat(chat_id, response.response, "assistant")
    
    return response
```

## Monitoreo de Costos

### Métricas Disponibles

- **Costos por día/mes/año**
- **Tokens utilizados por modelo**
- **Breakdown por agente**
- **Tasa de éxito de respuestas**
- **Tiempo promedio de procesamiento**
- **Requests más costosos**

### Alertas Automáticas

- Límite diario alcanzado (90%)
- Límite mensual alcanzado (90%)
- Costos anómalos detectados
- Errores de proveedores de IA

## Escalabilidad

### Horizontal
- Múltiples instancias de agentes
- Balanceador de carga Redis
- Cache de respuestas frecuentes

### Vertical
- Optimización de prompts
- Batch processing
- Modelo selection automático

## Seguridad

- **API Keys**: Almacenadas como variables de entorno
- **Rate Limiting**: Por usuario y por día
- **Sanitización**: Entrada y salida de datos
- **Logging**: Completo sin datos sensibles

## Troubleshooting

### Problemas Comunes

1. **Error de API Key**: Verificar configuración en `.env`
2. **Redis no conecta**: Verificar que el servicio Redis esté ejecutándose
3. **Respuestas lentas**: Revisar límites de rate limiting del proveedor
4. **Costos altos**: Revisar configuración de límites y uso de modelos

### Logs

Los logs están disponibles en:
- Container logs: `docker logs backend-1`
- Application logs: Nivel INFO para operaciones normales, ERROR para problemas

## Futuras Mejoras

1. **Memoria de Conversación**: Persistencia de contexto a largo plazo
2. **Aprendizaje Adaptativo**: Mejora automática basada en feedback
3. **Multimodal**: Soporte para imágenes y voz
4. **Análisis de Sentimientos**: Detección de satisfacción del cliente
5. **A/B Testing**: Experimentación con diferentes prompts y modelos
