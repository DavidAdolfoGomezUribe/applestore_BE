def obtener_chat_por_id(conn, chat_id):
    """
    Obtiene un chat por su ID.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
    
    Returns:
        dict: Chat encontrado o None
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM chats WHERE id = %s", (chat_id,))
    return cursor.fetchone()

def obtener_todos_los_chats(conn, limit=50, offset=0):
    """
    Obtiene todos los chats ordenados por última actividad.
    
    Args:
        conn: Conexión a la base de datos
        limit: Límite de resultados
        offset: Offset para paginación
    
    Returns:
        list: Lista de chats
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT * FROM chats 
           ORDER BY last_activity DESC 
           LIMIT %s OFFSET %s""",
        (limit, offset)
    )
    return cursor.fetchall()

def obtener_chats_con_mensajes_no_leidos(conn):
    """
    Obtiene chats que tienen mensajes no leídos.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        list: Lista de chats con mensajes no leídos
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """SELECT * FROM chats 
           WHERE unread_count > 0 
           ORDER BY last_activity DESC"""
    )
    return cursor.fetchall()

def buscar_chats(conn, search_term):
    """
    Busca chats por número de teléfono o nombre de contacto.
    
    Args:
        conn: Conexión a la base de datos
        search_term: Término de búsqueda
    
    Returns:
        list: Lista de chats que coinciden con la búsqueda
    """
    cursor = conn.cursor(dictionary=True)
    search_pattern = f"%{search_term}%"
    cursor.execute(
        """SELECT * FROM chats 
           WHERE phone_number LIKE %s 
           OR contact_name LIKE %s 
           ORDER BY last_activity DESC""",
        (search_pattern, search_pattern)
    )
    return cursor.fetchall()
