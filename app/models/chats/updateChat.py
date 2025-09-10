def cerrar_chat(conn, chat_id):
    """
    Marca un chat como cerrado (asigna fecha de cierre).
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE chats SET closed_at=NOW() WHERE id=%s",
        (chat_id,)
    )
    conn.commit()
