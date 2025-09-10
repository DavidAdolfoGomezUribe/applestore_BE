def actualizar_usuario(conn, user_id, name, email):
    """
    Actualiza los datos de un usuario.
    Args:
        conn: conexión activa a MySQL
        user_id: ID del usuario
        name: nuevo nombre
        email: nuevo email
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET name=%s, email=%s WHERE id=%s",
        (name, email, user_id)
    )
    conn.commit()
