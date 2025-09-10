import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        port=int(os.getenv("MYSQL_PORT"))
    )

def create_product_db(category: str, name: str, description: str, price: float, stock: int, image_url: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO productos (category, name, description, price, stock, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
            (category, name, description, price, stock, image_url)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_product_db(product_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE id = %s", (product_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def update_product_db(product_id: int, category: str, name: str, description: str, price: float, stock: int, image_url: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE productos SET category=%s, name=%s, description=%s, price=%s, stock=%s, image_url=%s WHERE id=%s",
            (category, name, description, price, stock, image_url, product_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_product_db(product_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id=%s", (product_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()