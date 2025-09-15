def create_message(conn, chat_id, sender, body):
    """
    Crea un nuevo mensaje en un chat.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
        sender: Quien envía el mensaje ('user', 'bot', 'system')
        body: Contenido del mensaje
    
    Returns:
        int: ID del mensaje creado
    """
    cursor = conn.cursor(dictionary=True)
    
    # Crear el mensaje
    cursor.execute(
        """INSERT INTO messages (chat_id, sender, body) 
           VALUES (%s, %s, %s)""",
        (chat_id, sender, body)
    )
    message_id = cursor.lastrowid
    
    conn.commit()
    return message_id

