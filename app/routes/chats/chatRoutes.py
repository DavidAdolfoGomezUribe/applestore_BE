from fastapi import APIRouter, HTTPException, Query, Path, status
from typing import List, Optional
from schemas.chats.chatSchemas import (
    ChatCreate, ChatResponse, MessageCreate, MessageResponse, 
    ChatWithMessages, MessageUpdate
)
from services.chats.chatService import (
    create_chat_service, get_chat_service, get_all_chats_service, search_chats_service,
    delete_chat_service, create_message_service,
    get_messages_service, get_chat_with_messages_service, 
    delete_message_service, search_messages_service
)

router = APIRouter(
    prefix="/chats",
    tags=["💬 Chats"],
    responses={404: {"description": "No encontrado"}},
)

# ========== ENDPOINTS DE CHATS ==========

@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="🆕 Crear o obtener chat",
    description="""
    Crea un nuevo chat o retorna uno existente basado en el número de teléfono o email.
    
    - **phone_number**: Número de WhatsApp (opcional)
    - **email**: Email alternativo para chat web (opcional)
    - **user_id**: ID del usuario registrado (opcional)
    
    Si ya existe un chat con ese identificador, lo retorna en lugar de crear uno duplicado.
    """
)
def create_chat(chat: ChatCreate):
    """Crear un nuevo chat o obtener uno existente"""
    try:
        return create_chat_service(chat)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear chat: {str(e)}"
        )

@router.get(
    "/",
    response_model=List[ChatResponse],
    summary="📋 Listar todos los chats",
    description="""
    Obtiene todos los chats ordenados por última actividad.
    
    Parámetros de paginación:
    - **limit**: Máximo número de chats a retornar (default: 50)
    - **offset**: Número de chats a saltar (default: 0)
    """
)

def get_all_chats(
    ):
    """Obtener todos los chats"""
    try:
        return get_all_chats_service()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener chats: {str(e)}"
        )


@router.get(
    "/search",
    response_model=List[ChatResponse],
    summary="🔍 Buscar chats",
    description="""
    Busca chats por número de teléfono o email.
    
    - **q**: Término de búsqueda (número de teléfono o email)
    """
)
def search_chats(
    q: str = Query(..., min_length=1, description="Término de búsqueda")
    ):
    """Buscar chats por número o nombre"""
    try:
        return search_chats_service(q)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar chats: {str(e)}"
        )

@router.get(
    "/{chat_id}",
    response_model=ChatResponse,
    summary="📱 Obtener chat por ID",
    description="Obtiene la información básica de un chat específico."
)
def get_chat(
    chat_id: int = Path(..., gt=0, description="ID del chat")
    ):
    """Obtener un chat específico"""
    try:
        chat = get_chat_service(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat no encontrado"
            )
        return chat
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener chat: {str(e)}"
        )

@router.get(
    "/{chat_id}/full",
    response_model=ChatWithMessages,
    summary="📱💬 Obtener chat completo con mensajes",
    description="""
    Obtiene un chat con todos sus mensajes incluidos.
    
    **Importante**: Este endpoint automáticamente marca el chat como leído.
    """
)
def get_chat_with_messages(
    chat_id: int = Path(..., gt=0, description="ID del chat")
    ):
    """Obtener chat completo con mensajes"""
    try:
        chat = get_chat_with_messages_service(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat no encontrado"
            )
        return chat
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener chat completo: {str(e)}"
        )


@router.delete(
    "/{chat_id}",
    summary="🗑️ Eliminar chat",
    description="Elimina un chat y todos sus mensajes.",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_chat(
    chat_id: int = Path(..., gt=0, description="ID del chat")
    ):
    """Eliminar un chat"""
    try:
        success = delete_chat_service(chat_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat no encontrado"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar chat: {str(e)}"
        )

# ========== ENDPOINTS DE MENSAJES ==========

@router.post(
    "/{chat_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="✉️ Enviar mensaje",
    description="""
    Crea un nuevo mensaje en un chat.
    
    - **sender**: Quien envía (user, bot, system)
    - **body**: Contenido del mensaje
    
    Automáticamente actualiza la actividad del chat y contadores.
    """
)
def create_message(
    message: MessageCreate,
    chat_id: int = Path(..., gt=0, description="ID del chat")
    ):
    """Crear un nuevo mensaje"""
    try:
        # Verificar que el chat_id coincida
        if message.chat_id != chat_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El chat_id del mensaje no coincide con la URL"
            )
        
        return create_message_service(message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear mensaje: {str(e)}"
        )




@router.get(
    "/{chat_id}/messages",
    response_model=List[MessageResponse],
    summary="💬 Obtener mensajes",
    description="""
    Obtiene los mensajes de un chat específico.
    
    Parámetros de paginación:
    - **limit**: Máximo número de mensajes (default: 100)
    - **offset**: Número de mensajes a saltar (default: 0)
    """
)
def get_messages(
    chat_id: int = Path(..., gt=0, description="ID del chat"),
    limit: int = Query(100, ge=1, le=200, description="Límite de mensajes"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
    ):
    """Obtener mensajes de un chat"""
    try:
        return get_messages_service(chat_id, limit, offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener mensajes: {str(e)}"
        )



@router.get(
    "/{chat_id}/messages/search",
    response_model=List[MessageResponse],
    summary="🔍 Buscar mensajes",
    description="Busca mensajes dentro de un chat por contenido."
)
def search_messages(
    chat_id: int = Path(..., gt=0, description="ID del chat"),
    q: str = Query(..., min_length=1, description="Término de búsqueda")
    ):
    """Buscar mensajes en un chat"""
    try:
        return search_messages_service(chat_id, q)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar mensajes: {str(e)}"
        )



@router.delete(
    "/messages/{message_id}",
    summary="🗑️ Eliminar mensaje",
    description="Elimina un mensaje específico.",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_message(
    message_id: int = Path(..., gt=0, description="ID del mensaje")
    ):
    """Eliminar un mensaje"""
    try:
        success = delete_message_service(message_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mensaje no encontrado"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar mensaje: {str(e)}"
        )