
from decimal import Decimal
from datetime import datetime, date

def convert_for_qdrant(obj):
    """Recursively convert Decimal to float and datetime/date to ISO string for JSON serialization."""
    if isinstance(obj, dict):
        return {k: convert_for_qdrant(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_for_qdrant(i) for i in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj

import requests
import os
import logging
from sentence_transformers import SentenceTransformer

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "products_kb")

logger = logging.getLogger(__name__)

def add_product(product: dict):
    """
    Agrega un producto a Qdrant como un punto/vector.
    El producto debe contener al menos 'id' y 'name'.
    """
    try:
        # Convert Decimal to float for Qdrant compatibility
        product_clean = convert_for_qdrant(product)
        vector = extract_vector_from_product(product_clean)
        payload = {
            "points": [
                {
                    "id": product_clean["id"],
                    "vector": vector,
                    "payload": product_clean
                }
            ]
        }
        url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points"
        response = requests.put(url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error agregando producto a Qdrant: {e}")
        return None

def update_product(product: dict):
    """
    Actualiza un producto en Qdrant (igual que agregar, sobrescribe si existe).
    """
    return add_product(product)

def delete_product(product_id: int):
    """
    Elimina un producto de Qdrant por su ID.
    """
    try:
        url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points/delete"
        payload = {"points": [product_id]}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error eliminando producto de Qdrant: {e}")
        return None


EMBED_MODEL = os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-small")
VECTOR_SIZE = 384
_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder

def extract_vector_from_product(product: dict):
    """
    Genera el vector de embedding para Qdrant usando name y description.
    """
    name = product.get("name", "")
    description = product.get("description", "")
    text = f"{name}. {description}"
    embedder = get_embedder()
    vector = embedder.encode([text], normalize_embeddings=True)[0]
    return vector.tolist() if hasattr(vector, 'tolist') else list(vector)
