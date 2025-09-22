# 🍎 Apple Store Backend API - Documentación Completa

## 📋 Información General

**Base URL:** `http://localhost:8000`  
**Versión:** 1.0.0  
**Documentación Interactiva:** 
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔐 Autenticación

La API utiliza **JWT (JSON Web Tokens)** para autenticación.

### Obtener Token
```bash
POST /users/login
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "contraseña123"
}
```

### Usar Token
Incluir en todas las rutas protegidas:
```
Authorization: Bearer <your_jwt_token>
```

### Roles de Usuario
- **user**: Funciones básicas y gestión de perfil propio
- **admin**: Acceso completo incluyendo gestión de productos y usuarios

---

## 👥 Endpoints de Usuarios

### 📝 Registro de Usuario
```bash
POST /users/register
Content-Type: application/json

{
  "name": "Juan Pérez",
  "email": "juan@example.com", 
  "password": "miPassword123",
  "role": "user"
}
```

### 🔑 Iniciar Sesión
```bash
POST /users/login
Content-Type: application/json

{
  "email": "juan@example.com",
  "password": "miPassword123"
}
```

### 👤 Perfil del Usuario Autenticado
```bash
# Obtener perfil
GET /users/me
Authorization: Bearer <token>

# Actualizar perfil
PUT /users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Nuevo Nombre",
  "email": "nuevo@email.com"
}

# Cambiar contraseña
PUT /users/me/password
Authorization: Bearer <token>
Content-Type: application/json

{
  "current_password": "passwordActual",
  "new_password": "nuevoPassword123"
}

# Eliminar cuenta
DELETE /users/me
Authorization: Bearer <token>
```

### 🛡️ Administración de Usuarios (Solo Admin)
```bash
# Listar todos los usuarios
GET /users/?skip=0&limit=100
Authorization: Bearer <admin_token>

# Obtener usuario específico
GET /users/{user_id}
Authorization: Bearer <admin_token>

# Actualizar usuario
PUT /users/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Nombre Actualizado",
  "email": "nuevo@email.com",
  "role": "admin"
}

# Eliminar usuario
DELETE /users/{user_id}
Authorization: Bearer <admin_token>
```

---

## 📱 Endpoints de Productos

### 🔍 Rutas Públicas (Sin Autenticación)

#### Listar Productos con Filtros
```bash
GET /products/?category=Iphone&min_price=500&max_price=2000&in_stock=true&search=Pro&page=1&page_size=20

# Parámetros disponibles:
# - category: Iphone, Mac, Ipad, Watch, Accessories
# - min_price: Precio mínimo
# - max_price: Precio máximo
# - in_stock: Solo productos en stock (true/false)
# - search: Búsqueda en nombre y descripción
# - page: Número de página (inicia en 1)
# - page_size: Productos por página (máximo 100)
# - is_active: Solo productos activos (por defecto true)
```

#### Productos por Categoría
```bash
GET /products/category/Iphone?page=1&page_size=20
GET /products/category/Mac?page=1&page_size=20
GET /products/category/Ipad?page=1&page_size=20
GET /products/category/Watch?page=1&page_size=20
GET /products/category/Accessories?page=1&page_size=20
```

#### Detalle Completo de Producto
```bash
GET /products/{product_id}

# Respuesta incluye especificaciones técnicas completas según categoría:
# - iPhone: cámaras, chip, almacenamiento, colores, conectividad, etc.
# - Mac: procesador, RAM, almacenamiento, puertos, pantalla, etc.
# - iPad: pantalla, chip, Apple Pencil, cámaras, etc.
# - Apple Watch: sensores, correas, resistencia al agua, etc.
# - Accessories: compatibilidad, características especiales, etc.
```

### 🛡️ Rutas Administrativas (Solo Admin)

#### Gestión Completa de Productos
```bash
# Listar todos los productos (incluyendo inactivos)
GET /products/admin/all?include_inactive=true&page=1&page_size=20
Authorization: Bearer <admin_token>

# Crear producto básico
POST /products/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Nuevo iPhone",
  "category": "Iphone",
  "description": "Descripción del producto",
  "price": 999.99,
  "stock": 50,
  "image_primary_url": "https://example.com/image.jpg",
  "release_date": "2024-09-22",
  "is_active": true
}
```

#### Crear Producto Completo con Especificaciones
```bash
POST /products/admin/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "product": {
    "name": "iPhone 16 Pro Max",
    "category": "Iphone",
    "description": "El iPhone más avanzado con titanio y chip A18 Pro",
    "price": 1299.99,
    "stock": 50,
    "image_primary_url": "https://example.com/iphone16pro.jpg",
    "release_date": "2024-09-22",
    "is_active": true
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
    "camera_features": ["Night mode", "Portrait mode", "4K ProRes", "Action mode"],
    "front_camera": "12MP TrueDepth",
    "battery_video_hours": 33,
    "fast_charging": true,
    "wireless_charging": true,
    "magsafe_compatible": true,
    "water_resistance": "IP68",
    "connectivity": ["5G", "WiFi 7", "Bluetooth 5.3", "USB-C"],
    "face_id": true,
    "touch_id": false,
    "operating_system": "iOS 18",
    "height_mm": 163.0,
    "width_mm": 77.6,
    "depth_mm": 8.25,
    "weight_grams": 227,
    "box_contents": ["iPhone", "USB-C to USB-C Cable", "Documentation"]
  }
}
```

#### Actualizar y Eliminar Productos
```bash
# Actualizar producto
PUT /products/{product_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Nombre Actualizado",
  "price": 1199.99,
  "stock": 75,
  "is_active": true
}

# Eliminar producto (soft delete)
DELETE /products/{product_id}
Authorization: Bearer <admin_token>

# Eliminar producto permanentemente
DELETE /products/{product_id}/hard
Authorization: Bearer <admin_token>

# Actualizar solo stock
PUT /products/{product_id}/stock
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "stock": 100
}
```

---

## 🗂️ Categorías de Productos y Especificaciones

### 📱 iPhone (`category: "Iphone"`)
**Especificaciones incluidas:**
- Modelo, generación, tipo (Pro, Pro Max, etc.)
- Opciones de almacenamiento y colores
- Chip, sistema de cámaras, características de cámara
- Pantalla (tamaño, tecnología, resolución, PPI)
- Batería, carga rápida, carga inalámbrica, MagSafe
- Resistencia al agua, conectividad
- Face ID, Touch ID, sistema operativo
- Dimensiones, peso, contenido de la caja

### 💻 Mac (`category: "Mac"`)
**Especificaciones incluidas:**
- Línea de producto (MacBook Air, MacBook Pro, iMac, etc.)
- Chip (M1, M2, M3, etc.), cores CPU/GPU/Neural
- RAM (opciones y tipo), almacenamiento (opciones y tipo)
- Pantalla (tamaño, tecnología, resolución, brillo)
- Puertos, teclado, Touch Bar, Touch ID
- Cámara web, funciones de audio, conectividad inalámbrica
- Sistema operativo, batería (para portátiles)
- Dimensiones, peso, colores, audiencia objetivo

### 📱 iPad (`category: "Ipad"`)
**Especificaciones incluidas:**
- Línea de producto (iPad Pro, iPad Air, iPad, iPad mini)
- Generación, tamaño y tecnología de pantalla
- Chip, opciones de almacenamiento
- Conectividad (Wi-Fi, Wi-Fi + Cellular)
- Sistema de cámaras, características de cámara
- Compatibilidad con Apple Pencil y Magic Keyboard
- Smart Connector, puertos, funciones de audio
- Touch ID, Face ID, sistema operativo
- Batería, dimensiones, peso, colores

### ⌚ Apple Watch (`category: "Watch"`)
**Especificaciones incluidas:**
- Serie, tipo de modelo (Standard, SE, Ultra, etc.)
- Tamaños y materiales de caja
- Tecnología y características de pantalla
- Chip, almacenamiento, conectividad
- Sensores de salud, funciones de fitness
- Corona Digital, botones, resistencia al agua
- Sistema operativo, batería, carga rápida
- Compatibilidad de correas, dimensiones, peso
- Colores, audiencia objetivo

### 🎧 Accessories (`category: "Accessories"`)
**Especificaciones incluidas:**
- Tipo de accesorio (Audio, Charging, Input, etc.)
- Categoría específica (AirPods, Cables, etc.)
- Compatibilidad con dispositivos
- Tecnología inalámbrica, conectividad
- Batería, cancelación de ruido
- Resistencia al agua, materiales
- Características especiales, accesorios incluidos
- Requisitos de sistema operativo

---

## 📊 Formatos de Respuesta

### Lista de Productos
```json
{
  "products": [...],
  "total": 24,
  "page": 1,
  "page_size": 20,
  "total_pages": 2
}
```

### Producto con Especificaciones
```json
{
  "id": 1,
  "name": "iPhone 15 Pro Max",
  "category": "Iphone",
  "price": 1499.99,
  "stock": 25,
  "is_active": true,
  "created_at": "2025-09-10T15:30:00",
  "updated_at": "2025-09-10T15:30:00",
  "iphone_spec": { ... },
  "mac_spec": null,
  "ipad_spec": null,
  "apple_watch_spec": null,
  "accessory_spec": null
}
```

### Token de Autenticación
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "role": "user"
  }
}
```

---

## ⚠️ Códigos de Error

| Código | Descripción |
|--------|-------------|
| 200 | Operación exitosa |
| 201 | Recurso creado exitosamente |
| 204 | Operación exitosa sin contenido |
| 400 | Error en los datos enviados |
| 401 | No autenticado |
| 403 | Sin permisos suficientes |
| 404 | Recurso no encontrado |
| 500 | Error interno del servidor |

---

## 🚀 Ejemplos de Uso Completos

### Flujo Completo: Registro → Login → Crear Producto

```bash
# 1. Registrar usuario admin
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Admin Apple Store",
    "email": "admin@applestore.com",
    "password": "adminSecure123",
    "role": "admin"
  }'

# 2. Hacer login y obtener token
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@applestore.com",
    "password": "adminSecure123"
  }' | jq -r '.access_token'

# 3. Crear producto con especificaciones completas
curl -X POST "http://localhost:8000/products/admin/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN_AQUI>" \
  -d '{
    "product": {
      "name": "iPhone 16 Pro",
      "category": "Iphone",
      "description": "El nuevo iPhone con chip A18 Pro",
      "price": 1199.99,
      "stock": 100,
      "is_active": true
    },
    "iphone_spec": {
      "model": "iPhone 16 Pro",
      "generation": 16,
      "model_type": "Pro",
      "storage_options": ["128GB", "256GB", "512GB", "1TB"],
      "storage_gb": 256,
      "colors": ["Natural Titanium", "Blue Titanium", "White Titanium", "Black Titanium"],
      "display_size": 6.3,
      "chip": "A18 Pro",
      "cameras": {
        "main": "48MP Fusion",
        "telephoto": "12MP 3x",
        "ultra_wide": "48MP Ultra Wide"
      },
      "camera_features": ["Night mode", "Portrait mode", "4K ProRes"],
      "connectivity": ["5G", "WiFi 7", "Bluetooth 5.3", "USB-C"]
    }
  }'

# 4. Consultar producto creado
curl -X GET "http://localhost:8000/products/25" | jq
```

---

## 🛠️ Configuración de Desarrollo

### Variables de Entorno
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=applestore_db
MYSQL_PORT=3306
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Iniciar Servidor
```bash
# Con Docker
docker compose up

# Local
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📚 Recursos Adicionales

- **Swagger UI**: `http://localhost:8000/docs` - Documentación interactiva
- **ReDoc**: `http://localhost:8000/redoc` - Documentación alternativa  
- **OpenAPI JSON**: `http://localhost:8000/openapi.json` - Especificación completa
- **Health Check**: `http://localhost:8000/` - Estado de la API

---

**¡La documentación completa está disponible en Swagger UI para pruebas interactivas!** 🚀
