def update_product(conn, product_id, name=None, description=None, price=None, stock=None, image_primary_url=None, image_secondary_url=None, image_tertiary_url=None, release_date=None, is_active=None):
    """
    Update product data with partial updates.
    """
    cursor = conn.cursor(dictionary=True)
    
    # Build dynamic update query
    fields = []
    values = []
    
    if name is not None:
        fields.append("name = %s")
        values.append(name)
    if description is not None:
        fields.append("description = %s")
        values.append(description)
    if price is not None:
        fields.append("price = %s")
        values.append(price)
    if stock is not None:
        fields.append("stock = %s")
        values.append(stock)
    if image_primary_url is not None:
        fields.append("image_primary_url = %s")
        values.append(image_primary_url)
    if image_secondary_url is not None:
        fields.append("image_secondary_url = %s")
        values.append(image_secondary_url)
    if image_tertiary_url is not None:
        fields.append("image_tertiary_url = %s")
        values.append(image_tertiary_url)
    if release_date is not None:
        fields.append("release_date = %s")
        values.append(release_date)
    if is_active is not None:
        fields.append("is_active = %s")
        values.append(is_active)
    
    if not fields:
        return False
    
    values.append(product_id)
    query = f"UPDATE products SET {', '.join(fields)} WHERE id = %s"
    cursor.execute(query, values)
    conn.commit()
    return cursor.rowcount > 0
