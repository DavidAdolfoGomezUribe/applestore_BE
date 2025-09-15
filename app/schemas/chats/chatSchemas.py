from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ========== ENUMS ==========
class MessageSender(str, Enum):
    USER = "user"
    BOT = "bot"
    SYSTEM = "system"

# ========== SCHEMAS DE CHAT ==========

class ChatBase(BaseModel):
    phone_number: Optional[str] = Field(None, max_length=20, description="Número de teléfono de WhatsApp")
    email: Optional[str] = Field(None, max_length=100, description="Email alternativo para chat web")


class ChatCreate(ChatBase):
    user_id: Optional[int] = Field(None, description="ID del usuario (opcional)")

    class Config:
        schema_extra = {
            "examples": [
                {
                    "phone_number": "+573105714739",
                    "user_id": 1
                },
                {
                    "email": "juan@example.com",
                    "user_id": 1
                }
            ]
        }


class ChatResponse(ChatBase):
    id: int
    user_id: Optional[int]
    last_message: Optional[str] = Field(None, description="Último mensaje para preview")
    created_at: datetime
    last_activity: datetime

    class Config:
        from_attributes = True

# ========== SCHEMAS DE MENSAJES ==========
class MessageBase(BaseModel):
    sender: MessageSender = Field(..., description="Quien envía el mensaje")
    body: str = Field(..., description="Contenido del mensaje")

class MessageCreate(MessageBase):
    chat_id: int = Field(..., description="ID del chat")

    class Config:
        schema_extra = {
            "examples": [
                {
                    "chat_id": 1,
                    "sender": "user",
                    "body": "Hola, quiero información sobre iPhones"
                },
                {
                    "chat_id": 1,
                    "sender": "bot",
                    "body": "¡Hola! Te puedo ayudar con información sobre nuestros iPhones. ¿Qué modelo te interesa?"
                }
            ]
        }

class MessageResponse(MessageBase):
    id: int
    chat_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MessageUpdate(BaseModel):
    """Para actualizar un mensaje"""
    body: Optional[str] = None

# ========== SCHEMAS COMPUESTOS ==========
class ChatWithMessages(ChatResponse):
    """Chat con sus mensajes incluidos"""
    messages: List[MessageResponse] = []
