def obtener_mensajes_por_chat(conn, chat_id, limit=100, offset=0):
    """
    Obtiene todos los mensajes de un chat ordenados por fecha.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
        limit: Límite de mensajes (default: 100)
        offset: Offset para paginación
    
    Returns:
        list: Lista de mensajes del chat
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT * FROM messages 
           WHERE chat_id = %s 
           ORDER BY created_at ASC 
           LIMIT %s OFFSET %s""",
        (chat_id, limit, offset)
    )
    return cursor.fetchall()

def obtener_ultimo_mensaje_chat(conn, chat_id):
    """
    Obtiene el último mensaje de un chat.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
    
    Returns:
        dict: Último mensaje o None
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT * FROM messages 
           WHERE chat_id = %s 
           ORDER BY created_at DESC 
           LIMIT 1""",
        (chat_id,)
    )
    return cursor.fetchone()

def contar_mensajes_chat(conn, chat_id):
    """
    Cuenta el total de mensajes en un chat.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
    
    Returns:
        int: Número total de mensajes
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) as total FROM messages WHERE chat_id = %s",
        (chat_id,)
    )
    result = cursor.fetchone()
    return result[0] if result else 0

def obtener_mensajes_por_sender(conn, chat_id, sender):
    """
    Obtiene mensajes de un chat filtrados por sender.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
        sender: Tipo de sender ('user', 'bot', 'system')
    
    Returns:
        list: Lista de mensajes del sender especificado
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT * FROM messages 
           WHERE chat_id = %s AND sender = %s 
           ORDER BY created_at ASC""",
        (chat_id, sender)
    )
    return cursor.fetchall()

def buscar_mensajes_en_chat(conn, chat_id, search_term):
    """
    Busca mensajes dentro de un chat por contenido.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
        search_term: Término a buscar en el contenido
    
    Returns:
        list: Lista de mensajes que contienen el término
    """
    cursor = conn.cursor(dictionary=True)
    search_pattern = f"%{search_term}%"
    cursor.execute(
        """SELECT * FROM messages 
           WHERE chat_id = %s AND body LIKE %s 
           ORDER BY created_at DESC""",
        (chat_id, search_pattern)
    )
    return cursor.fetchall()
