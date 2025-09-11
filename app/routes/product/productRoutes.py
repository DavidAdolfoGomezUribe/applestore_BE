from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from schemas.product.productSchemas import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    ProductFilters, ProductDetailResponse, ProductCompleteCreate,
    CategoryEnum
)
from services.product.productService import (
    create_product_db, get_product_by_id_db, get_products_list_db,
    update_product_db, delete_product_db, hard_delete_product_db,
    create_complete_product_db, get_products_by_category_db,
    search_products_db, get_products_in_stock_db, update_stock_db
)
from auth.auth_middleware import get_current_admin_user, get_current_user, optional_auth
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

# ========== RUTAS PÚBLICAS ==========
@router.get(
    "/", 
    response_model=ProductListResponse,
    summary="Obtener lista de productos con filtros",
    description="""
    Obtiene una lista paginada de productos con múltiples filtros disponibles.
    
    **Ruta pública:** No requiere autenticación.
    
    **Filtros disponibles:**
    - **category**: Filtrar por categoría (Iphone, Mac, Ipad, Watch, Accessories)
    - **min_price**: Precio mínimo en USD
    - **max_price**: Precio máximo en USD
    - **in_stock**: Solo productos con stock disponible
    - **search**: Búsqueda por nombre o descripción del producto
    - **is_active**: Solo productos activos (por defecto true)
    
    **Paginación:**
    - **page**: Número de página (inicia en 1)
    - **page_size**: Productos por página (máximo 100)
    
    **Respuesta:**
    - Lista de productos básicos (sin especificaciones detalladas)
    - Información de paginación (total, páginas, etc.)
    """,
    responses={
        200: {
            "description": "Lista de productos obtenida exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "products": [
                            {
                                "id": 1,
                                "name": "iPhone 15 Pro Max",
                                "category": "Iphone",
                                "description": "El iPhone más avanzado...",
                                "price": 1499.99,
                                "stock": 25,
                                "image_primary_url": "https://example.com/image.jpg",
                                "release_date": "2023-09-22",
                                "is_active": True,
                                "created_at": "2025-09-10T15:30:00",
                                "updated_at": "2025-09-10T15:30:00"
                            }
                        ],
                        "total": 24,
                        "page": 1,
                        "page_size": 20,
                        "total_pages": 2
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
def get_products(
    category: Optional[CategoryEnum] = Query(None, description="Filtrar por categoría"),
    min_price: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, ge=0, description="Precio máximo"),
    in_stock: Optional[bool] = Query(None, description="Solo productos en stock"),
    search: Optional[str] = Query(None, description="Buscar en nombre y descripción"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Productos por página"),
    is_active: Optional[bool] = Query(True, description="Solo productos activos")
):
    """
    Obtiene lista de productos con filtros y paginación.
    Ruta pública - no requiere autenticación.
    """
    try:
        filters = ProductFilters(
            category=category,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
            is_active=is_active,
            search=search
        )
        
        products, total = get_products_list_db(filters, page, page_size)
        total_pages = (total + page_size - 1) // page_size
        
        product_responses = []
        for product in products:
            product_responses.append(ProductResponse(**product))
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo productos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get(
    "/category/{category}", 
    response_model=ProductListResponse,
    summary="Obtener productos por categoría",
    description="""
    Obtiene productos de una categoría específica con paginación.
    
    **Ruta pública:** No requiere autenticación.
    
    **Categorías disponibles:**
    - **Iphone**: iPhones de todas las generaciones
    - **Mac**: MacBook, iMac, Mac Studio, Mac Pro, Mac mini
    - **Ipad**: iPad Pro, iPad Air, iPad, iPad mini
    - **Watch**: Apple Watch de todas las series
    - **Accessories**: AirPods, cables, cargadores, fundas, etc.
    
    **Parámetros:**
    - **category**: Categoría específica (requerido)
    - **page**: Número de página
    - **page_size**: Productos por página
    """,
    responses={
        200: {
            "description": "Productos de la categoría obtenidos exitosamente"
        },
        400: {
            "description": "Categoría inválida"
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
def get_products_by_category(
    category: CategoryEnum,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    Obtiene productos por categoría específica.
    Ruta pública - no requiere autenticación.
    """
    try:
        products, total = get_products_by_category_db(category, page, page_size)
        total_pages = (total + page_size - 1) // page_size
        
        product_responses = []
        for product in products:
            product_responses.append(ProductResponse(**product))
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo productos por categoría {category}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/search/{search_term}", response_model=ProductListResponse)
def search_products(
    search_term: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    Busca productos por término en nombre y descripción.
    Ruta pública - no requiere autenticación.
    """
    try:
        products, total = search_products_db(search_term, page, page_size)
        total_pages = (total + page_size - 1) // page_size
        
        product_responses = []
        for product in products:
            product_responses.append(ProductResponse(**product))
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error buscando productos con término '{search_term}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/in-stock", response_model=ProductListResponse)
def get_products_in_stock(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    Obtiene productos disponibles en stock.
    Ruta pública - no requiere autenticación.
    """
    try:
        products, total = get_products_in_stock_db(page, page_size)
        total_pages = (total + page_size - 1) // page_size
        
        product_responses = []
        for product in products:
            product_responses.append(ProductResponse(**product))
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo productos en stock: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get(
    "/{product_id}", 
    response_model=ProductDetailResponse,
    summary="Obtener detalle completo de un producto",
    description="""
    Obtiene la información completa de un producto específico, incluyendo todas sus especificaciones técnicas según su categoría.
    
    **Ruta pública:** No requiere autenticación.
    
    **Información incluida:**
    - **Datos básicos:** nombre, precio, stock, descripción, imágenes
    - **Especificaciones técnicas:** según la categoría del producto
    
    **Especificaciones por categoría:**
    - **iPhone:** cámaras, chip, almacenamiento, colores, conectividad, etc.
    - **Mac:** procesador, RAM, almacenamiento, puertos, pantalla, etc.
    - **iPad:** pantalla, chip, compatibilidad con Apple Pencil, cámaras, etc.
    - **Apple Watch:** sensores, correas, resistencia al agua, funciones de salud, etc.
    - **Accessories:** compatibilidad, características especiales, materiales, etc.
    """,
    responses={
        200: {
            "description": "Detalle del producto obtenido exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "iPhone 15 Pro Max",
                        "category": "Iphone",
                        "price": 1499.99,
                        "stock": 25,
                        "iphone_spec": {
                            "model": "iPhone 15 Pro Max",
                            "generation": 15,
                            "chip": "A17 Pro",
                            "storage_options": ["256GB", "512GB", "1TB"],
                            "colors": ["Natural Titanium", "Blue Titanium"],
                            "cameras": {
                                "main": "48MP",
                                "telephoto": "12MP 5x",
                                "ultra_wide": "12MP"
                            }
                        },
                        "mac_spec": None,
                        "ipad_spec": None,
                        "apple_watch_spec": None,
                        "accessory_spec": None
                    }
                }
            }
        },
        404: {
            "description": "Producto no encontrado",
            "content": {
                "application/json": {
                    "example": {"detail": "Producto no encontrado"}
                }
            }
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
def get_product_detail(product_id: int):
    """
    Obtiene detalle completo de un producto incluyendo especificaciones.
    Ruta pública - no requiere autenticación.
    """
    try:
        result = get_product_by_id_db(product_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        product_data = result['product']
        specifications = result['specifications']
        
        # Crear respuesta base
        response_data = ProductResponse(**product_data).dict()
        
        # Agregar especificaciones según categoría
        category = product_data['category']
        if specifications:
            if category == 'Iphone':
                response_data['iphone_spec'] = specifications
            elif category == 'Mac':
                response_data['mac_spec'] = specifications
            elif category == 'Ipad':
                response_data['ipad_spec'] = specifications
            elif category == 'Watch':
                response_data['apple_watch_spec'] = specifications
            elif category == 'Accessories':
                response_data['accessory_spec'] = specifications
        
        return ProductDetailResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo producto {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# ========== RUTAS DE ADMINISTRADOR ==========
@router.post(
    "/", 
    response_model=ProductResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto básico (Admin)",
    description="""
    Crea un nuevo producto con información básica únicamente.
    
    **Requiere permisos de administrador.**
    
    **Información básica incluida:**
    - Nombre del producto
    - Categoría (Iphone, Mac, Ipad, Watch, Accessories)
    - Descripción
    - Precio
    - Stock inicial
    - URLs de imágenes (hasta 3)
    - Fecha de lanzamiento
    - Estado activo/inactivo
    
    **Nota:** Para crear productos con especificaciones técnicas completas, usar el endpoint `/complete`.
    """,
    responses={
        201: {
            "description": "Producto básico creado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": 25,
                        "name": "Nuevo iPhone",
                        "category": "Iphone",
                        "description": "Descripción del producto",
                        "price": 999.99,
                        "stock": 50,
                        "is_active": True,
                        "created_at": "2025-09-10T15:30:00",
                        "updated_at": "2025-09-10T15:30:00"
                    }
                }
            }
        },
        400: {
            "description": "Error en los datos del producto"
        },
        401: {
            "description": "No autenticado"
        },
        403: {
            "description": "Sin permisos de administrador"
        }
    }
)
def create_product(
    product: ProductCreate,
    current_user=Depends(get_current_admin_user)
):
    """
    Crea un producto básico.
    Requiere rol de administrador.
    """
    try:
        product_id = create_product_db(product)
        
        if not product_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creando producto"
            )
        
        # Obtener producto creado para devolver respuesta completa
        result = get_product_by_id_db(product_id)
        product_data = result['product']
        
        return ProductResponse(**product_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando producto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post(
    "/admin/", 
    response_model=ProductDetailResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto completo con especificaciones (Admin)",
    description="""
    Crea un nuevo producto con todas sus especificaciones técnicas según su categoría.
    
    **Requiere permisos de administrador.**
    
    **Funcionalidad principal:**
    - Crea el producto base Y sus especificaciones técnicas en una sola operación
    - Validación automática de que las especificaciones coincidan con la categoría
    - Transacción completa (si falla, se revierte todo)
    
    **Especificaciones requeridas según categoría:**
    
    **iPhone (iphone_spec requerido):**
    - Modelo, generación, tipo (Pro, Pro Max, etc.)
    - Opciones de almacenamiento, colores disponibles
    - Chip, cámaras, características de cámara
    - Pantalla, batería, conectividad
    - Dimensiones, peso, contenido de la caja
    
    **Mac (mac_spec requerido):**
    - Línea de producto (MacBook Air, MacBook Pro, etc.)
    - Chip, cores CPU/GPU, opciones de RAM
    - Almacenamiento, puertos, pantalla
    - Teclado, cámara web, funciones de audio
    - Dimensiones, peso, colores
    
    **iPad (ipad_spec requerido):**
    - Línea de producto, generación, tamaño de pantalla
    - Chip, almacenamiento, opciones de conectividad
    - Cámaras, compatibilidad con Apple Pencil
    - Magic Keyboard, puertos, funciones de audio
    
    **Apple Watch (apple_watch_spec requerido):**
    - Serie, tipo de modelo, tamaños de caja
    - Materiales, pantalla, chip
    - Sensores de salud, funciones de fitness
    - Resistencia al agua, compatibilidad de correas
    
    **Accessories (accessory_spec requerido):**
    - Tipo de accesorio, categoría, compatibilidad
    - Tecnología inalámbrica, conectividad
    - Características especiales, materiales
    - Dimensiones, accesorios incluidos
    """,
    responses={
        201: {
            "description": "Producto completo creado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": 25,
                        "name": "iPhone 16 Pro",
                        "category": "Iphone",
                        "price": 1199.99,
                        "stock": 30,
                        "iphone_spec": {
                            "model": "iPhone 16 Pro",
                            "generation": 16,
                            "chip": "A18 Pro",
                            "storage_options": ["128GB", "256GB", "512GB", "1TB"],
                            "colors": ["Natural Titanium", "Blue Titanium"]
                        },
                        "mac_spec": None,
                        "ipad_spec": None,
                        "apple_watch_spec": None,
                        "accessory_spec": None
                    }
                }
            }
        },
        400: {
            "description": "Error de validación - especificaciones no coinciden con la categoría",
            "content": {
                "application/json": {
                    "example": {"detail": "iPhone specifications are required for iPhone products"}
                }
            }
        },
        401: {
            "description": "No autenticado"
        },
        403: {
            "description": "Sin permisos de administrador"
        },
        500: {
            "description": "Error interno del servidor"
        }
    }
)
def create_complete_product(
    product_data: ProductCompleteCreate,
    current_user=Depends(get_current_admin_user)
):
    """
    Crea un producto completo con todas sus especificaciones.
    Requiere rol de administrador.
    """
    try:
        product_id = create_complete_product_db(product_data)
        
        if not product_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creando producto completo"
            )
        
        # Obtener producto creado con especificaciones
        result = get_product_by_id_db(product_id)
        product_base = result['product']
        specifications = result['specifications']
        
        # Crear respuesta con especificaciones
        response_data = ProductResponse(**product_base).dict()
        
        category = product_base['category']
        if specifications:
            if category == 'Iphone':
                response_data['iphone_spec'] = specifications
            elif category == 'Mac':
                response_data['mac_spec'] = specifications
            elif category == 'Ipad':
                response_data['ipad_spec'] = specifications
            elif category == 'Watch':
                response_data['apple_watch_spec'] = specifications
            elif category == 'Accessories':
                response_data['accessory_spec'] = specifications
        
        return ProductDetailResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando producto completo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user=Depends(get_current_admin_user)
):
    """
    Actualiza un producto existente.
    Requiere rol de administrador.
    """
    try:
        # Verificar que el producto existe
        existing_product = get_product_by_id_db(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        # Actualizar producto
        success = update_product_db(product_id, product_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error actualizando producto"
            )
        
        # Obtener producto actualizado
        result = get_product_by_id_db(product_id)
        product_updated = result['product']
        
        return ProductResponse(**product_updated)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando producto {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.patch("/{product_id}/stock", response_model=dict)
def update_product_stock(
    product_id: int,
    new_stock: int = Query(..., ge=0, description="Nuevo stock del producto"),
    current_user=Depends(get_current_admin_user)
):
    """
    Actualiza solo el stock de un producto.
    Requiere rol de administrador.
    """
    try:
        # Verificar que el producto existe
        existing_product = get_product_by_id_db(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        # Actualizar stock
        success = update_stock_db(product_id, new_stock)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error actualizando stock"
            )
        
        return {
            "message": "Stock actualizado correctamente",
            "product_id": product_id,
            "new_stock": new_stock
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando stock del producto {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/{product_id}/soft", response_model=dict)
def soft_delete_product(
    product_id: int,
    current_user=Depends(get_current_admin_user)
):
    """
    Desactiva un producto (soft delete).
    Requiere rol de administrador.
    """
    try:
        success = delete_product_db(product_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        return {
            "message": "Producto desactivado correctamente",
            "product_id": product_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error desactivando producto {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/{product_id}/hard", response_model=dict)
def hard_delete_product(
    product_id: int,
    current_user=Depends(get_current_admin_user)
):
    """
    Elimina permanentemente un producto.
    Requiere rol de administrador.
    ⚠️ CUIDADO: Esta acción no se puede deshacer.
    """
    try:
        success = hard_delete_product_db(product_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        return {
            "message": "Producto eliminado permanentemente",
            "product_id": product_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando permanentemente producto {product_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# ========== RUTAS ADMINISTRATIVAS ==========
@router.get(
    "/admin/all", 
    response_model=ProductListResponse,
    summary="Obtener todos los productos (Admin)",
    description="""
    Obtiene todos los productos del sistema para administradores, con opción de incluir productos inactivos.
    
    **Requiere permisos de administrador.**
    
    **Funcionalidades especiales:**
    - Ver productos activos e inactivos
    - Acceso completo a toda la información
    - Sin restricciones de filtros
    
    **Parámetros:**
    - **page**: Número de página
    - **page_size**: Productos por página
    - **include_inactive**: Incluir productos desactivados
    """,
    responses={
        200: {
            "description": "Lista completa de productos para administrador"
        },
        401: {
            "description": "No autenticado"
        },
        403: {
            "description": "Sin permisos de administrador"
        }
    }
)
def get_all_products_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    include_inactive: bool = Query(False, description="Incluir productos inactivos"),
    current_user=Depends(get_current_admin_user)
):
    """
    Obtiene todos los productos para administradores.
    Incluye opción de ver productos inactivos.
    Requiere rol de administrador.
    """
    try:
        filters = ProductFilters(
            is_active=None if include_inactive else True
        )
        
        products, total = get_products_list_db(filters, page, page_size)
        total_pages = (total + page_size - 1) // page_size
        
        product_responses = []
        for product in products:
            product_responses.append(ProductResponse(**product))
        
        return ProductListResponse(
            products=product_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo productos para admin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )