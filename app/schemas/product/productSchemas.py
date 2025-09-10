from pydantic import BaseModel, Field
from typing import Optional

class ProductRequest(BaseModel):
    category: str
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    image_url: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    category: str
    name: str
    description: Optional[str]
    price: float
    stock: int
    image_url: Optional[str]
    class Config:
        orm_mode = True