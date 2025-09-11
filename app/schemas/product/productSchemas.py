from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum

class CategoryEnum(str, Enum):
    IPHONE = "Iphone"
    MAC = "Mac"
    IPAD = "Ipad"
    WATCH = "Watch"
    ACCESSORIES = "Accessories"

# ========== SCHEMAS BASE ==========
class ProductBase(BaseModel):
    name: str = Field(..., max_length=100, description="Nombre del producto")
    category: CategoryEnum = Field(..., description="Categoría del producto")
    description: Optional[str] = Field(None, description="Descripción del producto")
    price: float = Field(..., gt=0, description="Precio del producto")
    stock: int = Field(..., ge=0, description="Stock disponible")
    image_primary_url: Optional[str] = Field(None, description="URL de imagen principal")
    image_secondary_url: Optional[str] = Field(None, description="URL de imagen secundaria")
    image_tertiary_url: Optional[str] = Field(None, description="URL de imagen terciaria")
    release_date: Optional[date] = Field(None, description="Fecha de lanzamiento")
    is_active: bool = Field(True, description="Si el producto está activo")

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    category: Optional[CategoryEnum] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    image_primary_url: Optional[str] = None
    image_secondary_url: Optional[str] = None
    image_tertiary_url: Optional[str] = None
    release_date: Optional[date] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ========== FILTROS Y BÚSQUEDA ==========
class ProductFilters(BaseModel):
    category: Optional[CategoryEnum] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    in_stock: Optional[bool] = None
    is_active: Optional[bool] = None
    search: Optional[str] = Field(None, description="Búsqueda por nombre o descripción")

class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

# ========== SCHEMAS ESPECÍFICOS POR CATEGORÍA ==========

# iPhone Schemas
class iPhoneSpecCreate(BaseModel):
    model: str = Field(..., max_length=50)
    generation: int = Field(..., gt=0)
    model_type: str = Field(..., description="standard, Plus, Pro, Pro Max, SE")
    storage_options: List[str] = Field(..., description="Opciones de almacenamiento")
    storage_gb: int = Field(..., gt=0)
    colors: List[str] = Field(..., description="Colores disponibles")
    display_size: float = Field(..., gt=0)
    display_technology: Optional[str] = None
    display_resolution: Optional[str] = None
    display_ppi: Optional[int] = None
    chip: str = Field(..., max_length=30)
    cameras: Dict[str, Any] = Field(..., description="Configuración de cámaras")
    camera_features: List[str] = Field(default_factory=list)
    front_camera: Optional[str] = None
    battery_video_hours: Optional[int] = None
    fast_charging: bool = True
    wireless_charging: bool = True
    magsafe_compatible: bool = True
    water_resistance: Optional[str] = None
    connectivity: List[str] = Field(default_factory=list)
    face_id: bool = True
    touch_id: bool = False
    operating_system: str = "iOS 17"
    height_mm: Optional[float] = None
    width_mm: Optional[float] = None
    depth_mm: Optional[float] = None
    weight_grams: Optional[int] = None
    box_contents: List[str] = Field(default_factory=list)

class iPhoneSpecResponse(iPhoneSpecCreate):
    id: int

# Mac Schemas
class MacSpecCreate(BaseModel):
    product_line: str = Field(..., description="MacBook Air, MacBook Pro, iMac, etc.")
    screen_size: Optional[float] = None
    chip: str = Field(..., max_length=30)
    chip_cores: Dict[str, int] = Field(..., description="CPU, GPU, Neural cores")
    ram_gb: List[int] = Field(..., description="Opciones de RAM")
    ram_gb_base: int = Field(..., gt=0)
    ram_type: Optional[str] = None
    storage_options: List[str] = Field(...)
    storage_gb: int = Field(..., gt=0)
    storage_type: Optional[str] = None
    display_technology: Optional[str] = None
    display_resolution: Optional[str] = None
    display_ppi: Optional[int] = None
    display_brightness_nits: Optional[int] = None
    display_features: List[str] = Field(default_factory=list)
    ports: List[str] = Field(default_factory=list)
    keyboard_type: Optional[str] = None
    touch_bar: bool = False
    touch_id: bool = True
    webcam: Optional[str] = None
    audio_features: List[str] = Field(default_factory=list)
    wireless: List[str] = Field(default_factory=list)
    operating_system: str = "macOS Sonoma"
    battery_hours: Optional[int] = None
    height_mm: Optional[float] = None
    width_mm: Optional[float] = None
    depth_mm: Optional[float] = None
    weight_kg: Optional[float] = None
    colors: List[str] = Field(default_factory=list)
    target_audience: str = "Consumer"

class MacSpecResponse(MacSpecCreate):
    id: int

# iPad Schemas
class iPadSpecCreate(BaseModel):
    product_line: str = Field(..., description="iPad Pro, iPad Air, iPad, iPad mini")
    generation: Optional[int] = None
    screen_size: float = Field(..., gt=0)
    display_technology: Optional[str] = None
    display_resolution: Optional[str] = None
    display_ppi: Optional[int] = None
    display_brightness_nits: Optional[int] = None
    display_features: List[str] = Field(default_factory=list)
    chip: str = Field(..., max_length=30)
    storage_options: List[str] = Field(...)
    storage_gb: int = Field(..., gt=0)
    connectivity_options: List[str] = Field(default_factory=list)
    cellular_support: bool = False
    cellular_bands: List[str] = Field(default_factory=list)
    cameras: Dict[str, str] = Field(default_factory=dict)
    camera_features: List[str] = Field(default_factory=list)
    apple_pencil_support: str = "None"
    magic_keyboard_support: bool = False
    smart_connector: bool = False
    ports: List[str] = Field(default_factory=list)
    audio_features: List[str] = Field(default_factory=list)
    touch_id: bool = True
    face_id: bool = False
    operating_system: str = "iPadOS 17"
    battery_hours: Optional[int] = None
    height_mm: Optional[float] = None
    width_mm: Optional[float] = None
    depth_mm: Optional[float] = None
    weight_grams: Optional[int] = None
    colors: List[str] = Field(default_factory=list)

class iPadSpecResponse(iPadSpecCreate):
    id: int

# Apple Watch Schemas
class AppleWatchSpecCreate(BaseModel):
    series: int = Field(..., gt=0)
    model_type: str = Field(..., description="Standard, SE, Ultra, Nike, Hermès")
    case_sizes: List[str] = Field(...)
    case_size_mm: int = Field(..., gt=0)
    case_materials: List[str] = Field(...)
    case_material: str = Field(..., max_length=30)
    display_technology: Optional[str] = None
    display_size_sq_mm: Optional[int] = None
    display_brightness_nits: Optional[int] = None
    display_features: List[str] = Field(default_factory=list)
    chip: Optional[str] = None
    storage_gb: int = 32
    connectivity: List[str] = Field(default_factory=list)
    cellular_support: bool = False
    health_sensors: List[str] = Field(default_factory=list)
    fitness_features: List[str] = Field(default_factory=list)
    crown_type: str = "Digital Crown with haptic feedback"
    buttons: List[str] = Field(default_factory=list)
    water_resistance: Optional[str] = None
    operating_system: str = "watchOS 10"
    battery_hours: Optional[int] = None
    fast_charging: bool = True
    charging_method: Optional[str] = None
    band_compatibility: List[str] = Field(default_factory=list)
    height_mm: Optional[float] = None
    width_mm: Optional[float] = None
    depth_mm: Optional[float] = None
    weight_grams: Optional[float] = None
    colors: List[str] = Field(default_factory=list)
    target_audience: str = "Everyday"

class AppleWatchSpecResponse(AppleWatchSpecCreate):
    id: int

# Accessories Schemas
class AccessorySpecCreate(BaseModel):
    accessory_type: str = Field(..., description="Audio, Charging, Input, etc.")
    category: str = Field(..., max_length=50)
    compatibility: List[str] = Field(default_factory=list)
    wireless_technology: Optional[str] = None
    connectivity: List[str] = Field(default_factory=list)
    battery_hours: Optional[int] = None
    charging_case_hours: Optional[int] = None
    fast_charging: bool = False
    noise_cancellation: bool = False
    water_resistance: Optional[str] = None
    materials: List[str] = Field(default_factory=list)
    colors: List[str] = Field(default_factory=list)
    dimensions_mm: Optional[str] = None
    weight_grams: Optional[float] = None
    special_features: List[str] = Field(default_factory=list)
    included_accessories: List[str] = Field(default_factory=list)
    operating_system_req: Optional[str] = None

class AccessorySpecResponse(AccessorySpecCreate):
    id: int

# Schema unificado para producto completo
class ProductDetailResponse(ProductResponse):
    iphone_spec: Optional[iPhoneSpecResponse] = None
    mac_spec: Optional[MacSpecResponse] = None
    ipad_spec: Optional[iPadSpecResponse] = None
    apple_watch_spec: Optional[AppleWatchSpecResponse] = None
    accessory_spec: Optional[AccessorySpecResponse] = None

# Schema para crear producto completo
class ProductCompleteCreate(BaseModel):
    product: ProductCreate
    iphone_spec: Optional[iPhoneSpecCreate] = None
    mac_spec: Optional[MacSpecCreate] = None
    ipad_spec: Optional[iPadSpecCreate] = None
    apple_watch_spec: Optional[AppleWatchSpecCreate] = None
    accessory_spec: Optional[AccessorySpecCreate] = None

    class Config:
        schema_extra = {
            "examples": [
                {
                    "product": {
                        "name": "iPhone 16 Pro Max",
                        "category": "Iphone",
                        "description": "El iPhone más avanzado con titanio, cámara de 48MP con zoom óptico 5x y chip A18 Pro.",
                        "price": 1299.99,
                        "stock": 50,
                        "image_primary_url": "https://example.com/iphone16pro.jpg",
                        "image_secondary_url": "https://example.com/iphone16pro-camera.jpg",
                        "image_tertiary_url": "https://example.com/iphone16pro-action.jpg",
                        "release_date": "2024-09-22",
                        "is_active": True
                    },
                    "iphone_spec": {
                        "model": "iPhone 16 Pro Max",
                        "generation": 16,
                        "model_type": "Pro Max",
                        "storage_options": ["256GB", "512GB", "1TB"],
                        "storage_gb": 256,
                        "colors": ["Natural Titanium", "Blue Titanium", "White Titanium", "Black Titanium"],
                        "display_size": 6.9,
                        "display_technology": "Super Retina XDR",
                        "display_resolution": "2868×1320",
                        "display_ppi": 460,
                        "chip": "A18 Pro",
                        "cameras": {
                            "main": "48MP Fusion",
                            "telephoto": "12MP 5x Telephoto",
                            "ultra_wide": "48MP Ultra Wide"
                        },
                        "camera_features": ["Night mode", "Portrait mode", "4K ProRes", "Action mode", "Macro photography"],
                        "front_camera": "12MP TrueDepth",
                        "battery_video_hours": 33,
                        "fast_charging": True,
                        "wireless_charging": True,
                        "magsafe_compatible": True,
                        "water_resistance": "IP68",
                        "connectivity": ["5G", "WiFi 7", "Bluetooth 5.3", "USB-C", "Thread"],
                        "face_id": True,
                        "touch_id": False,
                        "operating_system": "iOS 18",
                        "height_mm": 163.0,
                        "width_mm": 77.6,
                        "depth_mm": 8.25,
                        "weight_grams": 227,
                        "box_contents": ["iPhone", "USB-C to USB-C Cable", "Documentation"]
                    }
                }
            ]
        }

    @validator('iphone_spec')
    def validate_iphone_spec(cls, v, values):
        if values.get('product') and values['product'].category == CategoryEnum.IPHONE and not v:
            raise ValueError('iPhone specifications are required for iPhone products')
        return v

    @validator('mac_spec')
    def validate_mac_spec(cls, v, values):
        if values.get('product') and values['product'].category == CategoryEnum.MAC and not v:
            raise ValueError('Mac specifications are required for Mac products')
        return v

    @validator('ipad_spec')
    def validate_ipad_spec(cls, v, values):
        if values.get('product') and values['product'].category == CategoryEnum.IPAD and not v:
            raise ValueError('iPad specifications are required for iPad products')
        return v

    @validator('apple_watch_spec')
    def validate_watch_spec(cls, v, values):
        if values.get('product') and values['product'].category == CategoryEnum.WATCH and not v:
            raise ValueError('Apple Watch specifications are required for Watch products')
        return v

    @validator('accessory_spec')
    def validate_accessory_spec(cls, v, values):
        if values.get('product') and values['product'].category == CategoryEnum.ACCESSORIES and not v:
            raise ValueError('Accessory specifications are required for Accessory products')
        return v