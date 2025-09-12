def create_product(conn, category, name, description, price, stock, image_url):
    """
    Create a new product in the database.
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (category, name, description, price, stock, image_primary_url) VALUES (%s, %s, %s, %s, %s, %s)",
        (category, name, description, price, stock, image_url)
    )
    conn.commit()
    return cursor.lastrowid
