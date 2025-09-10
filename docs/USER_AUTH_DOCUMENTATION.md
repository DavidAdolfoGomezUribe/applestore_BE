# Documentación del Sistema de Usuarios con JWT

## Características Implementadas

### 🔐 Autenticación y Seguridad
- **Contraseñas hasheadas** con bcrypt
- **Tokens JWT** para autenticación
- **Middleware de autenticación** para proteger rutas
- **Roles de usuario** (admin/user) con permisos diferenciados

### 👥 CRUD Completo de Usuarios

#### Rutas Públicas
- `POST /users/register` - Registro de nuevos usuarios
- `POST /users/login` - Inicio de sesión

#### Rutas Autenticadas (Usuario)
- `GET /users/me` - Obtener información del usuario actual
- `PUT /users/me` - Actualizar información del usuario actual
- `PUT /users/me/password` - Cambiar contraseña
- `DELETE /users/me` - Eliminar cuenta propia

#### Rutas de Administración (Solo Admins)
- `GET /users/` - Listar todos los usuarios (con paginación)
- `GET /users/count` - Obtener número total de usuarios
- `POST /users/` - Crear nuevo usuario
- `GET /users/{user_id}` - Obtener usuario por ID
- `PUT /users/{user_id}` - Actualizar usuario por ID
- `DELETE /users/{user_id}` - Eliminar usuario por ID

## Esquemas de Datos

### UserCreate
```json
{
  "name": "string (3-100 chars)",
  "email": "email@example.com",
  "password": "string (min 8 chars)",
  "role": "admin|user" // opcional, default: "user"
}
```

### UserLogin
```json
{
  "email": "email@example.com",
  "password": "string"
}
```

### TokenResponse
```json
{
  "access_token": "jwt_token_string",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Usuario",
    "email": "email@example.com",
    "role": "user"
  }
}
```

## Configuración

### Variables de Entorno Requeridas
```env
# Base de datos
MYSQL_HOST=localhost
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_DATABASE=applestore_db
MYSQL_PORT=3306

# JWT
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Dependencias Agregadas
```txt
passlib[bcrypt]          # Para hasheo de contraseñas
python-jose[cryptography] # Para JWT
python-multipart         # Para formularios
```

## Ejemplos de Uso

### 1. Registro de Usuario
```bash
curl -X POST "http://localhost:8000/users/register" \
-H "Content-Type: application/json" \
-d '{
  "name": "Juan Pérez",
  "email": "juan@example.com",
  "password": "mi_password_segura"
}'
```

### 2. Inicio de Sesión
```bash
curl -X POST "http://localhost:8000/users/login" \
-H "Content-Type: application/json" \
-d '{
  "email": "juan@example.com",
  "password": "mi_password_segura"
}'
```

### 3. Acceder a Rutas Protegidas
```bash
curl -X GET "http://localhost:8000/users/me" \
-H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 4. Cambiar Contraseña
```bash
curl -X PUT "http://localhost:8000/users/me/password" \
-H "Authorization: Bearer YOUR_JWT_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "current_password": "password_actual",
  "new_password": "nueva_password"
}'
```

## Usuarios de Prueba (Base de Datos)

### Administradores
- **Email:** ana.rodriguez@applestore.com - **Password:** admin123
- **Email:** carlos.mendoza@applestore.com - **Password:** admin456

### Usuarios Normales
- **Email:** beatriz.silva@gmail.com - **Password:** user123
- **Email:** david.gonzalez@outlook.com - **Password:** user456

## Seguridad Implementada

### Hasheo de Contraseñas
- Uso de **bcrypt** con salt rounds = 12
- Las contraseñas nunca se almacenan en texto plano
- Verificación segura durante el login

### JWT (JSON Web Tokens)
- Tokens firmados con HS256
- Expiración configurable (default: 30 minutos)
- Información del usuario en el payload

### Autorización por Roles
- **Usuarios normales:** Solo pueden gestionar su propia cuenta
- **Administradores:** Acceso completo a todas las operaciones CRUD

### Validaciones
- Emails únicos en el sistema
- Contraseñas de mínimo 8 caracteres
- Validación de formato de email
- Verificación de contraseña actual para cambios

## Estructura de Archivos

```
app/
├── auth/
│   ├── __init__.py
│   ├── auth_utils.py      # Utilidades JWT y hasheo
│   └── auth_middleware.py # Middleware de autenticación
├── routes/user/
│   └── userRoutes.py     # Rutas de usuarios (renovadas)
├── schemas/user/
│   └── userSchemas.py    # Esquemas Pydantic (renovados)
├── services/user/
│   └── userService.py    # Lógica de negocio (renovada)
└── main.py              # App principal (actualizada)
```

## Mantenimiento de Compatibilidad

Se mantuvieron rutas legacy para compatibilidad:
- `POST /users/legacy`
- `GET /users/legacy/{user_id}`
- `PUT /users/legacy/{user_id}`
- `DELETE /users/legacy/{user_id}`

**Recomendación:** Migrar a las nuevas rutas autenticadas lo antes posible.
