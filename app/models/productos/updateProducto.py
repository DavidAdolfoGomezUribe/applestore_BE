def actualizar_producto(conn, producto_id, name, description, price, stock, image_url):
    """
    Actualiza los datos de un producto.
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE productos SET name=%s, description=%s, price=%s, stock=%s, image_url=%s WHERE id=%s",
        (name, description, price, stock, image_url, producto_id)
    )
    conn.commit()
