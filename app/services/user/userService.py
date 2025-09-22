
# Refactor: Usar modelos para acceso a datos y solo lógica de negocio aquí
from typing import Optional, Dict, Any, List
from auth.auth_utils import hash_password, verify_password
from database import get_connection
from models.usuarios import crear_usuario, obtener_usuario_por_id, actualizar_usuario, eliminar_usuario

def create_user_db(name: str, email: str, password: str, role: str = "user") -> Optional[int]:
    """Crea un nuevo usuario con contraseña hasheada usando el modelo"""
    conn = get_connection()
    try:
        hashed_password = hash_password(password)
        user_id = crear_usuario(conn, name, email, hashed_password, role)
        return user_id
    except Exception as e:
        print(f"Error creando usuario: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_user_by_id_db(user_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un usuario por su ID usando el modelo"""
    conn = get_connection()
    try:
        return obtener_usuario_por_id(conn, user_id)
    except Exception as e:
        print(f"Error obteniendo usuario: {e}")
        return None
    finally:
        conn.close()

def update_user_db(user_id: int, name: Optional[str] = None, email: Optional[str] = None) -> bool:
    """Actualiza los datos de un usuario usando el modelo"""
    conn = get_connection()
    try:
        actualizar_usuario(conn, user_id, name, email)
        return True
    except Exception as e:
        print(f"Error actualizando usuario: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_user_db(user_id: int) -> bool:
    """Elimina un usuario usando el modelo"""
    conn = get_connection()
    try:
        eliminar_usuario(conn, user_id)
        return True
    except Exception as e:
        print(f"Error eliminando usuario: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def change_password_db(user_id: int, current_password: str, new_password: str) -> bool:
    """Cambia la contraseña de un usuario"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Verificar la contraseña actual
        user = get_user_by_id_db(user_id)
        if not user or not verify_password(current_password, user["password"]):
            return False
        hashed_password = hash_password(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error cambiando contraseña: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_user_by_email_db(email: str) -> Optional[Dict[str, Any]]:
    """Obtiene un usuario por email (incluye password para autenticación)"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, password, role, register_date, updated_at FROM users WHERE email = %s", 
            (email,)
        )
        return cursor.fetchone()
    finally:
        conn.close()

def get_all_users_db(skip: int = 0, limit: int = 100) -> list:
    """Obtiene todos los usuarios con paginación"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, role, register_date, updated_at FROM users ORDER BY id LIMIT %s OFFSET %s", 
            (limit, skip)
        )
        return cursor.fetchall()
    finally:
        conn.close()

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Autentica un usuario con email y password"""
    user = get_user_by_email_db(email)
    if not user:
        return None
    
    if not verify_password(password, user['password']):
        return None
    
    # Remover password del resultado
    user.pop('password', None)
    return user

def get_users_count_db() -> int:
    """Obtiene el número total de usuarios"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        conn.close()

# Funciones legacy para mantener compatibilidad
def get_user_db(user_id: int):
    """Función legacy - usar get_user_by_id_db en su lugar"""
    return get_user_by_id_db(user_id)