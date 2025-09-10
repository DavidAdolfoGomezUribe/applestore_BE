from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from typing import Dict, Any

from app.schemas.chats.chatSchema import chat_request, chat_response
from app.services.chats.chatService import AppleStoreChatAgent

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

try:
    apple_agent = AppleStoreChatAgent()
except RuntimeError as e:
    # Esto manejará el caso de que el servicio no se pueda inicializar
    # por un error en Qdrant o el LLM al iniciar la aplicación.
    @router.post("/", response_model=chat_response, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    async def chat_endpoint_error_state():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Server is in an unhealthy state, contact support."}
        )

# Si el servicio se inicializa correctamente, se define la rutica
@router.post("/", response_model=chat_response)
async def handle_chat_request(request: chat_request):
    """
    Endpoint para chatear con el bot de asistencia.
    """
    if not request.message or request.message.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "message es requerido"}
        )
    
    try:
        reply = await apple_agent.get_rag_reply(request.message)
        return {"reply": reply}
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "server error"}
        )