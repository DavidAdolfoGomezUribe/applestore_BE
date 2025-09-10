"""
Script para verificar y consultar la base de conocimiento en Qdrant
con soporte completo para datos especializados de productos Apple
"""
import os
import json
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Configuración
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "products_kb")
EMBED_MODEL = os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-small")

def print_product_details(payload):
    """Imprime los detalles completos de un producto de forma estructurada"""
    print(f"📱 Producto: {payload.get('name', 'N/A')}")
    print(f"   🏷️  Categoría: {payload.get('category', 'N/A')}")
    print(f"   💰 Precio: ${payload.get('price', 0):.2f}")
    print(f"   📦 Stock: {payload.get('stock', 0)} unidades")
    print(f"   📝 Descripción: {payload.get('description', 'N/A')}")
    
    # Datos especializados
    specialized = payload.get('specialized_data', {})
    if specialized:
        print(f"   🔧 Especificaciones técnicas:")
        category = payload.get('category', '')
        
        if category == 'iPhone':
            if 'chip' in specialized:
                print(f"      • Chip: {specialized['chip']}")
            if 'display_size' in specialized:
                print(f"      • Pantalla: {specialized['display_size']}\" {specialized.get('display_technology', '')}")
            if 'storage_gb' in specialized:
                print(f"      • Almacenamiento: {specialized['storage_gb']}GB")
            if 'cameras' in specialized:
                print(f"      • Cámaras: {specialized['cameras']}")
            if 'water_resistance' in specialized:
                print(f"      • Resistencia: {specialized['water_resistance']}")
        
        elif category == 'Mac':
            if 'chip' in specialized:
                print(f"      • Chip: {specialized['chip']}")
            if 'screen_size' in specialized:
                print(f"      • Pantalla: {specialized['screen_size']}\"")
            if 'ram_gb' in specialized:
                print(f"      • RAM: {specialized['ram_gb']}GB")
            if 'storage_gb' in specialized:
                print(f"      • Almacenamiento: {specialized['storage_gb']}GB {specialized.get('storage_type', '')}")
            if 'battery_hours' in specialized:
                print(f"      • Batería: {specialized['battery_hours']} horas")
        
        elif category == 'iPad':
            if 'chip' in specialized:
                print(f"      • Chip: {specialized['chip']}")
            if 'screen_size' in specialized:
                print(f"      • Pantalla: {specialized['screen_size']}\" {specialized.get('display_tech', '')}")
            if 'apple_pencil' in specialized:
                print(f"      • Apple Pencil: {'Sí' if specialized['apple_pencil'] else 'No'}")
            if 'cellular' in specialized:
                print(f"      • Cellular: {'Sí' if specialized['cellular'] else 'No'}")
        
        elif category == 'Apple Watch':
            if 'series' in specialized:
                print(f"      • Series: {specialized['series']} {specialized.get('model_type', '')}")
            if 'case_size' in specialized:
                print(f"      • Tamaño: {specialized['case_size']}mm")
            if 'health_sensors' in specialized:
                print(f"      • Sensores: {specialized['health_sensors']}")
            if 'battery_hours' in specialized:
                print(f"      • Batería: {specialized['battery_hours']} horas")
        
        elif category == 'Accessories':
            if 'category' in specialized:
                print(f"      • Tipo: {specialized['category']}")
            if 'compatibility' in specialized:
                print(f"      • Compatible con: {specialized['compatibility']}")
            if 'battery_hours' in specialized and specialized['battery_hours']:
                print(f"      • Batería: {specialized['battery_hours']} horas")
    
    # URLs de imágenes
    if payload.get('image_primary'):
        print(f"   🖼️  Imagen principal: {payload['image_primary']}")
    
    print()

def search_products(client, embedder, query, limit=5):
    """Realiza búsqueda semántica de productos"""
    print(f"🔍 Buscando: '{query}'")
    print("=" * 60)
    
    query_vector = embedder.encode([query], normalize_embeddings=True)[0]
    
    search_results = client.search(
        collection_name=COLLECTION,
        query_vector=query_vector.tolist(),
        limit=limit,
        with_payload=True
    )
    
    if not search_results:
        print("❌ No se encontraron resultados")
        return
    
    for i, result in enumerate(search_results, 1):
        print(f"#{i} - Relevancia: {result.score:.4f}")
        print_product_details(result.payload)
        print("-" * 60)

def main():
    client = QdrantClient(url=QDRANT_URL)
    
    # 1. Información de la colección
    print("🔍 INFORMACIÓN DE LA BASE DE CONOCIMIENTO")
    print("=" * 60)
    try:
        collection_info = client.get_collection(COLLECTION)
        print(f"📊 Colección: {COLLECTION}")
        print(f"📈 Puntos totales: {collection_info.points_count}")
        print(f"⚙️  Configuración: {collection_info.config.params}")
        print()
    except Exception as e:
        print(f"❌ Error accediendo a la colección: {e}")
        return
    
    # 2. Estadísticas por categoría
    print("📊 ESTADÍSTICAS POR CATEGORÍA")
    print("=" * 60)
    
    # Obtener todos los puntos para hacer estadísticas
    all_points, _ = client.scroll(
        collection_name=COLLECTION,
        limit=1000,  # Ajustar según el número de productos
        with_payload=True
    )
    
    category_stats = {}
    for point in all_points:
        category = point.payload.get('category', 'Unknown')
        category_stats[category] = category_stats.get(category, 0) + 1
    
    for category, count in category_stats.items():
        print(f"📱 {category}: {count} productos")
    print()
    
    # 3. Ejemplos de productos por categoría
    print("📱 MUESTRA DE PRODUCTOS POR CATEGORÍA")
    print("=" * 60)
    
    for category in ['iPhone', 'Mac', 'iPad', 'Apple Watch', 'Accessories']:
        category_points = [p for p in all_points if p.payload.get('category') == category]
        if category_points:
            print(f"🔹 {category.upper()}:")
            print_product_details(category_points[0].payload)
    
    # 4. Búsquedas semánticas de ejemplo
    embedder = SentenceTransformer(EMBED_MODEL)
    
    print("\n🎯 EJEMPLOS DE BÚSQUEDAS SEMÁNTICAS")
    print("=" * 60)
    
    search_queries = [
        "iPhone con la mejor cámara para fotografía profesional",
        "MacBook portátil para estudiantes",
        "iPad para dibujar y diseño gráfico",
        "Apple Watch para deportes y fitness",
        "auriculares con cancelación de ruido"
    ]
    
    for query in search_queries:
        search_products(client, embedder, query, limit=3)
        print()
    
    # 5. Búsqueda interactiva (opcional)
    print("💬 BÚSQUEDA INTERACTIVA")
    print("=" * 60)
    print("Escribe tu consulta (o 'salir' para terminar):")
    
    while True:
        try:
            user_query = input("\n🔍 Búsqueda: ").strip()
            if user_query.lower() in ['salir', 'exit', 'quit', '']:
                break
            search_products(client, embedder, user_query, limit=3)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error en la búsqueda: {e}")
    
    print("\n👋 ¡Verificación completada!")

if __name__ == "__main__":
    main()
