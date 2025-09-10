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

def create_user_db(name: str, email: str, password: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_user_db(user_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email FROM usuarios WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def update_user_db(user_id: int, name: str, email: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET name=%s, email=%s WHERE id=%s",
            (name, email, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_user_db(user_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id=%s", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()