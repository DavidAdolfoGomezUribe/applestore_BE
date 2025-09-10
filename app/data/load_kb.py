import os
import json
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

def get_specialized_product_data(conn, product_id, category):
    """Obtiene datos especializados según la categoría del producto"""
    cursor = conn.cursor()
    specialized_data = {}
    
    try:
        if category == 'Iphone':
            cursor.execute("""
                SELECT model, generation, model_type, storage_gb, colors, 
                    display_size, display_technology, chip, cameras, 
                    camera_features, battery_video_hours, water_resistance,
                    connectivity, face_id, touch_id, operating_system
                FROM iphones WHERE id = %s
            """, (product_id,))
            row = cursor.fetchone()
            if row:
                specialized_data = {
                    'model': row[0], 'generation': row[1], 'model_type': row[2],
                    'storage_gb': row[3], 'colors': row[4], 'display_size': row[5],
                    'display_technology': row[6], 'chip': row[7], 'cameras': row[8],
                    'camera_features': row[9], 'battery_hours': row[10], 
                    'water_resistance': row[11], 'connectivity': row[12],
                    'face_id': row[13], 'touch_id': row[14], 'os': row[15]
                }
        
        elif category == 'Mac':
            cursor.execute("""
                SELECT product_line, screen_size, chip, chip_cores, ram_gb, 
                    storage_gb, storage_type, display_technology, ports,
                    keyboard_type, touch_id, webcam, wireless, operating_system,
                    battery_hours, target_audience
                FROM macs WHERE id = %s
            """, (product_id,))
            row = cursor.fetchone()
            if row:
                specialized_data = {
                    'product_line': row[0], 'screen_size': row[1], 'chip': row[2],
                    'chip_cores': row[3], 'ram_gb': row[4], 'storage_gb': row[5],
                    'storage_type': row[6], 'display_tech': row[7], 'ports': row[8],
                    'keyboard': row[9], 'touch_id': row[10], 'webcam': row[11],
                    'wireless': row[12], 'os': row[13], 'battery_hours': row[14],
                    'target': row[15]
                }
        
        elif category == 'Ipad':
            cursor.execute("""
                SELECT product_line, generation, screen_size, display_technology,
                    chip, storage_gb, connectivity_options, cellular_support,
                    cameras, apple_pencil_support, magic_keyboard_support,
                    touch_id, face_id, operating_system, battery_hours
                FROM ipads WHERE id = %s
            """, (product_id,))
            row = cursor.fetchone()
            if row:
                specialized_data = {
                    'product_line': row[0], 'generation': row[1], 'screen_size': row[2],
                    'display_tech': row[3], 'chip': row[4], 'storage_gb': row[5],
                    'connectivity': row[6], 'cellular': row[7], 'cameras': row[8],
                    'apple_pencil': row[9], 'magic_keyboard': row[10],
                    'touch_id': row[11], 'face_id': row[12], 'os': row[13], 'battery_hours': row[14]
                }
        
        elif category == 'Watch':
            cursor.execute("""
                SELECT series, model_type, case_size_mm, case_material,
                    display_technology, chip, connectivity, cellular_support,
                    health_sensors, fitness_features, water_resistance,
                    operating_system, battery_hours, target_audience
                FROM apple_watches WHERE id = %s
            """, (product_id,))
            row = cursor.fetchone()
            if row:
                specialized_data = {
                    'series': row[0], 'model_type': row[1], 'case_size': row[2],
                    'case_material': row[3], 'display_tech': row[4], 'chip': row[5],
                    'connectivity': row[6], 'cellular': row[7], 'health_sensors': row[8],
                    'fitness': row[9], 'water_resistance': row[10], 'os': row[11],
                    'battery_hours': row[12], 'target': row[13]
                }
        
        elif category == 'Accessories':
            cursor.execute("""
                SELECT accessory_type, category, compatibility, wireless_technology,

                    connectivity, battery_hours, noise_cancellation, 
                    water_resistance, special_features, operating_system_req
                FROM accessories WHERE id = %s
            """, (product_id,))
            row = cursor.fetchone()
            if row:
                specialized_data = {
                    'accessory_type': row[0], 'category': row[1], 'compatibility': row[2],
                    'wireless_tech': row[3], 'connectivity': row[4], 'battery_hours': row[5],
                    'noise_cancel': row[6], 'water_resistance': row[7], 
                    'special_features': row[8], 'os_req': row[9]
                }
    
    except Exception as e:
        print(f"Error obteniendo datos especializados para producto {product_id}: {e}")
    
    return specialized_data

def create_comprehensive_text(product, specialized_data):
    """Crea un texto comprehensivo combinando información general y especializada"""
    
    # Información básica del producto
    text_parts = [
        f"Producto: {product[1]}",
        f"Categoría: {product[2]}",
        f"Descripción: {product[3]}",
        f"Precio: ${product[4]:.2f}",
        f"Stock disponible: {product[5]} unidades"
    ]
    
    # Agregar información especializada según la categoría
    if product[2] == 'Iphone' and specialized_data:
        text_parts.extend([
            f"iPhone {specialized_data.get('model', '')} generación {specialized_data.get('generation', '')}",
            f"Tipo: {specialized_data.get('model_type', '')}",
            f"Almacenamiento: {specialized_data.get('storage_gb', '')}GB",
            f"Pantalla: {specialized_data.get('display_size', '')}\" {specialized_data.get('display_technology', '')}",
            f"Chip: {specialized_data.get('chip', '')}",
            f"Cámaras: {specialized_data.get('cameras', '')}",
            f"Batería: {specialized_data.get('battery_hours', '')} horas de video",
            f"Resistencia: {specialized_data.get('water_resistance', '')}",
            f"Conectividad: {specialized_data.get('connectivity', '')}",
            f"Sistema: {specialized_data.get('os', '')}"
        ])
    
    elif product[2] == 'Mac' and specialized_data:
        text_parts.extend([
            f"{specialized_data.get('product_line', '')} de {specialized_data.get('screen_size', '')}\"",
            f"Chip: {specialized_data.get('chip', '')}",
            f"RAM: {specialized_data.get('ram_gb', '')}GB",
            f"Almacenamiento: {specialized_data.get('storage_gb', '')}GB {specialized_data.get('storage_type', '')}",
            f"Pantalla: {specialized_data.get('display_tech', '')}",
            f"Puertos: {specialized_data.get('ports', '')}",
            f"Batería: {specialized_data.get('battery_hours', '')} horas",
            f"Dirigido a: {specialized_data.get('target', '')}"
        ])
    
    elif product[2] == 'Ipad' and specialized_data:
        text_parts.extend([
            f"{specialized_data.get('product_line', '')} generación {specialized_data.get('generation', '')}",
            f"Pantalla: {specialized_data.get('screen_size', '')}\" {specialized_data.get('display_tech', '')}",
            f"Chip: {specialized_data.get('chip', '')}",
            f"Almacenamiento: {specialized_data.get('storage_gb', '')}GB",
            f"Conectividad: {specialized_data.get('connectivity', '')}",
            f"Celular: {'Sí' if specialized_data.get('cellular') else 'No'}",
            f"Apple Pencil: {'Compatible' if specialized_data.get('apple_pencil') else 'No compatible'}",
            f"Magic Keyboard: {'Compatible' if specialized_data.get('magic_keyboard') else 'No compatible'}",
            f"Batería: {specialized_data.get('battery_hours', '')} horas"
        ])
    
    elif product[2] == 'Watch' and specialized_data:
        text_parts.extend([
            f"Apple Watch Series {specialized_data.get('series', '')} {specialized_data.get('model_type', '')}",
            f"Tamaño: {specialized_data.get('case_size', '')}mm",
            f"Material: {specialized_data.get('case_material', '')}",
            f"Pantalla: {specialized_data.get('display_tech', '')}",
            f"Chip: {specialized_data.get('chip', '')}",
            f"Conectividad: {specialized_data.get('connectivity', '')}",
            f"Celular: {'Sí' if specialized_data.get('cellular') else 'No'}",
            f"Sensores de salud: {specialized_data.get('health_sensors', '')}",
            f"Resistencia: {specialized_data.get('water_resistance', '')}",
            f"Batería: {specialized_data.get('battery_hours', '')} horas"
        ])
    
    elif product[2] == 'Accessories' and specialized_data:
        text_parts.extend([
            f"Tipo de accesorio: {specialized_data.get('accessory_type', '')}",
            f"Categoría específica: {specialized_data.get('category', '')}",
            f"Compatibilidad: {specialized_data.get('compatibility', '')}",
            f"Tecnología inalámbrica: {specialized_data.get('wireless_tech', '')}",
            f"Conectividad: {specialized_data.get('connectivity', '')}",
            f"Batería: {specialized_data.get('battery_hours', '')} horas" if specialized_data.get('battery_hours') else "",
            f"Cancelación de ruido: {'Sí' if specialized_data.get('noise_cancel') else 'No'}" if specialized_data.get('noise_cancel') is not None else "",
            f"Características especiales: {specialized_data.get('special_features', '')}"
        ])
    
    # Filtrar partes vacías y unir
    return ". ".join([part for part in text_parts if part and not part.endswith(": ")])

def main():
    # 1. Conectar a MySQL y extraer productos con información completa
    conn = pymysql.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    
    # Obtener todos los productos
    cursor.execute("""
        SELECT id, name, category, description, price, stock, 
            image_primary_url, image_secondary_url, image_tertiary_url,
            release_date, is_active 
        FROM products 
        WHERE is_active = TRUE
    """)
    products = cursor.fetchall()

    
    print(f"Productos encontrados: {len(products)}")
    
    # 2. Procesar cada producto y obtener información especializada
    comprehensive_texts = []
    product_payloads = []
    
    for product in products:
        product_id = product[0]
        category = product[2]
        
        # Obtener datos especializados
        specialized_data = get_specialized_product_data(conn, product_id, category)
        
        # Crear texto comprehensivo
        comprehensive_text = create_comprehensive_text(product, specialized_data)
        comprehensive_texts.append(comprehensive_text)
        
        # Crear payload completo para Qdrant
        payload = {
            'id': product[0],
            'name': product[1],
            'category': product[2],
            'description': product[3],
            'price': float(product[4]),
            'stock': product[5],
            'image_primary': product[6],
            'image_secondary': product[7],
            'image_tertiary': product[8],
            'release_date': str(product[9]) if product[9] else None,
            'is_active': bool(product[10]),
            'specialized_data': specialized_data,
            'comprehensive_text': comprehensive_text
        }
        product_payloads.append(payload)
        
        print(f"Procesado: {product[1]} ({category})")
    
    conn.close()

    # 3. Generar embeddings usando los textos comprehensivos
    embedder = SentenceTransformer(EMBED_MODEL)
    print(f"Generando embeddings para {len(comprehensive_texts)} productos...")
    vectors = embedder.encode(comprehensive_texts, show_progress_bar=True, normalize_embeddings=True)
    print(f"Embeddings generados. Dimensión: {vectors.shape}")

    # 4. Conectar a Qdrant y crear colección si no existe
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

    # 5. Insertar productos como puntos vectoriales con payload completo
    points = []
    for i, (payload, vector) in enumerate(zip(product_payloads, vectors)):
        # Convertir numpy array a lista de Python
        vector_list = vector.tolist() if hasattr(vector, 'tolist') else list(vector)
        points.append(PointStruct(
            id=payload['id'], 
            vector=vector_list, 
            payload=payload
        ))
    
    print(f"Insertando {len(points)} puntos en Qdrant...")
    client.upsert(collection_name=COLLECTION, points=points)
    
    # 6. Verificar que se insertaron correctamente
    collection_info = client.get_collection(COLLECTION)
    print(f"Colección '{COLLECTION}' - Puntos totales: {collection_info.points_count}")
    
    # 7. Mostrar ejemplo de búsqueda
    print("\n=== EJEMPLO DE BÚSQUEDA ===")
    query = "iPhone con cámara profesional"
    query_vector = embedder.encode([query], normalize_embeddings=True)[0]
    
    search_results = client.search(
        collection_name=COLLECTION,
        query_vector=query_vector.tolist(),
        limit=3,
        with_payload=True
    )
    
    print(f"Búsqueda: '{query}'")
    for i, result in enumerate(search_results, 1):
        print(f"{i}. {result.payload['name']} - Score: {result.score:.4f}")
        print(f"   Precio: ${result.payload['price']}")
        print(f"   Stock: {result.payload['stock']}")
    
    print(f"\n✅ Carga completada exitosamente. {len(points)} productos cargados en vectores.")

if __name__ == "__main__":
    main()
