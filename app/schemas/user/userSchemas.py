from pydantic import BaseModel, Field
from typing import Optional

class UserRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., max_length=100, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        orm_mode = True