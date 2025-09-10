from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """Esquema para crear usuario"""
    name: str = Field(..., min_length=3, max_length=100, description="Nombre del usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=6, description="Contraseña del usuario")
    role: Optional[str] = Field(default="user", pattern="^(admin|user)$", description="Rol del usuario")

class UserUpdate(BaseModel):
    """Esquema para actualizar usuario"""
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Nombre del usuario")
    email: Optional[EmailStr] = Field(None, description="Email del usuario")
    role: Optional[str] = Field(None, pattern="^(admin|user)$", description="Rol del usuario")

class UserChangePassword(BaseModel):
    """Esquema para cambiar contraseña"""
    current_password: str = Field(..., min_length=6, description="Contraseña actual")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")

class UserLogin(BaseModel):
    """Esquema para login"""
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=1, description="Contraseña del usuario")

class UserResponse(BaseModel):
    """Esquema para respuesta de usuario"""
    id: int
    name: str
    email: str
    role: str
    register_date: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserPublicResponse(BaseModel):
    """Esquema público de usuario (sin información sensible)"""
    id: int
    name: str
    email: str
    role: str
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Esquema para respuesta de token"""
    access_token: str
    token_type: str
    user: UserPublicResponse

# Esquemas legacy para mantener compatibilidad
class UserRequest(UserCreate):
    """Esquema legacy - usar UserCreate en su lugar"""
    pass