import pymysql.cursors

def obtener_producto_por_id(conn, producto_id):
    """
    Obtiene un producto por su ID.
    """
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM products WHERE id = %s", (producto_id,))
    return cursor.fetchone()
