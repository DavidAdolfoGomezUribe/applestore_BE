from database import get_connection
from schemas.product.productSchemas import (
    ProductCreate, ProductUpdate, ProductFilters, 
    ProductCompleteCreate, CategoryEnum,
    iPhoneSpecCreate, MacSpecCreate, iPadSpecCreate, 
    AppleWatchSpecCreate, AccessorySpecCreate
)
from typing import Optional, Dict, Any, List, Tuple
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

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

# ========== CRUD BÁSICO PRODUCTOS ==========
def create_product_db(product_data: ProductCreate) -> Optional[int]:
    """Crea un producto básico y retorna su ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO products (name, category, description, price, stock, 
                            image_primary_url, image_secondary_url, image_tertiary_url, 
                            release_date, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            product_data.name,
            product_data.category.value,
            product_data.description,
            product_data.price,
            product_data.stock,
            product_data.image_primary_url,
            product_data.image_secondary_url,
            product_data.image_tertiary_url,
            product_data.release_date,
            product_data.is_active
        )
        
        cursor.execute(query, values)
        product_id = cursor.lastrowid
        conn.commit()
        
        logger.info(f"Producto creado con ID: {product_id}")
        return product_id
        
    except Exception as e:
        logger.error(f"Error creando producto: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def get_product_by_id_db(product_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene un producto por ID con todas sus especificaciones"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obtener producto base
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return None
        
        # Obtener especificaciones según categoría
        category = product['category']
        spec_data = None
        
        if category == 'Iphone':
            cursor.execute("SELECT * FROM iphones WHERE id = %s", (product_id,))
            spec_data = cursor.fetchone()
            if spec_data:
                # Parsear campos JSON
                for json_field in ['storage_options', 'colors', 'cameras', 'camera_features', 'connectivity', 'box_contents']:
                    if spec_data.get(json_field):
                        spec_data[json_field] = parse_json_field(spec_data[json_field])
                        
        elif category == 'Mac':
            cursor.execute("SELECT * FROM macs WHERE id = %s", (product_id,))
            spec_data = cursor.fetchone()
            if spec_data:
                for json_field in ['chip_cores', 'ram_gb', 'storage_options', 'display_features', 'ports', 'audio_features', 'wireless', 'colors']:
                    if spec_data.get(json_field):
                        spec_data[json_field] = parse_json_field(spec_data[json_field])
                        
        elif category == 'Ipad':
            cursor.execute("SELECT * FROM ipads WHERE id = %s", (product_id,))
            spec_data = cursor.fetchone()
            if spec_data:
                for json_field in ['storage_options', 'connectivity_options', 'cellular_bands', 'cameras', 'camera_features', 'display_features', 'ports', 'audio_features', 'colors']:
                    if spec_data.get(json_field):
                        spec_data[json_field] = parse_json_field(spec_data[json_field])
                        
        elif category == 'Watch':
            cursor.execute("SELECT * FROM apple_watches WHERE id = %s", (product_id,))
            spec_data = cursor.fetchone()
            if spec_data:
                for json_field in ['case_sizes', 'case_materials', 'display_features', 'connectivity', 'health_sensors', 'fitness_features', 'buttons', 'band_compatibility', 'colors']:
                    if spec_data.get(json_field):
                        spec_data[json_field] = parse_json_field(spec_data[json_field])
                        
        elif category == 'Accessories':
            cursor.execute("SELECT * FROM accessories WHERE id = %s", (product_id,))
            spec_data = cursor.fetchone()
            if spec_data:
                for json_field in ['compatibility', 'connectivity', 'materials', 'colors', 'special_features', 'included_accessories']:
                    if spec_data.get(json_field):
                        spec_data[json_field] = parse_json_field(spec_data[json_field])
        
        result = {
            'product': product,
            'specifications': spec_data
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error obteniendo producto {product_id}: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def get_products_list_db(filters: ProductFilters, page: int = 1, page_size: int = 20) -> Tuple[List[Dict[str, Any]], int]:
    """Obtiene lista de productos con filtros y paginación"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Construir WHERE clause
        where_conditions = []
        params = []
        
        if filters.category:
            where_conditions.append("category = %s")
            params.append(filters.category.value)
            
        if filters.min_price is not None:
            where_conditions.append("price >= %s")
            params.append(filters.min_price)
            
        if filters.max_price is not None:
            where_conditions.append("price <= %s")
            params.append(filters.max_price)
            
        if filters.in_stock is not None:
            if filters.in_stock:
                where_conditions.append("stock > 0")
            else:
                where_conditions.append("stock = 0")
                
        if filters.is_active is not None:
            where_conditions.append("is_active = %s")
            params.append(filters.is_active)
            
        if filters.search:
            where_conditions.append("(name LIKE %s OR description LIKE %s)")
            search_term = f"%{filters.search}%"
            params.extend([search_term, search_term])
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Contar total
        count_query = f"SELECT COUNT(*) as total FROM products {where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # Obtener productos con paginación
        offset = (page - 1) * page_size
        products_query = f"""
        SELECT * FROM products {where_clause} 
        ORDER BY created_at DESC 
        LIMIT %s OFFSET %s
        """
        
        cursor.execute(products_query, params + [page_size, offset])
        products = cursor.fetchall()
        
        return products, total
        
    except Exception as e:
        logger.error(f"Error obteniendo lista de productos: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def update_product_db(product_id: int, product_data: ProductUpdate) -> bool:
    """Actualiza un producto básico"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Construir query dinámicamente solo con campos que no son None
        update_fields = []
        values = []
        
        for field, value in product_data.dict(exclude_unset=True).items():
            if field == 'category' and value:
                update_fields.append("category = %s")
                values.append(value.value)
            else:
                update_fields.append(f"{field} = %s")
                values.append(value)
        
        if not update_fields:
            return True  # Nada que actualizar
        
        query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = %s"
        values.append(product_id)
        
        cursor.execute(query, values)
        affected_rows = cursor.rowcount
        conn.commit()
        
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"Error actualizando producto {product_id}: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def delete_product_db(product_id: int) -> bool:
    """Elimina un producto (soft delete)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar que existe
        cursor.execute("SELECT id FROM products WHERE id = %s", (product_id,))
        if not cursor.fetchone():
            return False
        
        # Soft delete
        cursor.execute("UPDATE products SET is_active = FALSE WHERE id = %s", (product_id,))
        affected_rows = cursor.rowcount
        conn.commit()
        
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"Error eliminando producto {product_id}: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def hard_delete_product_db(product_id: int) -> bool:
    """Elimina un producto permanentemente"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        affected_rows = cursor.rowcount
        conn.commit()
        
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"Error eliminando permanentemente producto {product_id}: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

# ========== CRUD ESPECÍFICO POR CATEGORÍA ==========
def create_iphone_spec_db(product_id: int, spec_data: iPhoneSpecCreate) -> bool:
    """Crea especificaciones de iPhone"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO iphones (
            id, model, generation, model_type, storage_options, storage_gb, colors,
            display_size, display_technology, display_resolution, display_ppi, chip,
            cameras, camera_features, front_camera, battery_video_hours, fast_charging,
            wireless_charging, magsafe_compatible, water_resistance, connectivity,
            face_id, touch_id, operating_system, height_mm, width_mm, depth_mm,
            weight_grams, box_contents
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        values = (
            product_id, spec_data.model, spec_data.generation, spec_data.model_type,
            format_json_field(spec_data.storage_options), spec_data.storage_gb,
            format_json_field(spec_data.colors), spec_data.display_size,
            spec_data.display_technology, spec_data.display_resolution,
            spec_data.display_ppi, spec_data.chip, format_json_field(spec_data.cameras),
            format_json_field(spec_data.camera_features), spec_data.front_camera,
            spec_data.battery_video_hours, spec_data.fast_charging,
            spec_data.wireless_charging, spec_data.magsafe_compatible,
            spec_data.water_resistance, format_json_field(spec_data.connectivity),
            spec_data.face_id, spec_data.touch_id, spec_data.operating_system,
            spec_data.height_mm, spec_data.width_mm, spec_data.depth_mm,
            spec_data.weight_grams, format_json_field(spec_data.box_contents)
        )
        
        cursor.execute(query, values)
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error creando spec iPhone: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def create_mac_spec_db(product_id: int, spec_data: MacSpecCreate) -> bool:
    """Crea especificaciones de Mac"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO macs (
            id, product_line, screen_size, chip, chip_cores, ram_gb, ram_gb_base,
            ram_type, storage_options, storage_gb, storage_type, display_technology,
            display_resolution, display_ppi, display_brightness_nits, display_features,
            ports, keyboard_type, touch_bar, touch_id, webcam, audio_features,
            wireless, operating_system, battery_hours, height_mm, width_mm,
            depth_mm, weight_kg, colors, target_audience
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        values = (
            product_id, spec_data.product_line, spec_data.screen_size, spec_data.chip,
            format_json_field(spec_data.chip_cores), format_json_field(spec_data.ram_gb),
            spec_data.ram_gb_base, spec_data.ram_type, format_json_field(spec_data.storage_options),
            spec_data.storage_gb, spec_data.storage_type, spec_data.display_technology,
            spec_data.display_resolution, spec_data.display_ppi, spec_data.display_brightness_nits,
            format_json_field(spec_data.display_features), format_json_field(spec_data.ports),
            spec_data.keyboard_type, spec_data.touch_bar, spec_data.touch_id, spec_data.webcam,
            format_json_field(spec_data.audio_features), format_json_field(spec_data.wireless),
            spec_data.operating_system, spec_data.battery_hours, spec_data.height_mm,
            spec_data.width_mm, spec_data.depth_mm, spec_data.weight_kg,
            format_json_field(spec_data.colors), spec_data.target_audience
        )
        
        cursor.execute(query, values)
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error creando spec Mac: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def create_ipad_spec_db(product_id: int, spec_data: iPadSpecCreate) -> bool:
    """Crea especificaciones de iPad"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO ipads (
            id, product_line, generation, screen_size, display_technology,
            display_resolution, display_ppi, display_brightness_nits, display_features,
            chip, storage_options, storage_gb, connectivity_options, cellular_support,
            cellular_bands, cameras, camera_features, apple_pencil_support,
            magic_keyboard_support, smart_connector, ports, audio_features,
            touch_id, face_id, operating_system, battery_hours, height_mm,
            width_mm, depth_mm, weight_grams, colors
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        values = (
            product_id, spec_data.product_line, spec_data.generation, spec_data.screen_size,
            spec_data.display_technology, spec_data.display_resolution, spec_data.display_ppi,
            spec_data.display_brightness_nits, format_json_field(spec_data.display_features),
            spec_data.chip, format_json_field(spec_data.storage_options), spec_data.storage_gb,
            format_json_field(spec_data.connectivity_options), spec_data.cellular_support,
            format_json_field(spec_data.cellular_bands), format_json_field(spec_data.cameras),
            format_json_field(spec_data.camera_features), spec_data.apple_pencil_support,
            spec_data.magic_keyboard_support, spec_data.smart_connector,
            format_json_field(spec_data.ports), format_json_field(spec_data.audio_features),
            spec_data.touch_id, spec_data.face_id, spec_data.operating_system,
            spec_data.battery_hours, spec_data.height_mm, spec_data.width_mm,
            spec_data.depth_mm, spec_data.weight_grams, format_json_field(spec_data.colors)
        )
        
        cursor.execute(query, values)
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error creando spec iPad: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def create_apple_watch_spec_db(product_id: int, spec_data: AppleWatchSpecCreate) -> bool:
    """Crea especificaciones de Apple Watch"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO apple_watches (
            id, series, model_type, case_sizes, case_size_mm, case_materials,
            case_material, display_technology, display_size_sq_mm, display_brightness_nits,
            display_features, chip, storage_gb, connectivity, cellular_support,
            health_sensors, fitness_features, crown_type, buttons, water_resistance,
            operating_system, battery_hours, fast_charging, charging_method,
            band_compatibility, height_mm, width_mm, depth_mm, weight_grams,
            colors, target_audience
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        values = (
            product_id, spec_data.series, spec_data.model_type,
            format_json_field(spec_data.case_sizes), spec_data.case_size_mm,
            format_json_field(spec_data.case_materials), spec_data.case_material,
            spec_data.display_technology, spec_data.display_size_sq_mm,
            spec_data.display_brightness_nits, format_json_field(spec_data.display_features),
            spec_data.chip, spec_data.storage_gb, format_json_field(spec_data.connectivity),
            spec_data.cellular_support, format_json_field(spec_data.health_sensors),
            format_json_field(spec_data.fitness_features), spec_data.crown_type,
            format_json_field(spec_data.buttons), spec_data.water_resistance,
            spec_data.operating_system, spec_data.battery_hours, spec_data.fast_charging,
            spec_data.charging_method, format_json_field(spec_data.band_compatibility),
            spec_data.height_mm, spec_data.width_mm, spec_data.depth_mm,
            spec_data.weight_grams, format_json_field(spec_data.colors), spec_data.target_audience
        )
        
        cursor.execute(query, values)
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error creando spec Apple Watch: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def create_accessory_spec_db(product_id: int, spec_data: AccessorySpecCreate) -> bool:
    """Crea especificaciones de Accesorio"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        INSERT INTO accessories (
            id, accessory_type, category, compatibility, wireless_technology,
            connectivity, battery_hours, charging_case_hours, fast_charging,
            noise_cancellation, water_resistance, materials, colors,
            dimensions_mm, weight_grams, special_features, included_accessories,
            operating_system_req
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        values = (
            product_id, spec_data.accessory_type, spec_data.category,
            format_json_field(spec_data.compatibility), spec_data.wireless_technology,
            format_json_field(spec_data.connectivity), spec_data.battery_hours,
            spec_data.charging_case_hours, spec_data.fast_charging,
            spec_data.noise_cancellation, spec_data.water_resistance,
            format_json_field(spec_data.materials), format_json_field(spec_data.colors),
            spec_data.dimensions_mm, spec_data.weight_grams,
            format_json_field(spec_data.special_features),
            format_json_field(spec_data.included_accessories), spec_data.operating_system_req
        )
        
        cursor.execute(query, values)
        conn.commit()
        return True
        
    except Exception as e:
        logger.error(f"Error creando spec Accessory: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

# ========== FUNCIÓN PARA CREAR PRODUCTO COMPLETO ==========
def create_complete_product_db(product_data: ProductCompleteCreate) -> Optional[int]:
    """Crea un producto completo con sus especificaciones"""
    try:
        # Crear producto base
        product_id = create_product_db(product_data.product)
        
        if not product_id:
            raise Exception("Error creando producto base")
        
        # Crear especificaciones según categoría
        category = product_data.product.category
        
        if category == CategoryEnum.IPHONE and product_data.iphone_spec:
            create_iphone_spec_db(product_id, product_data.iphone_spec)
        elif category == CategoryEnum.MAC and product_data.mac_spec:
            create_mac_spec_db(product_id, product_data.mac_spec)
        elif category == CategoryEnum.IPAD and product_data.ipad_spec:
            create_ipad_spec_db(product_id, product_data.ipad_spec)
        elif category == CategoryEnum.WATCH and product_data.apple_watch_spec:
            create_apple_watch_spec_db(product_id, product_data.apple_watch_spec)
        elif category == CategoryEnum.ACCESSORIES and product_data.accessory_spec:
            create_accessory_spec_db(product_id, product_data.accessory_spec)
        
        logger.info(f"Producto completo creado con ID: {product_id}")
        return product_id
        
    except Exception as e:
        logger.error(f"Error creando producto completo: {str(e)}")
        # Si falla, intentar limpiar el producto base creado
        if 'product_id' in locals():
            try:
                hard_delete_product_db(product_id)
            except:
                pass
        raise

# ========== FUNCIONES DE UTILIDAD ==========
def get_products_by_category_db(category: CategoryEnum, page: int = 1, page_size: int = 20) -> Tuple[List[Dict[str, Any]], int]:
    """Obtiene productos por categoría"""
    filters = ProductFilters(category=category)
    return get_products_list_db(filters, page, page_size)

def search_products_db(search_term: str, page: int = 1, page_size: int = 20) -> Tuple[List[Dict[str, Any]], int]:
    """Busca productos por término"""
    filters = ProductFilters(search=search_term)
    return get_products_list_db(filters, page, page_size)

def get_products_in_stock_db(page: int = 1, page_size: int = 20) -> Tuple[List[Dict[str, Any]], int]:
    """Obtiene productos en stock"""
    filters = ProductFilters(in_stock=True, is_active=True)
    return get_products_list_db(filters, page, page_size)

def update_stock_db(product_id: int, new_stock: int) -> bool:
    """Actualiza el stock de un producto"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE products SET stock = %s WHERE id = %s", (new_stock, product_id))
        affected_rows = cursor.rowcount
        conn.commit()
        
        return affected_rows > 0
        
    except Exception as e:
        logger.error(f"Error actualizando stock del producto {product_id}: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()