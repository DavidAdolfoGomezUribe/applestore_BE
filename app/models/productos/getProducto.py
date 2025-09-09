def obtener_producto_por_id(conn, producto_id):
    """
    Obtiene un producto por su ID.
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos WHERE id = %s", (producto_id,))
    return cursor.fetchone()
