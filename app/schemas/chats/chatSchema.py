from pydantic import BaseModel, Field

class chat_request(BaseModel):
    #Schema para la solicitud de chat
    message: str = Field(..., min_length=1, max_length=1000,
                          examples=["¿Cuál iPhone recomiendas para fotografía?"])

class chat_response(BaseModel):
    #Schema para la respuesta del chat.
    reply: str = Field(..., examples=["Para fotografía, te recomiendo el iPhone 15 Pro Max por su avanzado sistema de cámara..."])
