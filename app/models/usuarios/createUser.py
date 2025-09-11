def crear_usuario(conn, name, email, password, role="user"):
    """
    Crea un nuevo usuario en la base de datos.
    Args:
        conn: conexión activa a MySQL
        name: nombre del usuario
        email: email del usuario
        password: contraseña (encriptada o no)
        role: rol del usuario (default: "user")
    Returns:
        ID del usuario creado
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
        (name, email, password, role)
    )
    conn.commit()
    return cursor.lastrowid
