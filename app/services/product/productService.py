from typing import Optional, Dict, Any, List, Tuple
from database import get_connection
from schemas.product.productSchemas import (
    ProductCreate, ProductUpdate, ProductFilters, 
    ProductCompleteCreate, CategoryEnum,
    iPhoneSpecCreate, MacSpecCreate, iPadSpecCreate, 
    AppleWatchSpecCreate, AccessorySpecCreate
)
from models.productos.createProducto import crear_producto
from models.productos.getProducto import obtener_producto_por_id
from models.productos.updateProducto import actualizar_producto
from models.productos.deleteProducto import eliminar_producto
import json
import logging
from datetime import datetime
import pymysql.cursors

logger = logging.getLogger(__name__)

# ========== FUNCIONES AUXILIARES ==========

def obtener_todos_los_productos(conn) -> List[Dict[str, Any]]:
    """Obtiene todos los productos"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
    return cursor.fetchall()

def buscar_productos(conn, search_term: str) -> List[Dict[str, Any]]:
    """Busca productos por nombre o descripción"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM products WHERE name LIKE %s OR description LIKE %s",
        (f"%{search_term}%", f"%{search_term}%")
    )
    return cursor.fetchall()

def obtener_productos_por_categoria(conn, category: str) -> List[Dict[str, Any]]:
    """Obtiene productos por categoría"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM products WHERE category = %s", (category,))
    return cursor.fetchall()

def contar_productos_total(conn) -> int:
    """Cuenta el total de productos"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT COUNT(*) as total FROM products")
    return cursor.fetchone()['total']

def actualizar_producto_parcial(conn, producto_id: int, update_data: dict) -> bool:
    """Actualiza un producto con campos parciales"""
    if not update_data:
        return True
        
    # Construir query dinámicamente
    fields = []
    values = []
    
    for field, value in update_data.items():
        if field == 'image_url':
            field = 'image_primary_url'
        fields.append(f"{field} = %s")
        values.append(value)
    
    values.append(producto_id)
    
    cursor = conn.cursor()
    query = f"UPDATE products SET {', '.join(fields)} WHERE id = %s"
    cursor.execute(query, values)
    conn.commit()
    return cursor.rowcount > 0
    """Actualiza el stock de un producto"""
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock = %s WHERE id = %s", (new_stock, producto_id))
    return cursor.rowcount > 0

def actualizar_stock_producto(conn, producto_id: int, new_stock: int) -> bool:
    """Actualiza el stock de un producto"""
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock = %s WHERE id = %s", (new_stock, producto_id))
    conn.commit()
    return cursor.rowcount > 0

def desactivar_producto(conn, producto_id: int) -> bool:
    """Desactiva un producto (soft delete)"""
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET is_active = FALSE WHERE id = %s", (producto_id,))
    conn.commit()
    return cursor.rowcount > 0

def crear_producto_basico(conn, product_data: ProductCreate) -> Optional[int]:
    """Crea un producto básico usando el modelo existente"""
    return crear_producto(
        conn, 
        product_data.category.value,
        product_data.name,
        product_data.description,
        product_data.price,
        product_data.stock,
        product_data.image_primary_url or ""
    )

def crear_producto_completo(conn, product_data: ProductCompleteCreate) -> Optional[int]:
    """Crea un producto completo - implementación básica"""
    return crear_producto_basico(conn, product_data.product)

# ========== FUNCIONES HELPER ==========
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

# ========== SERVICIOS DE PRODUCTO ==========

def create_product_service(product_data: ProductCreate) -> Optional[int]:
    """
    Crea un producto básico usando el modelo.
    
    Args:
        product_data: Datos del producto
    
    Returns:
        ID del producto creado o None si hay error
    """
    conn = get_connection()
    try:
        return crear_producto_basico(conn, product_data)
    except Exception as e:
        logger.error(f"Error en create_product_service: {e}")
        return None
    finally:
        conn.close()

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
        # Convertir especificaciones a diccionario
        specs_dict = None
        if product_data.specifications:
            specs_dict = product_data.specifications.dict()
        
        return crear_producto_completo(
            conn=conn,
            name=product_data.name,
            category=product_data.category.value,
            description=product_data.description,
            price=product_data.price,
            stock=product_data.stock,
            image_primary_url=product_data.image_primary_url,
            image_secondary_url=product_data.image_secondary_url,
            image_tertiary_url=product_data.image_tertiary_url,
            release_date=product_data.release_date,
            is_active=product_data.is_active,
            specifications=specs_dict
        )
    except Exception as e:
        logger.error(f"Error en create_complete_product_service: {e}")
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
        product = obtener_producto_por_id(conn, product_id)
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
        products = obtener_todos_los_productos(conn, limit, offset, active_only)
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

def get_products_by_category_service(category: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Obtiene productos por categoría.
    
    Args:
        category: Categoría del producto
        limit: Límite de productos
        offset: Offset para paginación
    
    Returns:
        Lista de productos de la categoría
    """
    conn = get_connection()
    try:
        products = obtener_productos_por_categoria(conn, category, limit, offset)
        # Parsear campos JSON para cada producto
        for product in products:
            for field in ['storage_options', 'colors', 'chip_cores', 'ram_gb', 'storage_options',
                        'display_features', 'ports', 'cameras', 'camera_features', 'connectivity',
                        'wireless', 'audio_features', 'box_contents']:
                if field in product and product[field]:
                    product[field] = parse_json_field(product[field])
        return products
    except Exception as e:
        logger.error(f"Error en get_products_by_category_service: {e}")
        return []
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
        products = buscar_productos(conn, search_term, limit, offset)
        # Parsear campos JSON para cada producto
        for product in products:
            for field in ['storage_options', 'colors', 'chip_cores', 'ram_gb', 'storage_options',
                        'display_features', 'ports', 'cameras', 'camera_features', 'connectivity',
                        'wireless', 'audio_features', 'box_contents']:
                if field in product and product[field]:
                    product[field] = parse_json_field(product[field])
        return products
    except Exception as e:
        logger.error(f"Error en search_products_service: {e}")
        return []
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
        
        return actualizar_producto_parcial(conn, product_id, update_data)
    except Exception as e:
        logger.error(f"Error en update_product_service: {e}")
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
        return actualizar_stock_producto(conn, product_id, new_stock)
    except Exception as e:
        logger.error(f"Error en update_product_stock_service: {e}")
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
            return desactivar_producto(conn, product_id)
        else:
            return eliminar_producto(conn, product_id)
    except Exception as e:
        logger.error(f"Error en delete_product_service: {e}")
        return False
    finally:
        conn.close()

def get_products_count_service() -> int:
    """
    Obtiene el total de productos activos.
    
    Returns:
        Número total de productos
    """
    conn = get_connection()
    try:
        return contar_productos_total(conn)
    except Exception as e:
        logger.error(f"Error en get_products_count_service: {e}")
        return 0
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
            products = buscar_productos(conn, filters.search)
        elif filters.category:
            products = obtener_productos_por_categoria(conn, filters.category.value)
        else:
            products = obtener_todos_los_productos(conn)
        
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

# ========== BACKWARDS COMPATIBILITY ==========
# Mantener compatibilidad con el código existente

def create_product_db(product_data: ProductCreate) -> Optional[int]:
    """Alias para mantener compatibilidad"""
    return create_product_service(product_data)

def get_product_by_id_db(product_id: int) -> Optional[Dict[str, Any]]:
    """Alias para mantener compatibilidad"""
    return get_product_by_id_service(product_id)

def get_all_products_db(limit: int = 50, offset: int = 0, active_only: bool = True) -> List[Dict[str, Any]]:
    """Alias para mantener compatibilidad"""
    return get_all_products_service(limit, offset, active_only)

def update_product_db(product_id: int, product_data: ProductUpdate) -> bool:
    """Alias para mantener compatibilidad"""
    return update_product_service(product_id, product_data)

def delete_product_db(product_id: int, soft_delete: bool = True) -> bool:
    """Alias para mantener compatibilidad"""
    return delete_product_service(product_id, soft_delete)

# ========== ALIASES PARA COMPATIBILIDAD CON RUTAS ==========

def create_product_db(product_data: ProductCreate) -> Optional[int]:
    """Alias para mantener compatibilidad"""
    return create_product_service(product_data)

def get_product_by_id_db(product_id: int) -> Optional[Dict[str, Any]]:
    """Alias para mantener compatibilidad"""
    return get_product_by_id_service(product_id)

def get_products_list_db(filters: ProductFilters, page: int = 1, page_size: int = 20) -> Tuple[List[Dict[str, Any]], int]:
    """Alias para mantener compatibilidad"""
    return get_filtered_products_service(filters, page, page_size)

def hard_delete_product_db(product_id: int) -> bool:
    """Alias para mantener compatibilidad"""
    return delete_product_service(product_id, soft_delete=False)

def create_complete_product_db(product_data: ProductCompleteCreate) -> Optional[int]:
    """Alias para mantener compatibilidad"""
    return create_complete_product_service(product_data)

def get_products_by_category_db(category: CategoryEnum, page: int = 1, page_size: int = 20) -> Tuple[List[Dict[str, Any]], int]:
    """Alias para mantener compatibilidad"""
    filters = ProductFilters(category=category)
    return get_filtered_products_service(filters, page, page_size)

def search_products_db(search_term: str, page: int = 1, page_size: int = 20) -> Tuple[List[Dict[str, Any]], int]:
    """Alias para mantener compatibilidad"""
    filters = ProductFilters(search=search_term)
    return get_filtered_products_service(filters, page, page_size)

def get_products_in_stock_db(page: int = 1, page_size: int = 20) -> Tuple[List[Dict[str, Any]], int]:
    """Alias para mantener compatibilidad"""
    filters = ProductFilters(in_stock=True, is_active=True)
    return get_filtered_products_service(filters, page, page_size)

def update_stock_db(product_id: int, new_stock: int) -> bool:
    """Alias para mantener compatibilidad"""
    return update_product_stock_service(product_id, new_stock)