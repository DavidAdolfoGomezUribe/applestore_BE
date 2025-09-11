# 💬 Chat API Documentation

## Descripción General

Sistema de chat completo diseñado principalmente para WhatsApp, con capacidad de manejar conversaciones entre usuarios y bots. El sistema incluye gestión de chats, mensajes, contadores de no leídos y búsqueda.

## 🏗️ Arquitectura

### Base de Datos
- **chats**: Conversaciones principales con metadatos
- **messages**: Mensajes individuales con información de sender

### Componentes
- **Models**: Funciones de acceso a datos
- **Services**: Lógica de negocio
- **Routes**: Endpoints de API
- **Schemas**: Validación con Pydantic

## 📱 Casos de Uso Principales

### 1. Chat tipo WhatsApp Web
```
┌─────────────────┬─────────────────────────────┐
│ Lista de Chats  │        Conversación         │
├─────────────────┼─────────────────────────────┤
│ Juan Pérez      │                         Hola │ ◄─ Usuario
│ +57310571...    │                    10:29 AM  │
│ Hola            │                              │
│ ● 2             │  ¡Hola! ¿En qué puedo... ► │ ◄─ Bot  
├─────────────────│                    10:30 AM  │
│ María García    │                              │
│ Gracias por...  │                 Perfecto ► │
│                 │                    10:31 AM  │
└─────────────────┴─────────────────────────────┘
```

### 2. Dashboard de Administración
- Ver todos los chats activos
- Responder como bot
- Buscar conversaciones
- Gestionar contactos

## 🚀 Endpoints Principales

### Gestión de Chats

#### `POST /chats/`
Crear o obtener chat por número de teléfono.

**Request:**
```json
{
    "phone_number": "+573105714739",
    "contact_name": "Juan Pérez",
    "user_id": 1
}
```

**Response:**
```json
{
    "id": 1,
    "phone_number": "+573105714739",
    "contact_name": "Juan Pérez",
    "user_id": 1,
    "last_message": "Hola",
    "unread_count": 2,
    "created_at": "2025-09-11T10:00:00",
    "last_activity": "2025-09-11T10:30:00"
}
```

#### `GET /chats/`
Listar todos los chats con paginación.

**Query Parameters:**
- `limit`: Máximo 100 (default: 50)
- `offset`: Para paginación (default: 0)

#### `GET /chats/unread`
Chats con mensajes no leídos.

#### `GET /chats/search?q=termo`
Buscar chats por número o nombre.

#### `GET /chats/{chat_id}/full`
Chat completo con mensajes (marca como leído automáticamente).

**Response:**
```json
{
    "id": 1,
    "phone_number": "+573105714739",
    "contact_name": "Juan Pérez",
    "last_message": "Perfecto",
    "unread_count": 0,
    "created_at": "2025-09-11T10:00:00",
    "last_activity": "2025-09-11T10:31:00",
    "messages": [
        {
            "id": 1,
            "chat_id": 1,
            "sender": "user",
            "body": "Hola",
            "is_edited": false,
            "created_at": "2025-09-11T10:29:00"
        },
        {
            "id": 2,
            "chat_id": 1,
            "sender": "bot",
            "body": "¡Hola! ¿En qué puedo ayudarte?",
            "is_edited": false,
            "created_at": "2025-09-11T10:30:00"
        }
    ]
}
```

### Gestión de Mensajes

#### `POST /chats/{chat_id}/messages`
Enviar nuevo mensaje.

**Request:**
```json
{
    "chat_id": 1,
    "sender": "bot",
    "body": "¡Hola! ¿En qué puedo ayudarte?"
}
```

#### `GET /chats/{chat_id}/messages`
Obtener mensajes con paginación.

#### `GET /chats/{chat_id}/messages/search?q=termo`
Buscar mensajes en un chat.

#### `PUT /chats/messages/{message_id}`
Editar mensaje existente.

**Request:**
```json
{
    "body": "Mensaje editado"
}
```

### Utilidades

#### `PUT /chats/{chat_id}/mark-read`
Marcar chat como leído (resetea contador).

#### `PUT /chats/{chat_id}/contact-name?contact_name=Nuevo`
Actualizar nombre de contacto.

## 🔧 Funcionalidades Automáticas

### 1. Gestión de Actividad
- **last_activity** se actualiza automáticamente con cada mensaje
- **last_message** se actualiza como preview (truncado a 100 chars)

### 2. Contador de No Leídos
- Se incrementa automáticamente con mensajes de `user`
- Se resetea con `mark-read` o al obtener chat completo
- No se incrementa con mensajes de `bot` o `system`

### 3. Búsqueda Inteligente
- Por número de teléfono (parcial)
- Por nombre de contacto (parcial)
- Por contenido de mensajes

### 4. Prevención de Duplicados
- Un teléfono = un chat
- Al crear chat existente, retorna el actual

## 📊 Schemas de Datos

### ChatCreate
```python
{
    "phone_number": str,      # Requerido
    "contact_name": str,      # Opcional
    "user_id": int           # Opcional
}
```

### MessageCreate
```python
{
    "chat_id": int,          # Requerido
    "sender": "user|bot|system", # Requerido
    "body": str              # Requerido
}
```

### Enums
```python
MessageSender: "user" | "bot" | "system"
```

## 🎯 Casos de Uso Específicos

### Webhook de WhatsApp
```python
# 1. Recibir mensaje de WhatsApp
webhook_data = {
    "from": "+573105714739",
    "body": "Hola",
    "timestamp": 1631234567
}

# 2. Crear/obtener chat
chat = POST /chats/ {
    "phone_number": "+573105714739"
}

# 3. Guardar mensaje del usuario
message = POST /chats/{chat.id}/messages {
    "chat_id": chat.id,
    "sender": "user", 
    "body": "Hola"
}

# 4. Procesar con bot y responder
bot_response = process_with_bot(message.body)

response_message = POST /chats/{chat.id}/messages {
    "chat_id": chat.id,
    "sender": "bot",
    "body": bot_response
}
```

### Dashboard Admin
```python
# 1. Listar chats con no leídos primero
unread_chats = GET /chats/unread
all_chats = GET /chats/?limit=20

# 2. Ver conversación completa
conversation = GET /chats/{chat_id}/full

# 3. Responder como bot
response = POST /chats/{chat_id}/messages {
    "sender": "bot",
    "body": "Respuesta del administrador"
}
```

### Búsqueda y Filtros
```python
# Buscar chat por número
chats = GET /chats/search?q=57310

# Buscar chat por nombre  
chats = GET /chats/search?q=Juan

# Buscar mensajes en chat
messages = GET /chats/1/messages/search?q=iPhone
```

## ⚡ Optimizaciones

### Paginación
- Chats: max 100 por request
- Mensajes: max 200 por request

### Índices de Base de Datos
- `phone_number` (búsqueda rápida)
- `last_activity` (ordenamiento)
- `chat_id` en mensajes
- `created_at` en mensajes

### Manejo de Errores
- Validación automática con Pydantic
- HTTP status codes apropiados
- Mensajes de error descriptivos

## 🛡️ Consideraciones de Seguridad

- Validación de entrada en todos los endpoints
- Límites en longitud de mensajes
- Sanitización de números de teléfono
- Rate limiting recomendado para webhooks

## 📈 Métricas Disponibles

- Total de chats activos
- Mensajes por chat
- Chats con mensajes no leídos
- Actividad por fecha (via last_activity)

---

**Nota**: Este sistema está optimizado para WhatsApp pero es extensible para otros canales como Telegram o chat web.
