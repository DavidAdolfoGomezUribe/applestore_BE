"""
Endpoint temporal para migrar contraseñas
IMPORTANTE: Este endpoint debe eliminarse en producción
"""

from fastapi import APIRouter, HTTPException
import os
from dotenv import load_dotenv
from auth.auth_utils import hash_password, verify_password
from database import get_connection

load_dotenv()

# Router temporal - ELIMINAR EN PRODUCCIÓN
migration_router = APIRouter(
    prefix="/admin/migrate",
    tags=["migration"],
)

@migration_router.post("/hash-passwords")
def migrate_passwords_endpoint():
    """
    ENDPOINT TEMPORAL: Hashea las contraseñas de los usuarios iniciales
    ⚠️ ELIMINAR EN PRODUCCIÓN
    """
    
    known_passwords = {
        'ana.rodriguez@applestore.com': 'admin123',
        'carlos.mendoza@applestore.com': 'admin456',
        'beatriz.silva@gmail.com': 'user123',
        'david.gonzalez@outlook.com': 'user456'
    }
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        results = []
        updated_count = 0
        
        for email, plain_password in known_passwords.items():
            cursor.execute("SELECT id, email, password FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                current_hash = user['password']
                
                # Verificar si necesita actualización
                needs_update = not current_hash.startswith('$2b$') or len(current_hash) < 50
                
                if needs_update:
                    # Generar nuevo hash
                    new_hash = hash_password(plain_password)
                    
                    # Actualizar en base de datos
                    cursor.execute(
                        "UPDATE users SET password = %s WHERE email = %s",
                        (new_hash, email)
                    )
                    
                    updated_count += 1
                    results.append({
                        "email": email,
                        "status": "updated",
                        "message": "Contraseña hasheada correctamente"
                    })
                else:
                    results.append({
                        "email": email,
                        "status": "already_hashed",
                        "message": "Contraseña ya estaba hasheada"
                    })
            else:
                results.append({
                    "email": email,
                    "status": "not_found",
                    "message": "Usuario no encontrado"
                })
        
        if updated_count > 0:
            conn.commit()
        
        return {
            "message": f"Migración completada. {updated_count} contraseñas actualizadas.",
            "updated_count": updated_count,
            "results": results,
            "credentials": [
                {"email": email, "password": password}
                for email, password in known_passwords.items()
            ]
        }
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error en migración: {str(e)}")
    finally:
        conn.close()

@migration_router.get("/verify-passwords")
def verify_passwords_endpoint():
    """
    ENDPOINT TEMPORAL: Verifica que las contraseñas hasheadas funcionen
    ⚠️ ELIMINAR EN PRODUCCIÓN
    """
    
    known_passwords = {
        'ana.rodriguez@applestore.com': 'admin123',
        'carlos.mendoza@applestore.com': 'admin456',
        'beatriz.silva@gmail.com': 'user123',
        'david.gonzalez@outlook.com': 'user456'
    }
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        results = []
        all_valid = True
        
        for email, plain_password in known_passwords.items():
            cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                is_valid = verify_password(plain_password, user['password'])
                results.append({
                    "email": email,
                    "password": plain_password,
                    "is_valid": is_valid,
                    "status": "valid" if is_valid else "invalid"
                })
                
                if not is_valid:
                    all_valid = False
            else:
                results.append({
                    "email": email,
                    "password": plain_password,
                    "is_valid": False,
                    "status": "user_not_found"
                })
                all_valid = False
        
        return {
            "message": "Verificación completada",
            "all_passwords_valid": all_valid,
            "results": results
        }
        
    finally:
        conn.close()
