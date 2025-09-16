# 🤖 Sistema de Agentes IA con Arquitectura de Grafos

## Descripción General

El sistema de agentes IA implementa una arquitectura de grafos inteligente que permite:

- **Detección automática de intenciones** usando triggers y patrones
- **Routing inteligente** hacia agentes especializados
- **Múltiples proveedores de IA** (Gemini, OpenAI, Anthropic)
- **Tracking de costos en tiempo real** con Redis
- **Integración con múltiples canales** (WhatsApp, Web Chat, Telegram)
- **Escalamiento automático** a agentes humanos cuando es necesario

## Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Bot WhatsApp  │    │   Bot Web Chat  │    │  Bot Telegram   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    Intent Detector        │
                    │   (Trigger Analysis)      │
                    └─────────────┬─────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
       ┌────────▼────────┐  ┌────▼────┐  ┌───────▼────────┐
       │ Direct Response │  │ Agents  │  │ Human Escalate │
       └─────────────────┘  └────┬────┘  └────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
    ┌─────▼─────┐     ┌─────────▼────────┐     ┌───────▼────────┐
    │   Sales   │     │  Technical       │     │    Product     │
    │ Assistant │     │  Support         │     │    Expert      │
    └───────────┘     └──────────────────┘     └────────────────┘
```

## Componentes Principales

### 1. Intent Detector & Router
- **Ubicación**: `services/ai/routing.py`
- **Función**: Detecta intenciones y determina el flujo apropiado
- **Triggers soportados**:
  - Saludos y despedidas
  - Consultas de productos
  - Preguntas de precios
  - Soporte técnico
  - Comparaciones
  - Intención de compra
  - Quejas (escalamiento automático)

### 2. Agentes Especializados
- **Ubicación**: `services/ai/nodes.py`
- **Tipos disponibles**:
  - `sales_assistant`: Especializado en ventas y recomendaciones
  - `technical_support`: Soporte técnico y resolución de problemas
  - `product_expert`: Conocimiento profundo de productos Apple
  - `general_assistant`: Asistente de propósito general

### 3. Orquestador de Grafos
- **Ubicación**: `services/ai/orchestrator.py`
- **Función**: Coordina todo el flujo del sistema
- **Responsabilidades**:
  - Gestión de conversaciones
  - Tracking de costos
  - Integración con base de datos
  - Manejo de errores

### 4. Sistema de Costos
- **Ubicación**: `services/ai/cost_tracker.py`
- **Características**:
  - Tracking en tiempo real con Redis
  - Soporte para múltiples modelos
  - Límites diarios/mensuales configurables
  - Reportes detallados

## API Endpoints Principales

### Procesamiento de Mensajes

```http
POST /ai-agent/process
```

**Ejemplo de uso:**
```json
{
  "message": "Hola, necesito un iPhone para fotografía",
  "bot_type": "web_chat_bot",
  "chat_id": 123,
  "user_id": 456,
  "save_to_chat": true
}
```

**Respuesta:**
```json
{
  "response": "¡Hola! Para fotografía te recomiendo el iPhone 15 Pro...",
  "intent": "product_inquiry",
  "confidence": 0.89,
  "agent_used": "sales_assistant",
  "cost": 0.0025,
  "processing_time": 1.24,
  "recommendations": [...]
}
```

### Mensaje Directo a Agente

```http
POST /ai-agent/agent/direct
```

**Ejemplo:**
```json
{
  "message": "Compara iPhone 15 vs iPhone 15 Pro",
  "agent_type": "product_expert",
  "chat_id": 123
}
```

### Métricas del Sistema

```http
GET /ai-agent/metrics
```

Retorna métricas completas incluyendo costos, uso por agente, y estadísticas de intenciones.

### Resumen de Costos

```http
GET /ai-agent/costs/summary?period=daily
```

## Configuración de Proveedores

### Gemini (Por Defecto)
```bash
DEFAULT_AI_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
```

### OpenAI
```bash
DEFAULT_AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
```

### Cambio de Proveedor en Runtime
```http
POST /ai-agent/config/provider
{
  "provider": "openai"
}
```

## Configuración de Costos

```bash
COST_TRACKING_ENABLED=true
DAILY_COST_LIMIT=50.0
MONTHLY_COST_LIMIT=1000.0
REDIS_URL=redis://localhost:6379
```

## Integración con Canales

### Bot de WhatsApp
```python
from services.ai.orchestrator import graph_orchestrator
from services.ai.routing import BotType

# Procesar mensaje de WhatsApp
result = await graph_orchestrator.process_message(
    message=whatsapp_message,
    bot_type=BotType.WHATSAPP_BOT,
    chat_id=chat_id,
    user_id=user_id
)
```

### Bot de Web Chat
```python
# Similar al de WhatsApp pero con BotType.WEB_CHAT_BOT
result = await graph_orchestrator.process_message(
    message=web_message,
    bot_type=BotType.WEB_CHAT_BOT,
    chat_id=chat_id
)
```

## Triggers y Patrones

### Ejemplos de Detección de Intenciones

| Intent | Keywords | Patterns | Ejemplo |
|--------|----------|-----------|---------|
| `product_inquiry` | iphone, mac, ipad | `\b(iphone\|mac\|ipad)\b` | "Necesito un iPhone" |
| `price_question` | precio, costo, vale | `\bcuánto\s+(cuesta\|vale)` | "¿Cuánto cuesta el MacBook?" |
| `technical_support` | problema, error, no funciona | `\bno\s+funciona\b` | "Mi iPad no funciona" |
| `comparison` | comparar, diferencia, vs | `\bvs\b`, `diferencia\s+entre` | "iPhone vs Samsung" |

## Monitoreo y Métricas

### Dashboard de Costos
- Costo diario/mensual en tiempo real
- Breakdown por agente y modelo
- Alertas de límites
- Tendencias de uso

### Métricas de Conversación
- Distribución de intenciones
- Tiempo de respuesta por agente
- Tasa de escalamiento a humanos
- Satisfacción del usuario (futuro)

## Escalabilidad

### Agregar Nuevos Agentes
1. Definir configuración en `config.py`
2. Implementar nodo especializado en `nodes.py`
3. Agregar routing en `routing.py`

### Agregar Nuevos Proveedores
1. Extender enum `AIProvider` en `config.py`
2. Implementar integración en `nodes.py`
3. Configurar costos en `cost_tracker.py`

### Agregar Nuevos Canales
1. Extender enum `BotType` en `routing.py`
2. Implementar lógica específica del canal
3. Configurar triggers específicos si es necesario

## Casos de Uso

### 1. Bot de WhatsApp E-commerce
```python
# El bot de WhatsApp no encuentra trigger específico
if not found_specific_trigger:
    result = await graph_orchestrator.process_message(
        message=user_message,
        bot_type=BotType.WHATSAPP_BOT,
        chat_id=whatsapp_chat_id
    )
    send_whatsapp_message(result["response"])
```

### 2. Chat Web con Contexto
```python
# Mantener contexto de conversación web
result = await graph_orchestrator.process_message(
    message=user_input,
    bot_type=BotType.WEB_CHAT_BOT,
    chat_id=session_id,
    save_to_chat=True,
    context={"page": "product_detail", "product_id": 123}
)
```

### 3. Soporte Técnico Automatizado
```python
# Detección automática de problemas técnicos
if result["intent"] == "technical_support":
    # Escalamiento automático si es necesario
    if result.get("escalated_to_human"):
        notify_support_team(chat_id, user_message)
```

## Mantenimiento

### Logs Importantes
- `/logs/ai_agents.log`: Actividad de agentes
- `/logs/cost_tracking.log`: Tracking de costos
- `/logs/routing.log`: Decisiones de routing

### Comandos de Diagnóstico
```bash
# Verificar estado del sistema
curl GET /ai-agent/health

# Verificar límites de costo
curl GET /ai-agent/costs/limits

# Obtener métricas completas
curl GET /ai-agent/metrics
```

### Backup y Recuperación
- **Redis**: Backup diario de métricas de costos
- **Configuraciones**: Versionado en Git
- **Logs**: Rotación automática cada 7 días

## Próximas Mejoras

1. **Análisis de Sentimientos**: Detectar frustración del usuario
2. **Personalización**: Agentes adaptativos por usuario
3. **Multiidioma**: Soporte para múltiples idiomas
4. **A/B Testing**: Pruebas de diferentes configuraciones
5. **Machine Learning**: Mejora automática de triggers
