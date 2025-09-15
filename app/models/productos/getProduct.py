import pymysql.cursors

def get_product_by_id(conn, product_id):
    """
    Get a product by its ID.
    """
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    return cursor.fetchone()
