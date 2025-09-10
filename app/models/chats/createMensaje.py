def crear_mensaje(conn, chat_id, sender, message):
    """
    Crea un nuevo mensaje en un chat.
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mensajes (chat_id, sender, message) VALUES (%s, %s, %s)",
        (chat_id, sender, message)
    )
    conn.commit()
    return cursor.lastrowid
