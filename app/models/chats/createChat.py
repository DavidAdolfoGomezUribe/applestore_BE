def crear_chat(conn, user_id, source):
    """
    Crea un nuevo chat (conversación).
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chats (user_id, source) VALUES (%s, %s)",
        (user_id, source)
    )
    conn.commit()
    return cursor.lastrowid
