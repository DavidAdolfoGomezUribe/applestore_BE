from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.user import userRoutes
from routes.product import productRoutes
from routes.chats import chatRoutes
from routes.ai import agentRoutes

app = FastAPI(
    title="🍎 Apple Store Backend API",
    description="""
    ## API Backend completa para Apple Store

    Esta API proporciona funcionalidades completas para gestionar una tienda Apple, incluyendo:

    ### 🔐 **Autenticación y Usuarios**
    - Registro e inicio de sesión con JWT
    - Gestión de perfiles de usuario
    - Rutas de administrador protegidas
    - Cambio de contraseñas seguro

    ### 📱 **Gestión de Productos**
    - **Categorías soportadas:** iPhone, Mac, iPad, Apple Watch, Accessories
    - **Especificaciones técnicas detalladas** por cada tipo de producto
    - **Filtros avanzados:** categoría, precio, stock, búsqueda de texto
    - **Endpoints públicos** para browsing y **endpoints admin** para gestión

    ### 🛠️ **Características Técnicas**
    - **Autenticación JWT** con tokens de 60 minutos
    - **Validación de datos** con Pydantic schemas
    - **Manejo de errores** consistente
    - **Paginación** en todas las listas
    - **Soft delete** y hard delete para productos
    - **Especificaciones JSON** para características complejas

    ### 🔑 **Autenticación**
    Para usar endpoints protegidos, incluir el token en headers:
    ```
    Authorization: Bearer <your_jwt_token>
    ```

    ### 📋 **Roles de Usuario**
    - **user**: Acceso a funciones básicas y gestión de perfil
    - **admin**: Acceso completo incluyendo gestión de productos y usuarios

    ---
    **Versión:** 1.0.0 | **Base URL:** `/` | **Documentación:** `/docs`
    """,
    version="1.0.0",
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "Apple Store API Support",
        "url": "https://example.com/contact/",
        "email": "support@applestore.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "users",
            "description": "🔐 **Gestión de usuarios y autenticación**. Operaciones para registro, login, gestión de perfiles y administración de usuarios.",
        },
        {
            "name": "products", 
            "description": "📱 **Gestión de productos Apple**. CRUD completo con especificaciones técnicas detalladas para iPhone, Mac, iPad, Apple Watch y Accessories.",
        },
        {
            "name": "💬 Chats",
            "description": "💬 **Sistema de chats y mensajería**. Gestión completa de conversaciones y mensajes entre usuarios y el sistema.",
        },
        {
            "name": "🤖 AI Agent System",
            "description": "🤖 **Sistema de agentes de IA con arquitectura de grafos**. Detección inteligente de intenciones, routing automático, agentes especializados (ventas, soporte, productos), tracking de costos en tiempo real, y soporte para múltiples proveedores (Gemini, OpenAI). Incluye integración con WhatsApp, chat web, y escalamiento automático.",
        },
        {
            "name": "migration",
            "description": "⚠️ **Endpoints temporales de migración**. Solo para desarrollo - eliminar en producción.",
        }
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#routers
app.include_router(productRoutes.router)
app.include_router(chatRoutes.router)
app.include_router(userRoutes.router)
app.include_router(agentRoutes.router)


@app.get(
    "/", 
    tags=["root"],
    summary="🏠 Endpoint de bienvenida",
    description="Endpoint raíz que proporciona información básica de la API y enlaces útiles."
)
def read_root():
    """
    Endpoint de bienvenida de la Apple Store API.
    Proporciona información básica y enlaces a la documentación.
    """
    return {
        "message": "🍎 Welcome to Apple Store Backend API",
        "version": "1.0.0",
        "status": "✅ Active",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints": {
            "users": "/users",
            "products": "/products", 
            "admin_products": "/products/admin",
            "migration": "/admin/migrate"
        },
        "features": [
            "🔐 JWT Authentication",
            "📱 Complete Product Management", 
            "👥 User Administration",
            "🛠️ Technical Specifications",
            "🔍 Advanced Filtering",
            "📄 Pagination Support"
        ]
    }

@app.get("/")
async def root():
    return {"message": "Apple Store Backend API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)