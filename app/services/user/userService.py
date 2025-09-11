from database import get_connection
from auth.auth_utils import hash_password, verify_password
from typing import Optional, Dict, Any

def create_user_db(name: str, email: str, password: str, role: str = "user") -> Optional[int]:
    """Crea un nuevo usuario con contraseña hasheada"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, role)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error creando usuario: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_user_by_email_db(email: str) -> Optional[Dict[str, Any]]:
    """Obtiene un usuario por su email"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error obteniendo usuario: {e}")
        return None
    finally:
        conn.close()

def get_user_by_id_db(user_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un usuario por su ID"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error obteniendo usuario: {e}")
        return None
    finally:
        conn.close()

def get_all_users_db() -> list:
    """Obtiene todos los usuarios"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, role, register_date FROM users")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
        return []
    finally:
        conn.close()

def authenticate_user_db(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Autentica un usuario verificando email y contraseña"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user and verify_password(password, user['password']):
            # No devolver la contraseña en la respuesta
            user_response = {k: v for k, v in user.items() if k != 'password'}
            return user_response
        return None
    except Exception as e:
        print(f"Error autenticando usuario: {e}")
        return None
    finally:
        conn.close()

def update_user_db(user_id: int, name: str = None, email: str = None, role: str = None) -> bool:
    """Actualiza los datos de un usuario"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Construir la consulta dinámicamente
        update_fields = []
        params = []
        
        if name is not None:
            update_fields.append("name = %s")
            params.append(name)
        if email is not None:
            update_fields.append("email = %s")
            params.append(email)
        if role is not None:
            update_fields.append("role = %s")
            params.append(role)
        
        if not update_fields:
            return True  # No hay nada que actualizar
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        params.append(user_id)
        
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error actualizando usuario: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def change_password_db(user_id: int, new_password: str) -> bool:
    """Cambia la contraseña de un usuario"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
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

def delete_user_db(user_id: int) -> bool:
    """Elimina un usuario"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error eliminando usuario: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    """Crea un nuevo usuario con contraseña hasheada"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, role)
        )
        conn.commit()
        return cursor.lastrowid
    except pymysql.IntegrityError:
        return None  # Email ya existe
    finally:
        conn.close()

def get_user_by_id_db(user_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un usuario por ID"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, role, register_date, updated_at FROM users WHERE id = %s", 
            (user_id,)
        )
        return cursor.fetchone()
    finally:
        conn.close()

def get_user_by_email_db(email: str) -> Optional[Dict[str, Any]]:
    """Obtiene un usuario por email (incluye password para autenticación)"""
    conn = get_db_connection()
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
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, email, role, register_date, updated_at FROM users ORDER BY id LIMIT %s OFFSET %s", 
            (limit, skip)
        )
        return cursor.fetchall()
    finally:
        conn.close()

def update_user_db(user_id: int, name: Optional[str] = None, email: Optional[str] = None, role: Optional[str] = None) -> bool:
    """Actualiza un usuario"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        updates = []
        values = []
        
        if name is not None:
            updates.append("name = %s")
            values.append(name)
        if email is not None:
            updates.append("email = %s")
            values.append(email)
        if role is not None:
            updates.append("role = %s")
            values.append(role)
        
        if not updates:
            return False
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        
        cursor.execute(query, values)
        conn.commit()
        return cursor.rowcount > 0
    except pymysql.IntegrityError:
        return False  # Email ya existe
    finally:
        conn.close()

def change_password_db(user_id: int, current_password: str, new_password: str) -> bool:
    """Cambia la contraseña de un usuario"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Verificar contraseña actual
        cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user or not verify_password(current_password, user['password']):
            return False
        
        # Actualizar contraseña
        hashed_new_password = hash_password(new_password)
        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s",
            (hashed_new_password, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def delete_user_db(user_id: int) -> bool:
    """Elimina un usuario"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
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
    conn = get_db_connection()
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