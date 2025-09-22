import os
import pymysql
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance

# Configuración por variables de entorno (usa los nombres de servicio de Docker Compose)
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "mysql"),
    "user": os.getenv("MYSQL_USER", "applestore_user"),
    "password": os.getenv("MYSQL_PASSWORD", "applestore_password"),
    "database": os.getenv("MYSQL_DATABASE", "applestore_db")
}
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "products_kb")
VECTOR_SIZE = 384
EMBED_MODEL = os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-small")

def main():
    # 1. Conectar a MySQL y extraer productos
    conn = pymysql.connect(**MYSQL_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()

    # 2. Generar embeddings
    embedder = SentenceTransformer(EMBED_MODEL)
    texts = [f"{row['name']}. {row['description']}" for row in products]
    print(f"Generando embeddings para {len(texts)} productos...")
    vectors = embedder.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    print(f"Embeddings generados. Dimensión: {vectors.shape}")

    # 3. Conectar a Qdrant y crear colección si no existe
    client = QdrantClient(url=QDRANT_URL)
    collections = [c.name for c in client.get_collections().collections]
    print(f"Colecciones existentes en Qdrant: {collections}")

    if COLLECTION not in collections:
        print(f"Creando colección '{COLLECTION}' con dimensión {VECTOR_SIZE}")
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
    else:
        print(f"La colección '{COLLECTION}' ya existe")

    # 4. Verificar si ya hay puntos cargados
    collection_info = client.get_collection(COLLECTION)
    if getattr(collection_info, 'points_count', 0) > 0:
        print(f"La colección '{COLLECTION}' ya tiene {collection_info.points_count} puntos. No se recarga.")
        return

    # Insertar productos como puntos vectoriales
    points = []
    for row, vector in zip(products, vectors):
        # Convertir numpy array a lista de Python
        vector_list = vector.tolist() if hasattr(vector, 'tolist') else list(vector)
        # Qdrant no soporta Decimal ni datetime, convertir a tipos serializables
        def convert(obj):
            import decimal, datetime
            if isinstance(obj, decimal.Decimal):
                return float(obj)
            if isinstance(obj, (datetime.datetime, datetime.date)):
                return obj.isoformat()
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert(i) for i in obj]
            return obj
        payload = convert(row)
        points.append(PointStruct(
            id=row['id'],
            vector=vector_list,
            payload=payload
        ))
    print(f"Insertando {len(points)} puntos en Qdrant...")
    client.upsert(collection_name=COLLECTION, points=points)
    # Verificar que se insertaron correctamente
    collection_info = client.get_collection(COLLECTION)
    print(f"Colección '{COLLECTION}' - Puntos totales: {collection_info.points_count}")
    print(f"Carga completada exitosamente.")

if __name__ == "__main__":
    main()
