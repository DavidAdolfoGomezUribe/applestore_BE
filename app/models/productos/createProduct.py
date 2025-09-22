def create_product(conn, name, category, description, price, stock, image_primary_url=None, image_secondary_url=None, image_tertiary_url=None, release_date=None, is_active=True):
    """
    Create a new product in the database with all fields.
    """
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO products 
           (name, category, description, price, stock, image_primary_url, image_secondary_url, image_tertiary_url, release_date, is_active) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (name, category, description, price, stock, image_primary_url, image_secondary_url, image_tertiary_url, release_date, is_active)
    )
    conn.commit()
    return cursor.lastrowid
