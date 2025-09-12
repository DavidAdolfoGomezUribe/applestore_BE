def update_product(conn, product_id, name, description, price, stock, image_url):
    """
    Update product data.
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET name=%s, description=%s, price=%s, stock=%s, image_primary_url=%s WHERE id=%s",
        (name, description, price, stock, image_url, product_id)
    )
    conn.commit()
