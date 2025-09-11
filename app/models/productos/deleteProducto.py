def eliminar_producto(conn, producto_id):
    """
    Elimina un producto por su ID.
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (producto_id,))
    conn.commit()
