def delete_chat(conn, chat_id):
    """
    Elimina un chat y todos sus mensajes por ID.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat a eliminar
    """
    cursor = conn.cursor()
    # Los mensajes se eliminan automáticamente por CASCADE
    cursor.execute("DELETE FROM chats WHERE id = %s", (chat_id,))
    conn.commit()
    return cursor.rowcount > 0

def delete_message(conn, message_id):
    """
    Elimina un mensaje específico.
    
    Args:
        conn: Conexión a la base de datos
        message_id: ID del mensaje a eliminar
    
    Returns:
        bool: True si se eliminó, False si no existía
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE id = %s", (message_id,))
    conn.commit()
    return cursor.rowcount > 0

def delete_messages_chat(conn, chat_id):
    """
    Elimina todos los mensajes de un chat específico.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
    
    Returns:
        int: Número de mensajes eliminados
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE chat_id = %s", (chat_id,))
    deleted_count = cursor.rowcount
    
    # Resetear último mensaje del chat
    cursor.execute(
        "UPDATE chats SET last_message = NULL, unread_count = 0 WHERE id = %s",
        (chat_id,)
    )
    
    conn.commit()
    return deleted_count
