from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatCreateRequest(BaseModel):
    user_id: Optional[int] = None
    source: str = Field(..., max_length=50)

class ChatResponse(BaseModel):
    id: int
    user_id: Optional[int]
    source: str
    created_at: datetime
    closed_at: Optional[datetime]
    class Config:
        orm_mode = True

class MessageRequest(BaseModel):
    sender: str = Field(..., max_length=50)
    message: str = Field(..., min_length=1)

class MessageResponse(BaseModel):
    id: int
    chat_id: int
    sender: str
    message: str
    created_at: datetime
    class Config:
        orm_mode = True