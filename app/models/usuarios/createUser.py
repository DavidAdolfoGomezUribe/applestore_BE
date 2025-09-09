def crear_usuario(conn, name, email, password):
    """
    Crea un nuevo usuario en la base de datos.
    Args:
        conn: conexión activa a MySQL
        name: nombre del usuario
        email: email del usuario
        password: contraseña (encriptada o no)
    Returns:
        ID del usuario creado
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO usuarios (name, email, password) VALUES (%s, %s, %s)",
        (name, email, password)
    )
    conn.commit()
    return cursor.lastrowid
