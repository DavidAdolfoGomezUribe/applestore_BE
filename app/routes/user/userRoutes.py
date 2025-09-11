
from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import timedelta
from typing import List
from schemas.user.userSchemas import (
    UserCreate, UserUpdate, UserResponse, UserPublicResponse, 
    UserLogin, TokenResponse, UserChangePassword
)
from services.user.userService import (
    create_user_db, get_user_by_id_db, get_all_users_db, update_user_db, 
    delete_user_db
)
from auth.auth_utils import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.auth_middleware import get_current_user, get_current_admin_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/register", 
    response_model=UserPublicResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="""
    Registra un nuevo usuario en el sistema.
    
    **Campos requeridos:**
    - **name**: Nombre completo del usuario (mínimo 2 caracteres)
    - **email**: Email válido (debe ser único en el sistema)
    - **password**: Contraseña (mínimo 8 caracteres)
    - **role**: Rol del usuario ('admin' o 'user')
    
    **Respuesta:**
    - Devuelve los datos del usuario creado (sin contraseña)
    - Status 201: Usuario creado exitosamente
    - Status 400: Email ya registrado o datos inválidos
    """,
    responses={
        201: {
            "description": "Usuario registrado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Juan Pérez",
                        "email": "juan@example.com",
                        "role": "user",
                        "register_date": "2025-09-10T15:30:00",
                        "updated_at": "2025-09-10T15:30:00"
                    }
                }
            }
        },
        400: {
            "description": "Error en el registro",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            }
        }
    }
)
def register_user(user: UserCreate):
    """Registra un nuevo usuario en el sistema"""
    user_id = create_user_db(user.name, user.email, user.password, user.role)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    created_user = get_user_by_id_db(user_id)
    return UserPublicResponse(**created_user)

@router.post(
    "/login", 
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="""
    Autentica un usuario y devuelve un token JWT para acceder a rutas protegidas.
    
    **Campos requeridos:**
    - **email**: Email del usuario registrado
    - **password**: Contraseña del usuario
    
    **Respuesta:**
    - Token JWT válido por 60 minutos
    - Información básica del usuario
    - Tipo de token (bearer)
    
    **Uso del token:**
    - Incluir en headers: `Authorization: Bearer <token>`
    - Necesario para rutas protegidas y operaciones de administrador
    """,
    responses={
        200: {
            "description": "Login exitoso",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user": {
                            "id": 1,
                            "name": "Juan Pérez",
                            "email": "juan@example.com",
                            "role": "user"
                        }
                    }
                }
            }
        },
        401: {
            "description": "Credenciales incorrectas",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect email or password"}
                }
            }
        }
    }
)
def login_user(user_credentials: UserLogin):
    """Autentica un usuario y devuelve un token JWT"""
    from services.user.userService import authenticate_user
    user = authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"])}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserPublicResponse(**user)
    }

@router.get(
    "/me", 
    response_model=UserResponse,
    summary="Obtener perfil del usuario autenticado",
    description="""
    Obtiene la información completa del usuario actualmente autenticado.
    
    **Requiere autenticación:**
    - Token JWT válido en header Authorization
    
    **Respuesta:**
    - Información completa del usuario (incluyendo fechas de registro y actualización)
    """,
    responses={
        200: {
            "description": "Información del usuario",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Juan Pérez",
                        "email": "juan@example.com",
                        "role": "user",
                        "register_date": "2025-09-10T15:30:00",
                        "updated_at": "2025-09-10T15:30:00"
                    }
                }
            }
        },
        401: {
            "description": "No autenticado",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            }
        }
    }
)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Obtiene la información del usuario autenticado"""
    return UserResponse(**current_user)


@router.put(
    "/me", 
    response_model=UserResponse,
    summary="Actualizar perfil del usuario autenticado",
    description="""
    Permite al usuario autenticado actualizar su propia información.
    
    **Campos actualizables:**
    - **name**: Nombre del usuario (opcional)
    - **email**: Nuevo email (debe ser único, opcional)
    
    **Restricciones:**
    - No se puede cambiar el rol
    - No se puede cambiar la contraseña (usar endpoint específico)
    - El email debe ser único en el sistema
    """,
    responses={
        200: {
            "description": "Usuario actualizado exitosamente",
        },
        400: {
            "description": "Error en los datos",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already exists"}
                }
            }
        },
        401: {
            "description": "No autenticado"
        }
    }
)
def update_current_user(user_data: UserUpdate, current_user: dict = Depends(get_current_user)):
    """Actualiza la información del usuario autenticado"""
    # No permitir actualizar la contraseña desde este endpoint
    if hasattr(user_data, "password") and user_data.password is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password cannot be updated from this endpoint"
        )
    # Los usuarios normales no pueden cambiar su rol
    if current_user["role"] != "admin" and user_data.role is not None:
        user_data.role = None
    success = update_user_db(current_user["id"], user_data.name, user_data.email)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Could not update user"
        )
    updated_user = get_user_by_id_db(current_user["id"])
    return UserResponse(**updated_user)

@router.put(
    "/me/password",
    summary="Cambiar contraseña del usuario autenticado",
    description="""
    Permite al usuario autenticado cambiar su contraseña.
    
    **Campos requeridos:**
    - **current_password**: Contraseña actual para verificación
    - **new_password**: Nueva contraseña (mínimo 8 caracteres)
    
    **Proceso de seguridad:**
    1. Verifica que la contraseña actual sea correcta
    2. Hashea la nueva contraseña
    3. Actualiza la contraseña en la base de datos
    """,
    responses={
        200: {
            "description": "Contraseña actualizada exitosamente",
            "content": {
                "application/json": {
                    "example": {"message": "Password updated successfully"}
                }
            }
        },
        400: {
            "description": "Contraseña actual incorrecta",
            "content": {
                "application/json": {
                    "example": {"detail": "Current password is incorrect"}
                }
            }
        },
        401: {
            "description": "No autenticado"
        }
    }
)
def change_current_user_password(password_data: UserChangePassword, current_user: dict = Depends(get_current_user)):
    """Cambia la contraseña del usuario autenticado"""
    from services.user.userService import change_password_db
    success = change_password_db(current_user["id"], password_data.current_password, password_data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Current password is incorrect"
        )
    return {"message": "Password updated successfully"}

@router.delete(
    "/me", 
    status_code=status.HTTP_200_OK,
    summary="Eliminar cuenta del usuario autenticado",
    description="""
    Permite al usuario autenticado eliminar su propia cuenta.
    
    **Advertencia:**
    - Esta acción es irreversible
    - Se eliminarán todos los datos asociados al usuario
    - El token JWT actual quedará inválido
    
    **Respuesta:**
    - Status 204: Cuenta eliminada exitosamente (sin contenido)
    - Status 404: Usuario no encontrado
    """,
    responses={
        204: {
            "description": "Cuenta eliminada exitosamente"
        },
        404: {
            "description": "Usuario no encontrado"
        },
        401: {
            "description": "No autenticado"
        }
    }
)
def delete_current_user(current_user: dict = Depends(get_current_user)):
    """Elimina la cuenta del usuario autenticado"""
    success = delete_user_db(current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return {"message": "User deleted successfully"}

# === RUTAS DE ADMINISTRACIÓN ===

@router.get(
    "/", 
    response_model=List[UserResponse],
    summary="Obtener lista de todos los usuarios (Admin)",
    description="""
    Obtiene una lista paginada de todos los usuarios del sistema.
    
    **Requiere permisos de administrador.**
    
    **Parámetros de paginación:**
    - **skip**: Número de usuarios a omitir (para paginación)
    - **limit**: Número máximo de usuarios a devolver (1-1000)
    
    **Respuesta:**
    - Lista de usuarios con toda su información
    - Ordenados por fecha de registro (más recientes primero)
    """,
    responses={
        200: {
            "description": "Lista de usuarios obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "Juan Pérez",
                            "email": "juan@example.com",
                            "role": "user",
                            "register_date": "2025-09-10T15:30:00",
                            "updated_at": "2025-09-10T15:30:00"
                        },
                        {
                            "id": 2,
                            "name": "Admin User",
                            "email": "admin@example.com",
                            "role": "admin",
                            "register_date": "2025-09-09T10:00:00",
                            "updated_at": "2025-09-09T10:00:00"
                        }
                    ]
                }
            }
        },
        401: {
            "description": "No autenticado"
        },
        403: {
            "description": "Sin permisos de administrador"
        }
    }
)
def get_all_users(skip: int = Query(0, ge=0, description="Number of users to skip"), limit: int = Query(100, ge=1, le=1000, description="Number of users to return"), current_admin: dict = Depends(get_current_admin_user)):
    """Obtiene todos los usuarios (solo admins)"""
    users = get_all_users_db(skip, limit)
    return [UserResponse(**user) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, current_admin: dict = Depends(get_current_admin_user)):
    """Obtiene un usuario por ID (solo admins)"""
    user = get_user_by_id_db(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return UserResponse(**user)

@router.put("/{user_id}", response_model=UserResponse)
def update_user_admin(user_id: int, user_data: UserUpdate, current_admin: dict = Depends(get_current_admin_user)):
    """Actualiza un usuario por ID (solo admins)"""
    success = update_user_db(user_id, user_data.name, user_data.email)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found or email already exists"
        )
    updated_user = get_user_by_id_db(user_id)
    return UserResponse(**updated_user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_admin(user_id: int, current_admin: dict = Depends(get_current_admin_user)):
    """Elimina un usuario por ID (solo admins)"""
    success = delete_user_db(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )


