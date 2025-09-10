def obtener_chat_por_id(conn, chat_id):
    """
    Obtiene un chat por su ID.
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM chats WHERE id = %s", (chat_id,))
    return cursor.fetchone()
