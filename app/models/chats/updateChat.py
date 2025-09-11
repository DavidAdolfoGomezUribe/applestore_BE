def actualizar_nombre_contacto(conn, chat_id, contact_name):
    """
    Actualiza el nombre del contacto de un chat.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
        contact_name: Nuevo nombre del contacto
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE chats SET contact_name = %s WHERE id = %s",
        (contact_name, chat_id)
    )
    conn.commit()

def actualizar_ultimo_mensaje(conn, chat_id, last_message):
    """
    Actualiza el último mensaje y la última actividad de un chat.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
        last_message: Contenido del último mensaje
    """
    cursor = conn.cursor()
    # Truncar mensaje para preview
    preview_message = last_message[:100] + "..." if len(last_message) > 100 else last_message
    
    cursor.execute(
        """UPDATE chats 
           SET last_message = %s, last_activity = NOW() 
           WHERE id = %s""",
        (preview_message, chat_id)
    )
    conn.commit()

def actualizar_contador_no_leidos(conn, chat_id, unread_count):
    """
    Actualiza el contador de mensajes no leídos.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
        unread_count: Nuevo contador de no leídos
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE chats SET unread_count = %s WHERE id = %s",
        (unread_count, chat_id)
    )
    conn.commit()

def marcar_chat_como_leido(conn, chat_id):
    """
    Marca un chat como leído (resetea contador de no leídos).
    
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

def actualizar_actividad_chat(conn, chat_id):
    """
    Actualiza la última actividad de un chat a NOW().
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE chats SET last_activity = NOW() WHERE id = %s",
        (chat_id,)
    )
    conn.commit()

def editar_mensaje(conn, message_id, new_body):
    """
    Edita el contenido de un mensaje existente.
    
    Args:
        conn: Conexión a la base de datos
        message_id: ID del mensaje
        new_body: Nuevo contenido del mensaje
    """
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE messages 
           SET body = %s, is_edited = TRUE 
           WHERE id = %s""",
        (new_body, message_id)
    )
    conn.commit()
