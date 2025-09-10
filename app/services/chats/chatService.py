import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import models as qdrant_models
from fastembed import TextEmbedding
from langroid.agent.base import AgentConfig
from langroid.agent.chat_agent import ChatAgent
from langroid.language_models.openai_gpt import OpenAIGPT, OpenAIGPTConfig
from langroid.parsing.parser import ParsingConfig, Splitter
from langroid.agent.task import Task
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "company_kb"

class AppleStoreChatAgent:
    """
    Clase para el agente de chat de la tienda Apple que usa RAG.
    """
    def __init__(self):
        try:
            # Inicializar cliente Qdrant y modelo de embedding
            self.qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
            self.embedding_model = TextEmbedding()
            self.collection_name = COLLECTION_NAME
            
            # Inicializar el agente con Langroid
            llm_config = OpenAIGPTConfig()
            agent_config = AgentConfig(llm=llm_config)
            self.agent = ChatAgent(agent_config)

        except Exception as e:
            logger.error(f"Error al inicializar el servicio de chat: {e}")
            raise RuntimeError("Error al inicializar el servicio de chat, el motor de embeddings o LLM no está disponible.")

    async def get_rag_reply(self, message: str) -> str:
        """
        Obtiene una respuesta basada en RAG.
        1. Busca información relevante en Qdrant.
        2. Usa el LLM para generar una respuesta basada en la información recuperada.
        """
        try:
            # Busqueda en Qdrant
            query_embedding = self.embedding_model.embed(message)[0]
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=3
            )
            
            # Construir el contexto para el LLM
            context = "Información relevante de la base de conocimiento:\n"
            for result in search_result:
                payload = result.payload
                text_content = payload.get('text')
                if text_content:
                    context += f"- {text_content}\n"
            
            # Generar la respuesta usando el LLM
            prompt = f"{context}\n\nCon base en la información proporcionada, responde a la siguiente pregunta: {message}"
            
            # Usa Langroid para la generaciónn
            task_config = AgentConfig(llm=OpenAIGPTConfig(), max_tokens=200)
            llm = OpenAIGPT(task_config.llm)
            response = llm.generate(prompt)

            return response
        
        except Exception as e:
            logger.error(f"Error en la lógica RAG: {e}")
            raise RuntimeError("Error interno al procesar la solicitud.")