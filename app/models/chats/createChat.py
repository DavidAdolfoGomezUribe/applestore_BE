def crear_chat(conn, phone_number, user_id=None, contact_name=None):
    """
    Crea un nuevo chat (conversación).
    
    Args:
        conn: Conexión a la base de datos
        phone_number: Número de teléfono (requerido)
        user_id: ID del usuario (opcional)
        contact_name: Nombre del contacto (opcional)
    
    Returns:
        int: ID del chat creado
    """
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO chats (user_id, phone_number, contact_name) 
           VALUES (%s, %s, %s)""",
        (user_id, phone_number, contact_name)
    )
    conn.commit()
    return cursor.lastrowid

def obtener_chat_por_telefono(conn, phone_number):
    """
    Obtiene un chat existente por número de teléfono.
    
    Args:
        conn: Conexión a la base de datos
        phone_number: Número de teléfono
    
    Returns:
        dict: Chat encontrado o None
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM chats WHERE phone_number = %s", (phone_number,))
    return cursor.fetchone()

def obtener_o_crear_chat(conn, phone_number, user_id=None, contact_name=None):
    """
    Obtiene un chat existente o crea uno nuevo si no existe.
    
    Args:
        conn: Conexión a la base de datos
        phone_number: Número de teléfono
        user_id: ID del usuario (opcional)
        contact_name: Nombre del contacto (opcional)
    
    Returns:
        dict: Chat existente o recién creado
    """
    # Buscar chat existente
    chat = obtener_chat_por_telefono(conn, phone_number)
    
    if chat:
        # Si existe, actualizar nombre si se proporciona
        if contact_name and not chat['contact_name']:
            actualizar_nombre_contacto(conn, chat['id'], contact_name)
            chat['contact_name'] = contact_name
        return chat
    else:
        # Si no existe, crear nuevo chat
        chat_id = crear_chat(conn, phone_number, user_id, contact_name)
        return {
            'id': chat_id,
            'user_id': user_id,
            'phone_number': phone_number,
            'contact_name': contact_name,
            'last_message': None,
            'unread_count': 0
        }

def actualizar_nombre_contacto(conn, chat_id, contact_name):
    """
    Actualiza el nombre del contacto de un chat.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
        contact_name: Nuevo nombre del contacto
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE chats SET contact_name = %s WHERE id = %s",
        (contact_name, chat_id)
    )
    conn.commit()
