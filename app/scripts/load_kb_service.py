
import os
import sys
import time
import pymysql
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(env_path)

DB_HOST = os.getenv("MYSQL_HOST", "mysql")
DB_USER = os.getenv("MYSQL_USER", "applestore_user")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "applestore_password")
DB_NAME = os.getenv("MYSQL_DATABASE", "applestore_db")

# Esperar a que MySQL esté listo y tenga datos
def wait_for_mysql_and_data(retries=30, delay=3):
    for i in range(retries):
        try:
            conn = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=3306
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            conn.close()
            if count > 0:
                print(f"MySQL listo y {count} productos encontrados. Continuando...")
                return
            else:
                print("MySQL listo pero sin productos. Esperando datos...")
        except Exception as e:
            print(f"Esperando MySQL o datos... ({i+1}/{retries}) {e}")
        time.sleep(delay)
    raise Exception("No se pudo conectar a MySQL o no hay datos después de varios intentos.")

# Ajustar sys.path para importar load_kb.py
sys.path.append(os.path.join(os.path.dirname(__file__), '../data/qdrant'))
from load_kb import main as load_kb_main

if __name__ == "__main__":
    wait_for_mysql_and_data()
    load_kb_main()
