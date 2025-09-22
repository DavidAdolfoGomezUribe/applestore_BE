"""
Script para verificar y consultar la base de conocimiento en Qdrant
"""
import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Configuración
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "products_kb")
EMBED_MODEL = os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-small")

def main():
    client = QdrantClient(url=QDRANT_URL)
    
    # 1. Información de la colección
    print("=== INFORMACIÓN DE LA COLECCIÓN ===")
    collection_info = client.get_collection(COLLECTION)
    print(f"Colección: {COLLECTION}")
    print(f"Puntos totales: {collection_info.points_count}")
    print(f"Configuración de vectores: {collection_info.config.params}")
    print()
    
    # 2. Listar algunos puntos
    print("=== PRIMEROS 5 PUNTOS ===")
    points = client.scroll(
        collection_name=COLLECTION,
        limit=5,
        with_payload=True,
        with_vectors=True
    )[0]
    
    for point in points:
        print(f"ID: {point.id}")
        print(f"Payload: {point.payload}")
        print(f"Vector (primeros 5 valores): {point.vector[:5] if point.vector else 'Sin vector'}")
        print(f"Dimensión del vector: {len(point.vector) if point.vector else 0}")
        print("-" * 50)
    
    # 3. Búsqueda semántica de ejemplo
    print("=== BÚSQUEDA SEMÁNTICA ===")
    embedder = SentenceTransformer(EMBED_MODEL)
    query = "iPhone con cámara avanzada"
    query_vector = embedder.encode([query], normalize_embeddings=True)[0]
    
    search_results = client.search(
        collection_name=COLLECTION,
        query_vector=query_vector.tolist(),
        limit=3,
        with_payload=True
    )
    
    print(f"Búsqueda: '{query}'")
    print("Resultados más similares:")
    for i, result in enumerate(search_results, 1):
        print(f"{i}. {result.payload['name']} (Score: {result.score:.4f})")
        print(f"   Descripción: {result.payload['description']}")
        print()

if __name__ == "__main__":
    main()
