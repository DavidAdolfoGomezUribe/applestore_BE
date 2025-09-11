def crear_mensaje(conn, chat_id, sender, body, is_edited=False):
    """
    Crea un nuevo mensaje en un chat.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
        sender: Quien envía el mensaje ('user', 'bot', 'system')
        body: Contenido del mensaje
        is_edited: Si el mensaje fue editado (default: False)
    
    Returns:
        int: ID del mensaje creado
    """
    cursor = conn.cursor()
    
    # Crear el mensaje
    cursor.execute(
        """INSERT INTO messages (chat_id, sender, body, is_edited) 
           VALUES (%s, %s, %s, %s)""",
        (chat_id, sender, body, is_edited)
    )
    message_id = cursor.lastrowid
    
    # Actualizar el último mensaje y actividad del chat
    actualizar_ultimo_mensaje_chat(conn, chat_id, body)
    
    # Si el mensaje es del usuario, incrementar contador de no leídos
    if sender == 'user':
        incrementar_mensajes_no_leidos(conn, chat_id)
    
    conn.commit()
    return message_id

def actualizar_ultimo_mensaje_chat(conn, chat_id, last_message):
    """
    Actualiza el último mensaje y la última actividad de un chat.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
        last_message: Último mensaje
    """
    cursor = conn.cursor()
    # Truncar el mensaje si es muy largo para el preview
    preview_message = last_message[:100] + "..." if len(last_message) > 100 else last_message
    
    cursor.execute(
        """UPDATE chats 
           SET last_message = %s, last_activity = NOW() 
           WHERE id = %s""",
        (preview_message, chat_id)
    )

def incrementar_mensajes_no_leidos(conn, chat_id):
    """
    Incrementa el contador de mensajes no leídos de un chat.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE chats SET unread_count = unread_count + 1 WHERE id = %s",
        (chat_id,)
    )

def marcar_mensajes_como_leidos(conn, chat_id):
    """
    Marca todos los mensajes de un chat como leídos (resetea contador).
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE chats SET unread_count = 0 WHERE id = %s",
        (chat_id,)
    )
    conn.commit()
