from typing import Optional, Dict, Any, List
from database import get_connection
from auth.auth_utils import hash_password, verify_password
from models.usuarios.createUser import crear_usuario
from models.usuarios.getUser import obtener_usuario_por_id
from models.usuarios.updateUser import actualizar_usuario
from models.usuarios.deleteUser import eliminar_usuario
import pymysql.cursors

# ========== FUNCIONES AUXILIARES ==========

def obtener_usuario_por_email(conn, email: str) -> Optional[Dict[str, Any]]:
    """Obtiene un usuario por su email"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    return cursor.fetchone()

def obtener_todos_los_users(conn) -> List[Dict[str, Any]]:
    """Obtiene todos los users"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

def actualizar_password_usuario(conn, user_id: int, new_password_hash: str) -> bool:
    """Actualiza la contraseña de un usuario"""
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password_hash, user_id))
    return cursor.rowcount > 0

def create_user_service(name: str, email: str, password: str, role: str = "user") -> Optional[int]:
    """
    Crea un nuevo usuario con contraseña hasheada.
    
    Args:
        name: Nombre del usuario
        email: Email del usuario
        password: Contraseña en texto plano
        role: Rol del usuario (default: "user")
    
    Returns:
        ID del usuario creado o None si hay error
    """
    conn = get_connection()
    try:
        hashed_password = hash_password(password)
        return crear_usuario(conn, name, email, hashed_password, role)
    except Exception as e:
        print(f"Error en create_user_service: {e}")
        return None
    finally:
        conn.close()

def get_user_by_email_service(email: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene un usuario por su email.
    
    Args:
        email: Email del usuario
    
    Returns:
        Datos del usuario o None si no existe
    """
    conn = get_connection()
    try:
        return obtener_usuario_por_email(conn, email)
    except Exception as e:
        print(f"Error en get_user_by_email_service: {e}")
        return None
    finally:
        conn.close()

def get_user_by_id_service(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un usuario por su ID.
    
    Args:
        user_id: ID del usuario
    
    Returns:
        Datos del usuario o None si no existe
    """
    conn = get_connection()
    try:
        return obtener_usuario_por_id(conn, user_id)
    except Exception as e:
        print(f"Error en get_user_by_id_service: {e}")
        return None
    finally:
        conn.close()

def get_all_users_service() -> List[Dict[str, Any]]:
    """
    Obtiene todos los users del sistema.
    
    Returns:
        Lista de todos los users
    """
    conn = get_connection()
    try:
        return obtener_todos_los_users(conn)
    except Exception as e:
        print(f"Error en get_all_users_service: {e}")
        return []
    finally:
        conn.close()

def update_user_service(user_id: int, name: str = None, email: str = None, role: str = None) -> bool:
    """
    Actualiza los datos de un usuario.
    
    Args:
        user_id: ID del usuario
        name: Nuevo nombre (opcional)
        email: Nuevo email (opcional)
        role: Nuevo rol (opcional)
    
    Returns:
        True si se actualizó correctamente, False en caso contrario
    """
    conn = get_connection()
    try:
        return actualizar_usuario(conn, user_id, name, email, role)
    except Exception as e:
        print(f"Error en update_user_service: {e}")
        return False
    finally:
        conn.close()

def update_user_password_service(user_id: int, current_password: str, new_password: str) -> bool:
    """
    Actualiza la contraseña de un usuario verificando la contraseña actual.
    
    Args:
        user_id: ID del usuario
        current_password: Contraseña actual en texto plano
        new_password: Nueva contraseña en texto plano
    
    Returns:
        True si se actualizó correctamente, False en caso contrario
    """
    conn = get_connection()
    try:
        # Verificar contraseña actual
        user = obtener_usuario_por_id(conn, user_id)
        if not user:
            return False
        
        if not verify_password(current_password, user['password']):
            return False
        
        # Actualizar con nueva contraseña hasheada
        hashed_new_password = hash_password(new_password)
        return actualizar_password_usuario(conn, user_id, hashed_new_password)
    except Exception as e:
        print(f"Error en update_user_password_service: {e}")
        return False
    finally:
        conn.close()

def admin_update_user_password_service(user_id: int, new_password: str) -> bool:
    """
    Actualiza la contraseña de un usuario (para administradores).
    No requiere verificar la contraseña actual.
    
    Args:
        user_id: ID del usuario
        new_password: Nueva contraseña en texto plano
    
    Returns:
        True si se actualizó correctamente, False en caso contrario
    """
    conn = get_connection()
    try:
        hashed_new_password = hash_password(new_password)
        return actualizar_password_usuario(conn, user_id, hashed_new_password)
    except Exception as e:
        print(f"Error en admin_update_user_password_service: {e}")
        return False
    finally:
        conn.close()

def delete_user_service(user_id: int) -> bool:
    """
    Elimina un usuario del sistema.
    
    Args:
        user_id: ID del usuario
    
    Returns:
        True si se eliminó correctamente, False en caso contrario
    """
    conn = get_connection()
    try:
        return eliminar_usuario(conn, user_id)
    except Exception as e:
        print(f"Error en delete_user_service: {e}")
        return False
    finally:
        conn.close()

def verify_user_credentials_service(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verifica las credenciales de un usuario para login.
    
    Args:
        email: Email del usuario
        password: Contraseña en texto plano
    
    Returns:
        Datos del usuario si las credenciales son válidas, None en caso contrario
    """
    conn = get_connection()
    try:
        user = obtener_usuario_por_email(conn, email)
        if not user:
            return None
        
        if verify_password(password, user['password']):
            return user
        
        return None
    except Exception as e:
        print(f"Error en verify_user_credentials_service: {e}")
        return None
    finally:
        conn.close()

def user_exists_service(email: str) -> bool:
    """
    Verifica si un usuario existe por email.
    
    Args:
        email: Email a verificar
    
    Returns:
        True si el usuario existe, False en caso contrario
    """
    conn = get_connection()
    try:
        user = obtener_usuario_por_email(conn, email)
        return user is not None
    except Exception as e:
        print(f"Error en user_exists_service: {e}")
        return False
    finally:
        conn.close()

# ========== BACKWARDS COMPATIBILITY ==========
# Mantener compatibilidad con el código existente

def create_user_db(name: str, email: str, password: str, role: str = "user") -> Optional[int]:
    """Alias para mantener compatibilidad"""
    return create_user_service(name, email, password, role)

def get_user_by_email_db(email: str) -> Optional[Dict[str, Any]]:
    """Alias para mantener compatibilidad"""
    return get_user_by_email_service(email)

def get_user_by_id_db(user_id: int) -> Optional[Dict[str, Any]]:
    """Alias para mantener compatibilidad"""
    return get_user_by_id_service(user_id)

def get_all_users_db() -> List[Dict[str, Any]]:
    """Alias para mantener compatibilidad"""
    return get_all_users_service()

def update_user_db(user_id: int, name: str = None, email: str = None, role: str = None) -> bool:
    """Alias para mantener compatibilidad"""
    return update_user_service(user_id, name, email, role)

def update_user_password_db(user_id: int, current_password: str, new_password: str) -> bool:
    """Alias para mantener compatibilidad"""
    return update_user_password_service(user_id, current_password, new_password)

def delete_user_db(user_id: int) -> bool:
    """Alias para mantener compatibilidad"""
    return delete_user_service(user_id)
    """Obtiene todos los users"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, role, register_date FROM users")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error obteniendo users: {e}")
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
    except pymysql.IntegrityError:
        return None  # Email ya existe
    finally:
        conn.close()

def get_user_by_id_db(user_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un usuario por ID"""
    conn = get_connection()
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
    """Obtiene todos los users con paginación"""
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

def update_user_db(user_id: int, name: Optional[str] = None, email: Optional[str] = None, role: Optional[str] = None) -> bool:
    """Actualiza un usuario"""
    conn = get_connection()
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
    conn = get_connection()
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
    conn = get_connection()
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
    """Obtiene el número total de users"""
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