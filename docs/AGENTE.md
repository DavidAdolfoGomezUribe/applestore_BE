# Sistema de Agentes de IA - Guía Completa

## Índice
1. [Visión General](#visión-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Componentes Principales](#componentes-principales)
4. [Implementación Paso a Paso](#implementación-paso-a-paso)
5. [Configuración](#configuración)
6. [API Endpoints - Rutas Detalladas](#api-endpoints---rutas-detalladas)
7. [Uso del Sistema](#uso-del-sistema)
8. [Integración](#integración)
9. [Monitoreo y Costos](#monitoreo-y-costos)
10. [Ejemplos Prácticos](#ejemplos-prácticos)

## Visión General

### ¿Qué es este Sistema?
Este es un sistema avanzado de agentes de IA implementado para el backend de AppleStore que utiliza una arquitectura de grafos para proporcionar asistencia inteligente y conversacional. El sistema fue diseñado para manejar diferentes tipos de consultas de usuarios a través de agentes especializados.

### Características Principales
- **Arquitectura de Grafos**: Utiliza Langroid para crear nodos de agentes interconectados
- **Múltiples Proveedores de IA**: Soporte para Gemini, OpenAI y Anthropic con fallback automático
- **Agentes Especializados**: Diferentes agentes para ventas, soporte técnico, productos y asistencia general
- **Tracking de Costos**: Monitoreo en tiempo real de costos y tokens utilizados
- **Búsqueda Semántica**: Integración con Qdrant para recomendaciones de productos
- **Sistema de Routing**: Detección inteligente de intención para enrutar al agente correcto

## Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chat/WebBot   │───▶│   Orchestrator  │───▶│  Intent Router  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Cost Tracker   │    │  Agent Nodes    │
                       └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │     Redis       │    │   Qdrant DB     │
                       └─────────────────┘    └─────────────────┘
```

### Flujo de Datos
1. **Entrada**: Usuario envía mensaje a través de chat o API
2. **Orchestrator**: Recibe el mensaje y coordina todo el proceso
3. **Intent Router**: Analiza el mensaje y determina el agente apropiado
4. **Agent Node**: Procesa el mensaje usando IA especializada
5. **Search Integration**: Si es necesario, busca productos en Qdrant
6. **Cost Tracking**: Registra costos y métricas en Redis
7. **Response**: Devuelve respuesta enriquecida al usuario

## Componentes Principales

### 1. Orchestrator (`services/ai/orchestrator.py`)
**Propósito**: Coordinador central que maneja todo el flujo de procesamiento

**Funciones Principales**:
- Recibe requests de agentes
- Coordina entre routing, processing y tracking
- Maneja errores y fallbacks
- Integra búsqueda de productos

**Métodos Clave**:
```python
async def process_message(request: AgentRequest) -> AgentResponse
async def get_conversation_history(chat_id: int) -> List[ConversationMessage]
async def _search_products(query: str) -> List[ProductRecommendation]
```

### 2. Intent Router (`services/ai/routing.py`)
**Propósito**: Analiza mensajes y determina qué agente debe responder

**Lógica de Routing**:
- **Sales Assistant**: Palabras como "comprar", "precio", "recomendar"
- **Product Expert**: "especificaciones", "comparar", "diferencias"
- **Technical Support**: "problema", "error", "ayuda", "soporte"
- **General Assistant**: Todo lo demás (fallback)

**Configuración de Triggers**:
```python
ROUTING_PATTERNS = {
    AgentRole.SALES_ASSISTANT: [
        "comprar", "precio", "cost", "recomendar", "sugerir",
        "mejor opción", "presupuesto", "oferta"
    ],
    AgentRole.PRODUCT_EXPERT: [
        "especificaciones", "specs", "comparar", "diferencia",
        "características", "memoria", "almacenamiento"
    ],
    # ... más patrones
}
```

### 3. Agent Nodes (`services/ai/nodes.py`)
**Propósito**: Agentes especializados construidos con Langroid

#### Sales Assistant Agent
- **Especialidad**: Ventas y recomendaciones
- **Prompt**: Enfocado en entender necesidades y recomendar productos
- **Capacidades**: Análisis de presupuesto, recomendaciones personalizadas

#### Product Expert Agent  
- **Especialidad**: Información técnica detallada
- **Prompt**: Experto en especificaciones y comparativas
- **Capacidades**: Comparaciones técnicas, compatibilidad

#### Technical Support Agent
- **Especialidad**: Resolución de problemas
- **Prompt**: Diagnóstico y soluciones paso a paso
- **Capacidades**: Troubleshooting, guías de solución

#### General Assistant Agent
- **Especialidad**: Asistencia general y fallback
- **Prompt**: Información general sobre Apple Store
- **Capacidades**: Políticas, servicios, redirección

### 4. Cost Tracker (`services/ai/cost_tracker.py`)
**Propósito**: Monitoreo completo de costos y métricas

**Métricas Tracked**:
- Tokens de entrada y salida
- Costos por request
- Breakdown por agente y modelo
- Límites diarios/mensuales
- Tiempo de procesamiento

**Storage en Redis**:
```
cost:daily:2025-09-15 -> {"total_cost": 5.67, "requests": 234}
cost:monthly:2025-09 -> {"total_cost": 156.78, "requests": 5678}
metrics:agent:sales_assistant -> {"cost": 3.45, "requests": 123}
```

### 5. Configuration (`services/ai/config.py`)
**Propósito**: Configuración centralizada de todo el sistema

**Configuraciones Incluidas**:
- Proveedores de IA y sus costos
- Configuración de agentes
- Límites de costos
- Configuración de modelos

## Implementación Paso a Paso

### Paso 1: Instalación de Dependencias
Se agregaron las siguientes dependencias al `requirements.txt`:
```
langroid          # Framework de agentes
google-generativeai  # Gemini API
openai           # OpenAI API
tiktoken         # Conteo de tokens
redis>=4.5.0     # Para tracking (sin aioredis por conflictos)
```

### Paso 2: Estructura de Archivos Creada
```
app/
├── services/ai/
│   ├── __init__.py
│   ├── config.py          # Configuración central
│   ├── orchestrator.py    # Coordinador principal
│   ├── routing.py         # Sistema de routing
│   ├── nodes.py           # Agentes especializados
│   └── cost_tracker.py    # Tracking de costos
├── schemas/ai/
│   ├── __init__.py
│   └── agentSchemas.py    # Modelos Pydantic
└── routes/ai/
    ├── __init__.py
    └── agentRoutes.py     # Endpoints FastAPI
```

### Paso 3: Configuración de Docker
Se agregó Redis al `docker-compose.yml`:
```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
  command: redis-server --appendonly yes
```

### Paso 4: Variables de Entorno
Se configuraron en `.env`:
```
DEFAULT_AI_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
REDIS_URL=redis://redis:6379
COST_TRACKING_ENABLED=true
DAILY_COST_LIMIT=50.0
MONTHLY_COST_LIMIT=1000.0
```

## Configuración

### Variables de Entorno Requeridas

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DEFAULT_AI_PROVIDER` | Proveedor principal (gemini/openai/anthropic) | `gemini` |
| `GEMINI_API_KEY` | Clave API de Google Gemini | Requerido |
| `OPENAI_API_KEY` | Clave API de OpenAI | Opcional |
| `ANTHROPIC_API_KEY` | Clave API de Anthropic | Opcional |
| `REDIS_URL` | URL de conexión a Redis | `redis://redis:6379` |
| `COST_TRACKING_ENABLED` | Habilitar tracking de costos | `true` |
| `DAILY_COST_LIMIT` | Límite diario en USD | `50.0` |
| `MONTHLY_COST_LIMIT` | Límite mensual en USD | `1000.0` |

### Obtener API Keys

1. **Gemini API**: 
   - Ir a https://makersuite.google.com/app/apikey
   - Crear nueva API key
   - Copiar y pegar en `GEMINI_API_KEY`

2. **OpenAI API**:
   - Ir a https://platform.openai.com/account/api-keys
   - Crear nueva secret key
   - Copiar y pegar en `OPENAI_API_KEY`

3. **Anthropic API**:
   - Ir a https://console.anthropic.com/
   - Generar API key
   - Copiar y pegar en `ANTHROPIC_API_KEY`

## API Endpoints - Rutas Detalladas

### 1. POST `/ai-agent/process` - Procesamiento Principal

**Descripción**: Endpoint principal para procesar mensajes a través del sistema de grafos

**Request**:
```json
{
  "message": "Necesito un iPhone para fotografía profesional",
  "chat_id": 123,
  "user_id": 456,
  "agent_role": "sales_assistant",
  "context": {
    "budget": 1500,
    "previous_purchases": ["MacBook Pro"],
    "preferences": ["camera_quality", "battery_life"]
  },
  "conversation_history": [
    {
      "role": "user",
      "content": "Hola, busco un teléfono",
      "timestamp": "2025-09-15T10:00:00Z"
    }
  ]
}
```

**Response**:
```json
{
  "response": "Para fotografía profesional, te recomiendo el iPhone 15 Pro. Cuenta con un sistema de cámaras avanzado de 48MP con teleobjetivo 3x, modo Acción mejorado y grabación de video ProRes. Con tu presupuesto de $1500, es la opción perfecta.",
  "agent_role": "sales_assistant",
  "recommendations": [
    {
      "product_id": 1,
      "name": "iPhone 15 Pro",
      "category": "iPhone",
      "price": 1199.99,
      "confidence_score": 0.95,
      "reason": "Excelente para fotografía profesional con cámaras de 48MP y funciones pro",
      "specifications": {
        "camera": "48MP Main + 12MP Ultra Wide + 12MP Telephoto",
        "video": "4K ProRes, Dolby Vision",
        "storage": "128GB, 256GB, 512GB, 1TB"
      }
    },
    {
      "product_id": 2,
      "name": "iPhone 15 Pro Max",
      "category": "iPhone",
      "price": 1399.99,
      "confidence_score": 0.88,
      "reason": "Versión premium con teleobjetivo 5x para mayor alcance fotográfico"
    }
  ],
  "confidence": 0.92,
  "sources": ["product_database", "qdrant_search"],
  "follow_up_suggestions": [
    "¿Te interesa conocer más sobre las funciones de cámara?",
    "¿Quieres comparar con otros modelos?",
    "¿Necesitas accesorios para fotografía?"
  ],
  "metadata": {
    "agent_used": "sales_assistant",
    "intent_detected": "product_recommendation",
    "search_query": "iPhone fotografía profesional",
    "products_searched": 24,
    "tokens_used": 245,
    "cost": 0.0037,
    "processing_time": 1.8,
    "provider_used": "gemini",
    "model_used": "gemini-1.5-flash"
  },
  "timestamp": "2025-09-15T10:05:30Z"
}
```

**Códigos de Estado**:
- `200`: Procesamiento exitoso
- `400`: Request inválido
- `429`: Límite de costos excedido
- `500`: Error interno del servidor

**Curl Example**:
```bash
curl -X POST "http://localhost:8000/ai-agent/process" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Necesito un iPhone para fotografía profesional",
    "chat_id": 123,
    "user_id": 456
  }'
```

### 2. GET `/ai-agent/metrics` - Métricas del Sistema

**Descripción**: Obtiene métricas detalladas de uso y costos

**Query Parameters**:
- `period`: `daily`, `monthly`, `yearly` (default: `daily`)
- `agent`: Filtrar por agente específico (opcional)
- `date`: Fecha específica YYYY-MM-DD (opcional)

**Response**:
```json
{
  "daily_metrics": {
    "date": "2025-09-15",
    "period": "daily",
    "total_cost": 12.45,
    "total_requests": 567,
    "total_tokens": 89123,
    "breakdown_by_agent": {
      "sales_assistant": {
        "cost": 7.89,
        "requests": 234,
        "tokens": 45600,
        "avg_cost_per_request": 0.0337
      },
      "product_expert": {
        "cost": 2.34,
        "requests": 123,
        "tokens": 23400,
        "avg_cost_per_request": 0.0190
      },
      "technical_support": {
        "cost": 1.56,
        "requests": 89,
        "tokens": 15600,
        "avg_cost_per_request": 0.0175
      },
      "general_assistant": {
        "cost": 0.66,
        "requests": 121,
        "tokens": 4523,
        "avg_cost_per_request": 0.0055
      }
    },
    "breakdown_by_model": {
      "gemini-1.5-flash": {
        "cost": 8.90,
        "requests": 456,
        "tokens": 67890
      },
      "gpt-3.5-turbo": {
        "cost": 3.55,
        "requests": 111,
        "tokens": 21233
      }
    },
    "breakdown_by_provider": {
      "gemini": {
        "cost": 8.90,
        "requests": 456,
        "success_rate": 0.98
      },
      "openai": {
        "cost": 3.55,
        "requests": 111,
        "success_rate": 0.96
      }
    },
    "most_expensive_request": 0.156,
    "average_cost_per_request": 0.0220,
    "average_tokens_per_request": 157,
    "success_rate": 0.97,
    "avg_processing_time": 1.4,
    "peak_hour": "14:00",
    "cost_trend": "increasing"
  },
  "limits": {
    "daily_limit": 50.0,
    "monthly_limit": 1000.0,
    "daily_usage_percentage": 24.9,
    "monthly_usage_percentage": 15.6,
    "estimated_monthly_cost": 373.5,
    "days_until_limit": 3.0
  },
  "alerts": [
    {
      "type": "warning",
      "message": "Daily usage at 25% of limit",
      "threshold": 25
    }
  ]
}
```

**Curl Example**:
```bash
curl -X GET "http://localhost:8000/ai-agent/metrics?period=daily&date=2025-09-15"
```

### 3. POST `/ai-agent/chat-integration` - Integración con Chats

**Descripción**: Endpoint especializado para integración con el sistema de chats existente

**Request**:
```json
{
  "chat_id": 123,
  "message": "¿Cuál es la diferencia entre iPhone 15 y iPhone 15 Pro?",
  "agent_config": {
    "role": "product_expert",
    "max_recommendations": 2,
    "use_conversation_history": true,
    "temperature": 0.7,
    "max_tokens": 800
  }
}
```

**Response**:
```json
{
  "chat_id": 123,
  "message_id": 456,
  "agent_response": {
    "response": "Las principales diferencias entre iPhone 15 y iPhone 15 Pro son:\n\n**iPhone 15:**\n- Cámara principal de 48MP\n- Chip A16 Bionic\n- Aluminio\n- Precio desde $899\n\n**iPhone 15 Pro:**\n- Sistema de 3 cámaras (48MP + 12MP + 12MP telefoto)\n- Chip A17 Pro\n- Titanio\n- Botón de Acción personalizable\n- Precio desde $1199\n\nLa diferencia de $300 se justifica por las cámaras profesionales y el rendimiento superior.",
    "agent_role": "product_expert",
    "recommendations": [
      {
        "product_id": 1,
        "name": "iPhone 15",
        "price": 899.99,
        "confidence_score": 0.85
      },
      {
        "product_id": 2,
        "name": "iPhone 15 Pro",
        "price": 1199.99,
        "confidence_score": 0.90
      }
    ],
    "confidence": 0.94
  },
  "created_at": "2025-09-15T10:05:30Z"
}
```

### 4. GET `/ai-agent/agents` - Lista de Agentes

**Descripción**: Obtiene información sobre todos los agentes disponibles

**Response**:
```json
{
  "agents": [
    {
      "role": "sales_assistant",
      "name": "Asistente de Ventas",
      "description": "Especializado en recomendaciones y ventas de productos Apple",
      "capabilities": [
        "Recomendaciones personalizadas",
        "Análisis de presupuesto",
        "Comparación de productos",
        "Asistencia en decisiones de compra"
      ],
      "triggers": ["comprar", "precio", "recomendar", "mejor opción"],
      "model": "gemini-1.5-flash",
      "temperature": 0.7,
      "max_tokens": 800,
      "status": "active"
    },
    {
      "role": "product_expert",
      "name": "Experto en Productos",
      "description": "Información técnica detallada sobre productos Apple",
      "capabilities": [
        "Especificaciones técnicas",
        "Comparativas detalladas",
        "Análisis de compatibilidad",
        "Recomendaciones por uso específico"
      ],
      "triggers": ["especificaciones", "comparar", "diferencias"],
      "model": "gemini-1.5-flash",
      "temperature": 0.5,
      "max_tokens": 1000,
      "status": "active"
    }
    // ... más agentes
  ]
}
```

### 5. POST `/ai-agent/feedback` - Feedback del Usuario

**Descripción**: Permite enviar feedback sobre las respuestas para mejorar el sistema

**Request**:
```json
{
  "message_id": "msg_123456",
  "chat_id": 123,
  "rating": 5,
  "feedback": "Excelente recomendación, muy detallada",
  "helpful": true,
  "tags": ["accurate", "detailed", "helpful"]
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Feedback registrado correctamente",
  "feedback_id": "fb_789012"
}
```

### 6. GET `/ai-agent/health` - Estado del Sistema

**Descripción**: Verifica el estado de todos los componentes del sistema

**Response**:
```json
{
  "status": "healthy",
  "components": {
    "redis": {
      "status": "connected",
      "response_time": 2.3
    },
    "qdrant": {
      "status": "connected", 
      "collections": ["products_kb"],
      "points": 24
    },
    "ai_providers": {
      "gemini": {
        "status": "available",
        "model": "gemini-1.5-flash",
        "last_check": "2025-09-15T10:00:00Z"
      },
      "openai": {
        "status": "available",
        "model": "gpt-3.5-turbo",
        "last_check": "2025-09-15T10:00:00Z"
      }
    }
  },
  "uptime": 86400,
  "version": "1.0.0"
}
```

## Uso del Sistema

### 1. Uso Básico - Mensaje Simple

```python
import requests

# Enviar mensaje simple
response = requests.post("http://localhost:8000/ai-agent/process", 
    json={
        "message": "Necesito un iPad para estudiar",
        "user_id": 123
    }
)

result = response.json()
print(result["response"])
print(result["recommendations"])
```

### 2. Uso Avanzado - Con Contexto

```python
# Mensaje con contexto completo
response = requests.post("http://localhost:8000/ai-agent/process",
    json={
        "message": "¿Qué MacBook me recomiendas?",
        "chat_id": 456,
        "user_id": 123,
        "agent_role": "sales_assistant",
        "context": {
            "budget": 2000,
            "use_case": "video_editing",
            "current_device": "MacBook Air 2019"
        },
        "conversation_history": [
            {
                "role": "user",
                "content": "Hola, necesito cambiar mi laptop",
                "timestamp": "2025-09-15T10:00:00Z"
            },
            {
                "role": "assistant", 
                "content": "¡Perfecto! ¿Para qué vas a usar tu nueva laptop?",
                "timestamp": "2025-09-15T10:01:00Z"
            }
        ]
    }
)
```

### 3. Integración con Sistema de Chats Existente

```python
# En tu controlador de chats
from services.ai.orchestrator import graph_orchestrator
from schemas.ai.agentSchemas import AgentRequest, AgentRole

async def handle_chat_message(chat_id: int, message: str, user_id: int):
    # Crear request para el agente
    agent_request = AgentRequest(
        message=message,
        chat_id=chat_id,
        user_id=user_id,
        agent_role=AgentRole.SALES_ASSISTANT
    )
    
    # Procesar con el orchestrator
    agent_response = await graph_orchestrator.process_message(agent_request)
    
    # Guardar en base de datos
    await save_message_to_chat(
        chat_id=chat_id,
        content=agent_response.response,
        sender="assistant",
        metadata={
            "agent_role": agent_response.agent_role,
            "recommendations": agent_response.recommendations,
            "cost": agent_response.metadata.get("cost", 0)
        }
    )
    
    return agent_response
```

## Integración

### Con WhatsApp Bot

```python
# Ejemplo de integración con bot de WhatsApp
async def handle_whatsapp_message(phone_number: str, message: str):
    # Mapear número a user_id
    user_id = get_user_by_phone(phone_number)
    
    # Procesar con agente
    response = await requests.post("http://backend:8000/ai-agent/process",
        json={
            "message": message,
            "user_id": user_id,
            "context": {
                "channel": "whatsapp",
                "phone": phone_number
            }
        }
    )
    
    # Enviar respuesta por WhatsApp
    await send_whatsapp_message(phone_number, response["response"])
    
    # Si hay recomendaciones, enviar como carrusel
    if response["recommendations"]:
        await send_product_carousel(phone_number, response["recommendations"])
```

### Con Frontend Web

```javascript
// Frontend JavaScript
async function sendMessage(message, chatId) {
    const response = await fetch('/ai-agent/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${userToken}`
        },
        body: JSON.stringify({
            message: message,
            chat_id: chatId,
            user_id: getCurrentUserId()
        })
    });
    
    const result = await response.json();
    
    // Mostrar respuesta
    displayMessage(result.response, 'assistant');
    
    // Mostrar recomendaciones si existen
    if (result.recommendations) {
        displayProductRecommendations(result.recommendations);
    }
    
    // Mostrar sugerencias de seguimiento
    if (result.follow_up_suggestions) {
        displayQuickReplies(result.follow_up_suggestions);
    }
}
```

## Monitoreo y Costos

### Dashboard de Métricas

```python
# Obtener métricas para dashboard
async def get_dashboard_metrics():
    metrics_response = requests.get("http://localhost:8000/ai-agent/metrics")
    metrics = metrics_response.json()
    
    return {
        "total_cost_today": metrics["daily_metrics"]["total_cost"],
        "requests_today": metrics["daily_metrics"]["total_requests"],
        "success_rate": metrics["daily_metrics"]["success_rate"],
        "top_agent": max(metrics["daily_metrics"]["breakdown_by_agent"], 
                        key=lambda x: x["requests"]),
        "cost_trend": metrics["daily_metrics"]["cost_trend"],
        "alerts": metrics.get("alerts", [])
    }
```

### Alertas Automáticas

El sistema incluye alertas automáticas configurables:

- **Límite de Costos**: Alerta cuando se alcanza 80% del límite diario/mensual
- **Errores de IA**: Notificación cuando hay fallos en proveedores
- **Rendimiento**: Alerta si el tiempo de respuesta supera umbrales
- **Uso Anómalo**: Detección de patrones inusuales de uso

### Optimización de Costos

1. **Selección Automática de Modelo**: Usa el modelo más económico apropiado
2. **Cache de Respuestas**: Respuestas similares se cachean por 1 hora
3. **Batch Processing**: Agrupa requests similares
4. **Rate Limiting**: Limita requests por usuario/hora

## Ejemplos Prácticos

### Ejemplo 1: Consulta de Venta

**Input**:
```json
{
  "message": "Quiero comprar un iPhone, tengo $800 de presupuesto",
  "user_id": 123
}
```

**Process**:
1. Router detecta intención de "venta" → Sales Assistant
2. Sales Assistant analiza presupuesto ($800)
3. Busca iPhones en rango de precio en Qdrant
4. Genera recomendación personalizada

**Output**:
```json
{
  "response": "Con tu presupuesto de $800, te recomiendo el iPhone 14 de 128GB por $729. Es una excelente opción con cámara dual de 12MP, chip A15 Bionic y soporte para 5G. Te quedarían $71 para un case y protector de pantalla.",
  "recommendations": [
    {
      "product_id": 5,
      "name": "iPhone 14 128GB",
      "price": 729.99,
      "confidence_score": 0.92
    }
  ]
}
```

### Ejemplo 2: Consulta Técnica

**Input**:
```json
{
  "message": "¿Cuánta memoria RAM tiene el MacBook Pro M3?",
  "user_id": 456
}
```

**Process**:
1. Router detecta "especificaciones" → Product Expert
2. Product Expert busca información técnica específica
3. Proporciona respuesta detallada

**Output**:
```json
{
  "response": "El MacBook Pro con chip M3 tiene las siguientes opciones de memoria:\n\n- MacBook Pro 14\" M3: 8GB unificada (configurable hasta 24GB)\n- MacBook Pro 16\" M3 Pro: 18GB unificada (configurable hasta 36GB)\n- MacBook Pro 16\" M3 Max: 36GB unificada (configurable hasta 128GB)\n\nLa memoria es del tipo LPDDR5 integrada en el chip para máximo rendimiento."
}
```

### Ejemplo 3: Soporte Técnico

**Input**:
```json
{
  "message": "Mi iPhone no enciende, ¿qué puedo hacer?",
  "user_id": 789
}
```

**Process**:
1. Router detecta "problema" → Technical Support
2. Technical Support genera guía de diagnóstico
3. Proporciona pasos de solución

**Output**:
```json
{
  "response": "Te ayudo a solucionar el problema. Sigue estos pasos:\n\n1. **Forzar reinicio**: Mantén presionados Volume Up + Volume Down + Botón lateral por 10 segundos\n2. **Verificar carga**: Conecta a cargador por 30 minutos, debe aparecer símbolo de batería\n3. **Cargador original**: Asegúrate de usar cable y adaptador Apple originales\n\n¿Alguno de estos pasos funcionó? Si no, puede ser necesario llevar el dispositivo a revisión técnica.",
  "follow_up_suggestions": [
    "El paso 1 funcionó",
    "Sigue sin encender",
    "¿Dónde puedo llevarlo a revisión?"
  ]
}
```

## Resolución de Problemas

### Problemas Comunes

1. **Error 401 - API Key inválida**
   - Verificar que las API keys estén configuradas correctamente
   - Revisar que no hayan expirado

2. **Error 429 - Límite de costos excedido**
   - Revisar métricas de uso
   - Ajustar límites si es necesario
   - Verificar uso anómalo

3. **Respuestas lentas**
   - Verificar latencia de proveedores de IA
   - Revisar conexión a Redis/Qdrant
   - Considerar optimizar prompts

4. **Sin recomendaciones de productos**
   - Verificar que Qdrant esté funcionando
   - Revisar que hay productos en la base de datos
   - Verificar embeddings

### Logs y Debugging

```bash
# Ver logs del contenedor
docker logs backend-1 -f

# Verificar estado de servicios
curl http://localhost:8000/ai-agent/health

# Ver métricas en tiempo real
curl http://localhost:8000/ai-agent/metrics

# Verificar Redis
docker exec -it redis-1 redis-cli ping
```

## Conclusión

Este sistema de agentes de IA proporciona una solución completa y escalable para asistencia conversacional en el backend de AppleStore. Con su arquitectura modular, soporte multi-proveedor y monitoreo completo de costos, está diseñado para manejar desde consultas simples hasta interacciones complejas con múltiples agentes especializados.

La implementación está lista para producción y puede escalarse horizontalmente agregando más instancias de agentes o implementando balanceadores de carga especializados.
