from typing import Optional, Dict, Any, List, Tuple
from database import get_connection
from schemas.product.productSchemas import (
    ProductCreate, ProductUpdate, ProductFilters, 
    ProductCompleteCreate, CategoryEnum,
    iPhoneSpecCreate, MacSpecCreate, iPadSpecCreate, 
    AppleWatchSpecCreate, AccessorySpecCreate
)
from models.productos.createProduct import create_product
from models.productos.getProduct import get_product_by_id
from models.productos.updateProduct import update_product
from models.productos.deleteProduct import delete_product
from models.productos.createSpecs import (
    create_iphone_spec, create_mac_spec, create_ipad_spec, create_apple_watch_spec, create_accessory_spec
)
from services.qdrant.vector_sync_service import add_product, update_product, delete_product, extract_vector_from_product

import json
import logging
from datetime import datetime
import pymysql.cursors

logger = logging.getLogger(__name__)


def get_all_products(conn, limit: int = 50, offset: int = 0, active_only: bool = True) -> List[Dict[str, Any]]:
    """Obtiene todos los productos con paginación"""
    cursor = conn.cursor()
    if active_only:
        cursor.execute(
            "SELECT * FROM products WHERE is_active = 1 ORDER BY created_at DESC LIMIT %s OFFSET %s", 
            (limit, offset)
        )
    else:
        cursor.execute(
            "SELECT * FROM products ORDER BY created_at DESC LIMIT %s OFFSET %s", 
            (limit, offset)
        )
    return cursor.fetchall()

def search_products_db(conn, search_term: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Search products by name or description with pagination"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM products WHERE (name LIKE %s OR description LIKE %s) AND is_active = 1 ORDER BY created_at DESC LIMIT %s OFFSET %s",
        (f"%{search_term}%", f"%{search_term}%", limit, offset)
    )
    return cursor.fetchall()

def get_products_by_category_db(conn, category: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Get products by category with pagination"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM products WHERE category = %s AND is_active = 1 ORDER BY created_at DESC LIMIT %s OFFSET %s", 
        (category, limit, offset)
    )
    return cursor.fetchall()

def update_product_partial_db(conn, product_id: int, update_data: dict) -> bool:
    """Update a product with partial fields"""
    if not update_data:
        return True
    fields = []
    values = []
    for field, value in update_data.items():
        if field == 'image_url':
            field = 'image_primary_url'
        fields.append(f"{field} = %s")
        values.append(value)
    values.append(product_id)
    cursor = conn.cursor()
    query = f"UPDATE products SET {', '.join(fields)} WHERE id = %s"
    cursor.execute(query, values)
    conn.commit()
    return cursor.rowcount > 0

def update_product_stock_db(conn, product_id: int, new_stock: int) -> bool:
    """Update the stock of a product"""
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock = %s WHERE id = %s", (new_stock, product_id))
    conn.commit()
    return cursor.rowcount > 0

def format_json_field(data: Any) -> str:
    """Convierte datos a JSON string para MySQL"""
    if data is None:
        return None
    if isinstance(data, (list, dict)):
        return json.dumps(data)
    return str(data)

def parse_json_field(data: str) -> Any:
    """Parsea JSON string de MySQL"""
    if data is None:
        return None
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return data

def create_complete_product_service(product_data: ProductCompleteCreate) -> Optional[int]:
    """
    Crea un producto completo con especificaciones usando el modelo.
    
    Args:
        product_data: Datos completos del producto
    
    Returns:
        ID del producto creado o None si hay error
    """
    conn = get_connection()
    try:
        # Crear producto en DB
        p = product_data.product
        product_id = create_product(
            conn,
            p.name,
            p.category.value,
            p.description,
            p.price,
            p.stock,
            p.image_primary_url,
            p.image_secondary_url,
            p.image_tertiary_url,
            p.release_date,
            p.is_active
        )
        # Insertar en tabla de especificaciones si corresponde
        if product_id:
            # iPhone
            if product_data.iphone_spec is not None:
                create_iphone_spec(conn, product_id, product_data.iphone_spec)
            # Mac
            if product_data.mac_spec is not None:
                create_mac_spec(conn, product_id, product_data.mac_spec)
            # iPad
            if product_data.ipad_spec is not None:
                create_ipad_spec(conn, product_id, product_data.ipad_spec)
            # Apple Watch
            if product_data.apple_watch_spec is not None:
                create_apple_watch_spec(conn, product_id, product_data.apple_watch_spec)
            # Accessory
            if product_data.accessory_spec is not None:
                create_accessory_spec(conn, product_id, product_data.accessory_spec)
            # Obtener producto creado y sincronizar con Qdrant
            product = get_product_by_id(conn, product_id)
            if product:
                add_product(product)
        return product_id
    except Exception as e:
        logger.error(f"Error in create_complete_product_service: {e}")
        return None
    finally:
        conn.close()

def get_product_by_id_service(product_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un producto por ID usando el modelo.
    
    Args:
        product_id: ID del producto
    
    Returns:
        Datos del producto o None si no existe
    """
    conn = get_connection()
    try:
        product = get_product_by_id(conn, product_id)
        if product:
            # Parsear campos JSON
            for field in ['storage_options', 'colors', 'chip_cores', 'ram_gb', 'storage_options',
                         'display_features', 'ports', 'cameras', 'camera_features', 'connectivity',
                         'wireless', 'audio_features', 'box_contents']:
                if field in product and product[field]:
                    product[field] = parse_json_field(product[field])
        return product
    except Exception as e:
        logger.error(f"Error en get_product_by_id_service: {e}")
        return None
    finally:
        conn.close()

def get_all_products_service(limit: int = 50, offset: int = 0, active_only: bool = True) -> List[Dict[str, Any]]:
    """
    Obtiene todos los productos con paginación.
    
    Args:
        limit: Límite de productos
        offset: Offset para paginación
        active_only: Solo productos activos
    
    Returns:
        Lista de productos
    """
    conn = get_connection()
    try:
        products = get_all_products(conn, limit, offset, active_only)
        # Parsear campos JSON para cada producto
        for product in products:
            for field in ['storage_options', 'colors', 'chip_cores', 'ram_gb', 'storage_options',
                         'display_features', 'ports', 'cameras', 'camera_features', 'connectivity',
                         'wireless', 'audio_features', 'box_contents']:
                if field in product and product[field]:
                    product[field] = parse_json_field(product[field])
        return products
    except Exception as e:
        logger.error(f"Error en get_all_products_service: {e}")
        return []
    finally:
        conn.close()

def get_products_by_category_service(category: str, limit: int = 50, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
    """
    Obtiene productos por categoría.
    
    Args:
        category: Categoría del producto
        limit: Límite de productos
        offset: Offset para paginación
    
    Returns:
        Tupla de (lista de productos, total)
    """
    conn = get_connection()
    try:
        products = get_products_by_category_db(conn, category, limit, offset)
        # Get total count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM products WHERE category = %s AND is_active = 1", (category,))
        total = cursor.fetchone()['total']
        
        # Parse JSON fields for each product
        for product in products:
            for field in ['storage_options', 'colors', 'chip_cores', 'ram_gb', 'storage_options',
                         'display_features', 'ports', 'cameras', 'camera_features', 'connectivity',
                         'wireless', 'audio_features', 'box_contents']:
                if field in product and product[field]:
                    product[field] = parse_json_field(product[field])
        return products, total
    except Exception as e:
        logger.error(f"Error in get_products_by_category_service: {e}")
        return [], 0
    finally:
        conn.close()

def search_products_service(search_term: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Busca productos por término.
    
    Args:
        search_term: Término de búsqueda
        limit: Límite de productos
        offset: Offset para paginación
    
    Returns:
        Lista de productos que coinciden
    """
    conn = get_connection()
    try:
        all_products = search_products_db(conn, search_term)
        total = len(all_products)
        products = all_products[offset:offset+limit]
        for product in products:
            for field in ['storage_options', 'colors', 'chip_cores', 'ram_gb', 'storage_options',
                        'display_features', 'ports', 'cameras', 'camera_features', 'connectivity',
                        'wireless', 'audio_features', 'box_contents']:
                if field in product and product[field]:
                    product[field] = parse_json_field(product[field])
        return products, total
    except Exception as e:
        logger.error(f"Error in search_products_service: {e}")
        return [], 0
    finally:
        conn.close()

def update_product_service(product_id: int, product_data: ProductUpdate) -> bool:
    """
    Actualiza un producto usando el modelo.
    
    Args:
        product_id: ID del producto
        product_data: Nuevos datos del producto
    
    Returns:
        True si se actualizó correctamente
    """
    conn = get_connection()
    try:
        # Convertir datos a diccionario, excluyendo campos None
        update_data = {k: v for k, v in product_data.dict().items() if v is not None}
        # Convertir enums a string
        if 'category' in update_data:
            update_data['category'] = update_data['category'].value
        success = update_product_partial_db(conn, product_id, update_data)
        if success:
            product = get_product_by_id(conn, product_id)
            if product:
                update_product(product)
        return success
    except Exception as e:
        logger.error(f"Error in update_product_service: {e}")
        return False
    finally:
        conn.close()

def update_product_stock_service(product_id: int, new_stock: int) -> bool:
    """
    Actualiza el stock de un producto.
    
    Args:
        product_id: ID del producto
        new_stock: Nuevo stock
    
    Returns:
        True si se actualizó correctamente
    """
    conn = get_connection()
    try:
        success = update_product_stock_db(conn, product_id, new_stock)
        if success:
            product = get_product_by_id(conn, product_id)
            if product:
                update_product(product)
        return success
    except Exception as e:
        logger.error(f"Error in update_product_stock_service: {e}")
        return False
    finally:
        conn.close()

def delete_product_service(product_id: int, soft_delete: bool = True) -> bool:
    """
    Elimina un producto (soft o hard delete).
    
    Args:
        product_id: ID del producto
        soft_delete: Si es True, desactiva. Si es False, elimina completamente
    
    Returns:
        True si se eliminó correctamente
    """
    conn = get_connection()
    try:
        if soft_delete:
            return deactivate_product_db(conn, product_id)
        else:
            # Get product before deleting for Qdrant sync
            product = get_product_by_id(conn, product_id)
            db_deleted = delete_product(conn, product_id)
            if db_deleted and product:
                delete_product_qdrant = delete_product(product_id)
            return db_deleted
    except Exception as e:
        logger.error(f"Error en delete_product_service: {e}")
        return False
    finally:
        conn.close()

def get_filtered_products_service(filters: ProductFilters, page: int = 1, page_size: int = 20) -> Tuple[List[Dict[str, Any]], int]:
    """
    Obtiene productos con filtros aplicados.
    
    Args:
        filters: Filtros a aplicar
        page: Número de página (default: 1)
        page_size: Tamaño de página (default: 20)
    
    Returns:
        Tupla con (productos, total_count)
    """
    conn = get_connection()
    try:
        # Construir consulta con filtros
        conditions = []
        params = []
        
        if filters.category:
            conditions.append("p.category = %s")
            params.append(filters.category.value)
        
        if filters.min_price:
            conditions.append("p.price >= %s")
            params.append(filters.min_price)
        
        if filters.max_price:
            conditions.append("p.price <= %s")
            params.append(filters.max_price)
        
        if filters.in_stock:
            conditions.append("p.stock > 0")
        
        if filters.search:
            conditions.append("(p.name LIKE %s OR p.description LIKE %s)")
            search_term = f"%{filters.search}%"
            params.extend([search_term, search_term])
        
        # Calcular offset para paginación
        offset = (page - 1) * page_size
        
        # Usar función de búsqueda si hay término de búsqueda
        if filters.search:
            products = search_products_db(conn, filters.search)
        elif filters.category:
            products = get_products_by_category_db(conn, filters.category.value)
        else:
            products = get_all_products(conn)
        
        # Aplicar filtros adicionales
        filtered_products = []
        for product in products:
            # Filtro por precio mínimo
            if filters.min_price and product['price'] < filters.min_price:
                continue
            # Filtro por precio máximo  
            if filters.max_price and product['price'] > filters.max_price:
                continue
            # Filtro por stock
            if filters.in_stock and product['stock'] <= 0:
                continue
            # Filtro por activo
            if filters.is_active is not None and product['is_active'] != filters.is_active:
                continue
            filtered_products.append(product)
        
        # Obtener conteo total después de filtros
        total_count = len(filtered_products)
        
        # Aplicar paginación
        paginated_products = filtered_products[offset:offset + page_size]
        
        # Parsear campos JSON
        for product in paginated_products:
            for field in ['storage_options', 'colors', 'chip_cores', 'ram_gb', 'storage_options',
                         'display_features', 'ports', 'cameras', 'camera_features', 'connectivity',
                         'wireless', 'audio_features', 'box_contents']:
                if field in product and product[field]:
                    product[field] = parse_json_field(product[field])
        
        return paginated_products, total_count
    except Exception as e:
        logger.error(f"Error en get_filtered_products_service: {e}")
        return [], 0
    finally:
        conn.close()
