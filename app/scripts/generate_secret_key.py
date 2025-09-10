#!/usr/bin/env python3
"""
Script para generar una clave secreta segura para JWT
Uso: python generate_secret_key.py
"""

import secrets
import string

def generate_secret_key(length=32):
    """Genera una clave secreta segura para JWT"""
    return secrets.token_urlsafe(length)

def generate_password(length=12):
    """Genera una contraseña segura"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    print("=== Generador de Claves Seguras ===\n")
    
    print("Clave secreta para JWT:")
    print(f"SECRET_KEY={generate_secret_key()}\n")
    
    print("Contraseñas de ejemplo:")
    for i in range(3):
        print(f"PASSWORD_{i+1}={generate_password()}")
    
    print("\n=== Instrucciones ===")
    print("1. Copia la SECRET_KEY a tu archivo .env")
    print("2. NUNCA compartas esta clave en repositorios públicos")
    print("3. Usa una clave diferente para cada entorno (dev, test, prod)")
