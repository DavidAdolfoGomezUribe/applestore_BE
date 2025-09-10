#!/usr/bin/env python3
"""
Script para generar contraseñas hasheadas correctamente para la base de datos
"""

from passlib.context import CryptContext

# Configuración igual que en auth_utils.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    return pwd_context.hash(password)

if __name__ == "__main__":
    print("=== Generador de Contraseñas Hasheadas ===\n")
    
    passwords = {
        "admin123": "Ana Rodríguez (admin)",
        "admin456": "Carlos Mendoza (admin)", 
        "user123": "Beatriz Silva (user)",
        "user456": "David González (user)"
    }
    
    print("Contraseñas hasheadas con bcrypt:")
    print("="*50)
    
    for password, description in passwords.items():
        hashed = hash_password(password)
        print(f"{description}")
        print(f"Password: {password}")
        print(f"Hash: {hashed}")
        print("-" * 50)
    
    print("\n=== SQL UPDATE STATEMENTS ===")
    print("Copia y ejecuta estos comandos en tu base de datos:\n")
    
    users = [
        ("ana.rodriguez@applestore.com", hash_password("admin123")),
        ("carlos.mendoza@applestore.com", hash_password("admin456")),
        ("beatriz.silva@gmail.com", hash_password("user123")),
        ("david.gonzalez@outlook.com", hash_password("user456"))
    ]
    
    for email, hashed_password in users:
        print(f"UPDATE users SET password = '{hashed_password}' WHERE email = '{email}';")
