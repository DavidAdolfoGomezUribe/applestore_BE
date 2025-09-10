def obtener_mensajes_por_chat(conn, chat_id):
    """
    Obtiene todos los mensajes de un chat.
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM mensajes WHERE chat_id = %s ORDER BY created_at ASC", (chat_id,))
    return cursor.fetchall()
