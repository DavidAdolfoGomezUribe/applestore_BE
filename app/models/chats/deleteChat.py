def eliminar_chat(conn, chat_id):
    """
    Elimina un chat por su ID.
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats WHERE id=%s", (chat_id,))
    conn.commit()
