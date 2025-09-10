"""
Auth module for Apple Store Backend
====================================

Este módulo contiene todas las utilidades de autenticación y autorización
para el sistema de usuarios del Apple Store Backend.

Funcionalidades:
- Hasheo y verificación de contraseñas con bcrypt
- Generación y validación de tokens JWT
- Middleware de autenticación
- Decoradores de autorización por roles
"""

# Importaciones principales para facilitar el uso del módulo
from .auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Nota: Los middleware se importan de forma lazy para evitar circular imports
# from .auth_middleware import (
#     get_current_user,
#     get_current_admin_user,
#     optional_auth,
#     security
# )

# Definir qué se exporta cuando se hace "from app.auth import *"
__all__ = [
    # Utilidades de contraseñas
    'hash_password',
    'verify_password',
    
    # Utilidades JWT
    'create_access_token',
    'verify_token',
    
    # Configuración
    'SECRET_KEY',
    'ALGORITHM',
    'ACCESS_TOKEN_EXPIRE_MINUTES',
    
    # Middleware (importar directamente desde auth_middleware cuando se necesiten)
    # 'get_current_user',
    # 'get_current_admin_user',
    # 'optional_auth',
    # 'security'
]

# Metadatos del módulo
__version__ = "1.0.0"
__author__ = "Apple Store Backend Team"
__description__ = "Authentication and authorization utilities"
