from fastapi import APIRouter, HTTPException, status
from app.schemas.chats.chatSchemas import ChatCreateRequest, ChatResponse, MessageRequest, MessageResponse
from app.services.chats.chatService import create_chat_db, get_chat_db, close_chat_db, delete_chat_db, create_message_db, get_messages_by_chat_db

router = APIRouter(
    prefix="/chats",
    tags=["chats"],
)

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat_route(chat: ChatCreateRequest):
    chat_id = create_chat_db(chat.user_id, chat.source)
    if not chat_id:
        raise HTTPException(status_code=500, detail="Error creating chat")
    
    new_chat = get_chat_db(chat_id)
    if not new_chat:
        raise HTTPException(status_code=500, detail="Error retrieving new chat")
    return new_chat

@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat_route(chat_id: int):
    chat = get_chat_db(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.put("/{chat_id}/close", status_code=status.HTTP_204_NO_CONTENT)
def close_chat_route(chat_id: int):
    if not close_chat_db(chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")

@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_route(chat_id: int):
    if not delete_chat_db(chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")

@router.post("/{chat_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message_route(chat_id: int, message: MessageRequest):
    message_id = create_message_db(chat_id, message.sender, message.message)
    if not message_id:
        raise HTTPException(status_code=500, detail="Error creating message")
    
    new_message = get_messages_by_chat_db(chat_id)
    return new_message[-1] if new_message else {"id": message_id, "chat_id": chat_id, **message.dict()}

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
def get_messages_route(chat_id: int):
    messages = get_messages_by_chat_db(chat_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Messages not found for this chat")
    return messages