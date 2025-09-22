def get_chat_by_id(conn, chat_id):
    """
    Obtiene un chat por su ID.
    
    Args:
        conn: Conexión a la base de datos
        chat_id: ID del chat
    
    Returns:
        dict: Chat encontrado o None
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats WHERE id = %s", (chat_id,))
    return cursor.fetchone()

def get_all_chats(conn):
    """
    Obtiene todos los chats ordenados por última actividad.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        list: Lista de chats
    """
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM chats 
           ORDER BY last_activity DESC"""
    )
    return cursor.fetchall()


def search_chats(conn, search_term):
    """
    Busca chats por número de teléfono o email.
    
    Args:
        conn: Conexión a la base de datos
        search_term: Término de búsqueda
    
    Returns:
        list: Lista de chats que coinciden con la búsqueda
    """
    cursor = conn.cursor()
    search_pattern = f"%{search_term}%"
    cursor.execute(
        """SELECT * FROM chats 
           WHERE phone_number LIKE %s 
           OR email LIKE %s 
           ORDER BY last_activity DESC""",
        (search_pattern, search_pattern)
    )
    return cursor.fetchall()
