
def create_chat(conn, phone_number=None, email=None, user_id=None):
    """
    Crea un nuevo chat (conversación) por phone_number o email.
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """INSERT INTO chats (user_id, phone_number, email) 
           VALUES (%s, %s, %s)""",
        (user_id, phone_number, email)
    )
    conn.commit()
    return cursor.lastrowid


def get_or_create_chat(conn, phone_number=None, email=None, user_id=None):
    """
    Busca un chat existente por phone_number o email, si no existe lo crea.
    """
    cursor = conn.cursor(dictionary=True)
    
    # Validar que al menos uno de los identificadores esté presente
    if not phone_number and not email:
        raise ValueError("Debe proporcionar phone_number o email")
    
    # Buscar chat existente
    if phone_number:
        cursor.execute(
            "SELECT * FROM chats WHERE phone_number = %s", 
            (phone_number,)
        )
        existing_chat = cursor.fetchone()
        if existing_chat:
            return existing_chat
    
    if email:
        cursor.execute(
            "SELECT * FROM chats WHERE email = %s", 
            (email,)
        )
        existing_chat = cursor.fetchone()
        if existing_chat:
            return existing_chat
    
    # Si no existe, crear nuevo chat
    chat_id = create_chat(conn, phone_number, email, user_id)
    
    # Obtener el chat recién creado
    cursor.execute("SELECT * FROM chats WHERE id = %s", (chat_id,))
    return cursor.fetchone()

