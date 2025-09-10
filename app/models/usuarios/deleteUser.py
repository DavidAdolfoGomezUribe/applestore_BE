def eliminar_usuario(conn, user_id):
    """
    Elimina un usuario por su ID.
    Args:
        conn: conexión activa a MySQL
        user_id: ID del usuario
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=%s", (user_id,))
    conn.commit()
