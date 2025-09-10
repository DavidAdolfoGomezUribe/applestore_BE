from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.security import HTTPBearer
from datetime import timedelta
from typing import List, Optional

from schemas.user.userSchemas import (
    UserCreate, UserUpdate, UserResponse, UserPublicResponse, 
    UserLogin, TokenResponse, UserChangePassword, UserRequest
)
from services.user.userService import (
    create_user_db, get_user_by_id_db, get_all_users_db, update_user_db, 
    delete_user_db, authenticate_user, change_password_db, get_users_count_db
)
from auth.auth_utils import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.auth_middleware import get_current_user, get_current_admin_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

security = HTTPBearer()

@router.post("/register", response_model=UserPublicResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate):
    """Registra un nuevo usuario"""
    user_id = create_user_db(user.name, user.email, user.password, user.role)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    created_user = get_user_by_id_db(user_id)
    return created_user

@router.post("/login", response_model=TokenResponse)
def login_user(user_credentials: UserLogin):
    """Autentica un usuario y devuelve un token JWT"""
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
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Obtiene la información del usuario autenticado"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Actualiza la información del usuario autenticado"""
    # Los usuarios normales no pueden cambiar su rol
    if current_user["role"] != "admin" and user_data.role is not None:
        user_data.role = None
    
    success = update_user_db(
        current_user["id"], 
        user_data.name, 
        user_data.email, 
        user_data.role
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Could not update user"
        )
    
    updated_user = get_user_by_id_db(current_user["id"])
    return updated_user

@router.put("/me/password")
def change_current_user_password(
    password_data: UserChangePassword,
    current_user: dict = Depends(get_current_user)
):
    """Cambia la contraseña del usuario autenticado"""
    success = change_password_db(
        current_user["id"], 
        password_data.current_password, 
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Current password is incorrect"
        )
    
    return {"message": "Password updated successfully"}

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(current_user: dict = Depends(get_current_user)):
    """Elimina la cuenta del usuario autenticado"""
    success = delete_user_db(current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

# === RUTAS DE ADMINISTRACIÓN ===

@router.get("/", response_model=List[UserResponse])
def get_all_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    current_admin: dict = Depends(get_current_admin_user)
):
    """Obtiene todos los usuarios (solo admins)"""
    users = get_all_users_db(skip, limit)
    return users

@router.get("/count")
def get_users_count(current_admin: dict = Depends(get_current_admin_user)):
    """Obtiene el número total de usuarios (solo admins)"""
    count = get_users_count_db()
    return {"count": count}

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_admin(
    user: UserCreate, 
    current_admin: dict = Depends(get_current_admin_user)
):
    """Crea un nuevo usuario (solo admins)"""
    user_id = create_user_db(user.name, user.email, user.password, user.role)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    created_user = get_user_by_id_db(user_id)
    return created_user

@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int, 
    current_admin: dict = Depends(get_current_admin_user)
):
    """Obtiene un usuario por ID (solo admins)"""
    user = get_user_by_id_db(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user_admin(
    user_id: int, 
    user_data: UserUpdate,
    current_admin: dict = Depends(get_current_admin_user)
):
    """Actualiza un usuario por ID (solo admins)"""
    success = update_user_db(user_id, user_data.name, user_data.email, user_data.role)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found or email already exists"
        )
    
    updated_user = get_user_by_id_db(user_id)
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_admin(
    user_id: int, 
    current_admin: dict = Depends(get_current_admin_user)
):
    """Elimina un usuario por ID (solo admins)"""
    success = delete_user_db(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

# === RUTAS LEGACY PARA COMPATIBILIDAD ===

@router.post("/legacy", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_route(user: UserRequest):
    """Ruta legacy para crear usuario - usar /register en su lugar"""
    user_id = create_user_db(user.name, user.email, user.password)
    if not user_id:
        raise HTTPException(status_code=500, detail="Error creating user")
    
    created_user = get_user_by_id_db(user_id)
    return created_user

@router.get("/legacy/{user_id}", response_model=UserResponse)
def get_user_route(user_id: int):
    """Ruta legacy para obtener usuario - usar /{user_id} con autenticación en su lugar"""
    user = get_user_by_id_db(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/legacy/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_user_route(user_id: int, user: UserRequest):
    """Ruta legacy para actualizar usuario - usar /{user_id} con autenticación en su lugar"""
    if not update_user_db(user_id, user.name, user.email):
        raise HTTPException(status_code=404, detail="User not found")

@router.delete("/legacy/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_route(user_id: int):
    """Ruta legacy para eliminar usuario - usar /{user_id} con autenticación en su lugar"""
    if not delete_user_db(user_id):
        raise HTTPException(status_code=404, detail="User not found")