
from auth.auth_middleware import get_current_admin_user, get_current_user, optional_auth
import logging
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from schemas.product.productSchemas import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    ProductFilters, ProductDetailResponse, ProductCompleteCreate,
    CategoryEnum
)
from services.product.productService import (
    get_product_by_id_service, get_filtered_products_service,
    update_product_service, delete_product_service,
    create_complete_product_service, get_products_by_category_service,
    update_product_stock_service
)

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
                        "total": 24
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
        products, total = get_filtered_products_service(filters, 1, 1000)  
        product_responses = [ProductResponse(**product) for product in products]
        return ProductListResponse(
            products=product_responses,
            total=total
        )
    except Exception as e:
        logger.error(f"Error obteniendo productos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

# Ruta para obtener productos por categoría
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
        # Pass category.value (string) and correct pagination args
        products, total = get_products_by_category_service(category.value, page_size, (page-1)*page_size)
        total_pages = (total + page_size - 1) // page_size
        product_responses = [ProductResponse(**product) for product in products]
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
        product_data = get_product_by_id_service(product_id)
        
        if not product_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        return ProductDetailResponse(**product_data)
        
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
def create_product(
    product_data: ProductCompleteCreate,
    current_user=Depends(get_current_admin_user)
):
    """
    Crea un producto completo con todas sus especificaciones.
    Requiere rol de administrador.
    """
    try:
        product_id = create_complete_product_service(product_data)
        
        if not product_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creando producto completo"
            )
        
        # Obtener producto creado con especificaciones
        product_db = get_product_by_id_service(product_id)
        if not product_db:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error obteniendo producto creado"
            )
        return ProductDetailResponse(**product_db)
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
        existing_product = get_product_by_id_service(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        # Actualizar producto
        success = update_product_service(product_id, product_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error actualizando producto"
            )
        
        # Obtener producto actualizado
        product_updated = get_product_by_id_service(product_id)
        
        if not product_updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error obteniendo producto actualizado"
            )
        
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
        existing_product = get_product_by_id_service(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        
        # Actualizar stock
        success = update_product_stock_service(product_id, new_stock)
        
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