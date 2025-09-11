import os
from dotenv import load_dotenv
from typing import List, Optional
from database import get_connection
from models.chats.createChat import crear_chat, obtener_o_crear_chat
from models.chats.getChat import obtener_chat_por_id
from models.chats.updateChat import actualizar_nombre_contacto, marcar_chat_como_leido, editar_mensaje
from models.chats.deleteChat import eliminar_chat, eliminar_mensaje
from models.chats.createMensaje import crear_mensaje
from schemas.chats.chatSchemas import ChatCreate, ChatResponse, MessageCreate, MessageResponse, ChatWithMessages

load_dotenv()

# ========== FUNCIONES AUXILIARES ==========

def obtener_todos_los_chats(conn, limit=50, offset=0):
    """Obtiene todos los chats con paginación"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM chats ORDER BY last_activity DESC LIMIT %s OFFSET %s",
        (limit, offset)
    )
    return cursor.fetchall()

def obtener_chats_con_mensajes_no_leidos(conn):
    """Obtiene chats que tienen mensajes no leídos"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM chats WHERE unread_count > 0 ORDER BY last_activity DESC")
    return cursor.fetchall()

def buscar_chats(conn, search_term: str):
    """Busca chats por número de teléfono o nombre de contacto"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT * FROM chats 
           WHERE phone_number LIKE %s OR contact_name LIKE %s 
           ORDER BY last_activity DESC""",
        (f"%{search_term}%", f"%{search_term}%")
    )
    return cursor.fetchall()

def obtener_mensajes_por_chat(conn, chat_id: int, limit=50, offset=0):
    """Obtiene mensajes de un chat específico"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT * FROM messages 
           WHERE chat_id = %s 
           ORDER BY created_at DESC 
           LIMIT %s OFFSET %s""",
        (chat_id, limit, offset)
    )
    return cursor.fetchall()

def obtener_ultimo_mensaje_chat(conn, chat_id: int):
    """Obtiene el último mensaje de un chat"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM messages WHERE chat_id = %s ORDER BY created_at DESC LIMIT 1",
        (chat_id,)
    )
    return cursor.fetchone()

def contar_mensajes_chat(conn, chat_id: int) -> int:
    """Cuenta los mensajes de un chat"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM messages WHERE chat_id = %s", (chat_id,))
    return cursor.fetchone()['total']

def obtener_mensajes_por_sender(conn, chat_id: int, sender: str):
    """Obtiene mensajes de un chat filtrados por remitente"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT * FROM messages 
           WHERE chat_id = %s AND sender = %s 
           ORDER BY created_at DESC""",
        (chat_id, sender)
    )
    return cursor.fetchall()

def buscar_mensajes_en_chat(conn, chat_id: int, search_term: str):
    """Busca mensajes en un chat específico"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT * FROM messages 
           WHERE chat_id = %s AND body LIKE %s 
           ORDER BY created_at DESC""",
        (chat_id, f"%{search_term}%")
    )
    return cursor.fetchall()

# ========== SERVICIOS DE CHAT ==========

def create_chat_service(chat_data: ChatCreate) -> ChatResponse:
    """
    Crea un nuevo chat o obtiene uno existente por teléfono.
    
    Args:
        chat_data: Datos del chat a crear
    
    Returns:
        ChatResponse: Chat creado o existente
    """
    conn = get_connection()
    try:
        # Usar función inteligente que busca o crea
        chat = obtener_o_crear_chat(
            conn, 
            chat_data.phone_number, 
            chat_data.user_id, 
            chat_data.contact_name
        )
        
        return ChatResponse(
            id=chat['id'],
            user_id=chat['user_id'],
            phone_number=chat['phone_number'],
            contact_name=chat['contact_name'],
            last_message=chat.get('last_message'),
            unread_count=chat.get('unread_count', 0),
            created_at=chat.get('created_at'),
            last_activity=chat.get('last_activity')
        )
    finally:
        conn.close()

def get_chat_service(chat_id: int) -> Optional[ChatResponse]:
    """
    Obtiene un chat por ID.
    
    Args:
        chat_id: ID del chat
    
    Returns:
        ChatResponse o None si no existe
    """
    conn = get_connection()
    try:
        chat = obtener_chat_por_id(conn, chat_id)
        if not chat:
            return None
            
        return ChatResponse(
            id=chat['id'],
            user_id=chat['user_id'],
            phone_number=chat['phone_number'],
            contact_name=chat['contact_name'],
            last_message=chat['last_message'],
            unread_count=chat['unread_count'],
            created_at=chat['created_at'],
            last_activity=chat['last_activity']
        )
    finally:
        conn.close()

def get_all_chats_service(limit: int = 50, offset: int = 0) -> List[ChatResponse]:
    """
    Obtiene todos los chats con paginación.
    
    Args:
        limit: Límite de resultados
        offset: Offset para paginación
    
    Returns:
        Lista de chats
    """
    conn = get_connection()
    try:
        chats = obtener_todos_los_chats(conn, limit, offset)
        
        return [
            ChatResponse(
                id=chat['id'],
                user_id=chat['user_id'],
                phone_number=chat['phone_number'],
                contact_name=chat['contact_name'],
                last_message=chat['last_message'],
                unread_count=chat['unread_count'],
                created_at=chat['created_at'],
                last_activity=chat['last_activity']
            )
            for chat in chats
        ]
    finally:
        conn.close()

def get_unread_chats_service() -> List[ChatResponse]:
    """
    Obtiene chats con mensajes no leídos.
    
    Returns:
        Lista de chats con mensajes no leídos
    """
    conn = get_connection()
    try:
        chats = obtener_chats_con_mensajes_no_leidos(conn)
        
        return [
            ChatResponse(
                id=chat['id'],
                user_id=chat['user_id'],
                phone_number=chat['phone_number'],
                contact_name=chat['contact_name'],
                last_message=chat['last_message'],
                unread_count=chat['unread_count'],
                created_at=chat['created_at'],
                last_activity=chat['last_activity']
            )
            for chat in chats
        ]
    finally:
        conn.close()

def search_chats_service(search_term: str) -> List[ChatResponse]:
    """
    Busca chats por número o nombre.
    
    Args:
        search_term: Término de búsqueda
    
    Returns:
        Lista de chats que coinciden
    """
    conn = get_connection()
    try:
        chats = buscar_chats(conn, search_term)
        
        return [
            ChatResponse(
                id=chat['id'],
                user_id=chat['user_id'],
                phone_number=chat['phone_number'],
                contact_name=chat['contact_name'],
                last_message=chat['last_message'],
                unread_count=chat['unread_count'],
                created_at=chat['created_at'],
                last_activity=chat['last_activity']
            )
            for chat in chats
        ]
    finally:
        conn.close()

def update_chat_contact_name_service(chat_id: int, contact_name: str) -> bool:
    """
    Actualiza el nombre de contacto de un chat.
    
    Args:
        chat_id: ID del chat
        contact_name: Nuevo nombre
    
    Returns:
        True si se actualizó correctamente
    """
    conn = get_connection()
    try:
        actualizar_nombre_contacto(conn, chat_id, contact_name)
        return True
    except Exception:
        return False
    finally:
        conn.close()

def mark_chat_as_read_service(chat_id: int) -> bool:
    """
    Marca un chat como leído.
    
    Args:
        chat_id: ID del chat
    
    Returns:
        True si se marcó correctamente
    """
    conn = get_connection()
    try:
        marcar_chat_como_leido(conn, chat_id)
        return True
    except Exception:
        return False
    finally:
        conn.close()

def delete_chat_service(chat_id: int) -> bool:
    """
    Elimina un chat.
    
    Args:
        chat_id: ID del chat
    
    Returns:
        True si se eliminó correctamente
    """
    conn = get_connection()
    try:
        return eliminar_chat(conn, chat_id)
    finally:
        conn.close()

# ========== SERVICIOS DE MENSAJES ==========

def create_message_service(message_data: MessageCreate) -> MessageResponse:
    """
    Crea un nuevo mensaje.
    
    Args:
        message_data: Datos del mensaje
    
    Returns:
        MessageResponse: Mensaje creado
    """
    conn = get_connection()
    try:
        message_id = crear_mensaje(
            conn,
            message_data.chat_id,
            message_data.sender.value,
            message_data.body
        )
        
        # Obtener el mensaje creado
        messages = obtener_mensajes_por_chat(conn, message_data.chat_id)
        created_message = next((msg for msg in messages if msg['id'] == message_id), None)
        
        if not created_message:
            raise Exception("Error retrieving created message")
        
        return MessageResponse(
            id=created_message['id'],
            chat_id=created_message['chat_id'],
            sender=created_message['sender'],
            body=created_message['body'],
            is_edited=created_message['is_edited'],
            created_at=created_message['created_at']
        )
    finally:
        conn.close()

def get_messages_service(chat_id: int, limit: int = 100, offset: int = 0) -> List[MessageResponse]:
    """
    Obtiene mensajes de un chat.
    
    Args:
        chat_id: ID del chat
        limit: Límite de mensajes
        offset: Offset para paginación
    
    Returns:
        Lista de mensajes
    """
    conn = get_connection()
    try:
        messages = obtener_mensajes_por_chat(conn, chat_id, limit, offset)
        
        return [
            MessageResponse(
                id=msg['id'],
                chat_id=msg['chat_id'],
                sender=msg['sender'],
                body=msg['body'],
                is_edited=msg['is_edited'],
                created_at=msg['created_at']
            )
            for msg in messages
        ]
    finally:
        conn.close()

def get_chat_with_messages_service(chat_id: int) -> Optional[ChatWithMessages]:
    """
    Obtiene un chat con sus mensajes.
    
    Args:
        chat_id: ID del chat
    
    Returns:
        Chat con mensajes o None
    """
    conn = get_connection()
    try:
        # Obtener chat
        chat = obtener_chat_por_id(conn, chat_id)
        if not chat:
            return None
        
        # Obtener mensajes
        messages = obtener_mensajes_por_chat(conn, chat_id)
        
        # Marcar como leído
        marcar_chat_como_leido(conn, chat_id)
        
        return ChatWithMessages(
            id=chat['id'],
            user_id=chat['user_id'],
            phone_number=chat['phone_number'],
            contact_name=chat['contact_name'],
            last_message=chat['last_message'],
            unread_count=0,  # Ya se marcó como leído
            created_at=chat['created_at'],
            last_activity=chat['last_activity'],
            messages=[
                MessageResponse(
                    id=msg['id'],
                    chat_id=msg['chat_id'],
                    sender=msg['sender'],
                    body=msg['body'],
                    is_edited=msg['is_edited'],
                    created_at=msg['created_at']
                )
                for msg in messages
            ]
        )
    finally:
        conn.close()

def edit_message_service(message_id: int, new_body: str) -> bool:
    """
    Edita un mensaje.
    
    Args:
        message_id: ID del mensaje
        new_body: Nuevo contenido
    
    Returns:
        True si se editó correctamente
    """
    conn = get_connection()
    try:
        editar_mensaje(conn, message_id, new_body)
        return True
    except Exception:
        return False
    finally:
        conn.close()

def delete_message_service(message_id: int) -> bool:
    """
    Elimina un mensaje.
    
    Args:
        message_id: ID del mensaje
    
    Returns:
        True si se eliminó correctamente
    """
    conn = get_connection()
    try:
        return eliminar_mensaje(conn, message_id)
    finally:
        conn.close()

def search_messages_service(chat_id: int, search_term: str) -> List[MessageResponse]:
    """
    Busca mensajes en un chat.
    
    Args:
        chat_id: ID del chat
        search_term: Término de búsqueda
    
    Returns:
        Lista de mensajes que coinciden
    """
    conn = get_connection()
    try:
        messages = buscar_mensajes_en_chat(conn, chat_id, search_term)
        
        return [
            MessageResponse(
                id=msg['id'],
                chat_id=msg['chat_id'],
                sender=msg['sender'],
                body=msg['body'],
                is_edited=msg['is_edited'],
                created_at=msg['created_at']
            )
            for msg in messages
        ]
    finally:
        conn.close()