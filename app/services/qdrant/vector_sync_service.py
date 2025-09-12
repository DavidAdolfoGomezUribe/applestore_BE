import requests
import os
import logging

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "products")

logger = logging.getLogger(__name__)

def add_product(product: dict):
    """
    Agrega un producto a Qdrant como un punto/vector.
    El producto debe contener al menos 'id' y 'name'.
    """
    try:
        vector = extract_vector_from_product(product)
        payload = {
            "points": [
                {
                    "id": product["id"],
                    "vector": vector,
                    "payload": product
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

def extract_vector_from_product(product: dict):
    """
    Extrae o genera el vector del producto. Aquí puedes usar un modelo de embeddings real.
    Por ahora, retorna un vector dummy (debes reemplazarlo por tu lógica real).
    """
    # Ejemplo: vector de ceros de tamaño 10
    return [0.0] * 10
