def obtener_usuario_por_id(conn, user_id):
    """
    Obtiene un usuario por su ID.
    Args:
        conn: conexión activa a MySQL
        user_id: ID del usuario
    Returns:
        Diccionario con los datos del usuario o None
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    return cursor.fetchone()
