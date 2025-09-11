import os
import pymysql
from passlib.context import CryptContext
from dotenv import load_dotenv
import time

# Cargar variables de entorno
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(env_path)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
DB_HOST = os.getenv("MYSQL_HOST", "mysql")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DATABASE", "applestore")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def wait_for_mysql(host, port, user, password, database, retries=10, delay=3):
    for i in range(retries):
        try:
            conn = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            conn.close()
            print("MySQL está listo.")
            return
        except Exception as e:
            print(f"Esperando MySQL... ({i+1}/{retries})")
            time.sleep(delay)
    raise Exception("No se pudo conectar a MySQL después de varios intentos.")

def main():
    wait_for_mysql(DB_HOST, 3306, DB_USER, DB_PASSWORD, DB_NAME)
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cur = conn.cursor()
    # Selecciona usuarios cuyas contraseñas no están hasheadas (no empiezan por $2b$)
    cur.execute("SELECT id, password FROM users WHERE password NOT LIKE '$2b$%';")
    users = cur.fetchall()
    for user_id, plain_password in users:
        hashed = hash_password(plain_password)
        cur.execute("UPDATE users SET password=%s WHERE id=%s;", (hashed, user_id))
        print(f"Usuario {user_id} actualizado.")
    conn.commit()
    cur.close()
    conn.close()
    print("Contraseñas hasheadas correctamente.")

if __name__ == "__main__":
    main()