
from typing import List, Optional
from database import get_connection
from models.chats.createChat import  get_or_create_chat
from models.chats.getChat import get_chat_by_id, get_all_chats, search_chats
from models.chats.deleteChat import delete_chat, delete_message
from models.chats.createMensaje import create_message
from models.chats.getMensajes import get_messages_by_chat, search_messages_in_chat
from schemas.chats.chatSchemas import ChatCreate, ChatResponse, MessageCreate, MessageResponse, ChatWithMessages

# ========== SERVICIOS DE CHAT ==========

def create_chat_service(chat_data: ChatCreate) -> ChatResponse:
    with get_connection() as conn:
        chat = get_or_create_chat(
            conn,
            phone_number=chat_data.phone_number,
            email=getattr(chat_data, 'email', None),
            user_id=chat_data.user_id,
        )
        return ChatResponse(**chat)

def get_chat_service(chat_id: int) -> Optional[ChatResponse]:
    with get_connection() as conn:
        chat = get_chat_by_id(conn, chat_id)
        return ChatResponse(**chat) if chat else None

def get_all_chats_service() -> List[ChatResponse]:
    with get_connection() as conn:
        chats = get_all_chats(conn)
        return [ChatResponse(**chat) for chat in chats]

def search_chats_service(search_term: str) -> List[ChatResponse]:
    with get_connection() as conn:
        chats = search_chats(conn, search_term)
        return [ChatResponse(**chat) for chat in chats]


def delete_chat_service(chat_id: int) -> bool:
    with get_connection() as conn:
        return delete_chat(conn, chat_id)

# ========== SERVICIOS DE MENSAJES ==========

def create_message_service(message_data: MessageCreate) -> MessageResponse:
    with get_connection() as conn:
        message_id = create_message(conn, message_data.chat_id, message_data.sender.value, message_data.body)
        messages = get_messages_by_chat(conn, message_data.chat_id)
        created_message = next((msg for msg in messages if msg['id'] == message_id), None)
        if not created_message:
            raise Exception("Error retrieving created message")
        return MessageResponse(**created_message)

def get_messages_service(chat_id: int, limit: int = 100, offset: int = 0) -> List[MessageResponse]:
    with get_connection() as conn:
        messages = get_messages_by_chat(conn, chat_id, limit, offset)
        return [MessageResponse(**msg) for msg in messages]

def get_chat_with_messages_service(chat_id: int) -> Optional[ChatWithMessages]:
    with get_connection() as conn:
        chat = get_chat_by_id(conn, chat_id)
        if not chat:
            return None
        messages = get_messages_by_chat(conn, chat_id)
        return ChatWithMessages(
            **chat,
            messages=[MessageResponse(**msg) for msg in messages]
        )

def delete_message_service(message_id: int) -> bool:
    with get_connection() as conn:
        return delete_message(conn, message_id)


def search_messages_service(chat_id: int, search_term: str) -> List[MessageResponse]:
    with get_connection() as conn:
        messages = search_messages_in_chat(conn, chat_id, search_term)
        return [MessageResponse(**msg) for msg in messages]