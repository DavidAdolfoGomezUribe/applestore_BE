def crear_producto(conn, category, name, description, price, stock, image_url):
    """
    Crea un nuevo producto en la base de datos.
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (category, name, description, price, stock, image_primary_url) VALUES (%s, %s, %s, %s, %s, %s)",
        (category, name, description, price, stock, image_url)
    )
    conn.commit()
    return cursor.lastrowid
