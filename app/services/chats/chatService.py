import os
from dotenv import load_dotenv
from database import get_connection

load_dotenv()

def create_chat_db(user_id: int, source: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chats (user_id, source) VALUES (%s, %s)",
            (user_id, source)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_chat_db(chat_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chats WHERE id = %s", (chat_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def close_chat_db(chat_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE chats SET closed_at=NOW() WHERE id=%s", (chat_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_chat_db(chat_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chats WHERE id=%s", (chat_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def create_message_db(chat_id: int, sender: str, message: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mensajes (chat_id, sender, message) VALUES (%s, %s, %s)",
            (chat_id, sender, message)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_messages_by_chat_db(chat_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mensajes WHERE chat_id = %s ORDER BY created_at ASC", (chat_id,))
        return cursor.fetchall()
    finally:
        conn.close()