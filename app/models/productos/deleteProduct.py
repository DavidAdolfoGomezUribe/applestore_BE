def delete_product(conn, product_id):
    """
    Delete a product by its ID.
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()
    return cursor.rowcount > 0
