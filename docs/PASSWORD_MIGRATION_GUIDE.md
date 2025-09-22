# Solución para Contraseñas Hasheadas Automáticamente

#### Pasos:
1. **Ejecutar migración**:
   ```bash
   curl -X POST "http://localhost:8000/admin/migrate/hash-passwords"
   ```

2. **Verificar que funciona**:
   ```bash
   curl -X GET "http://localhost:8000/admin/migrate/verify-passwords"
   ```

3. **Probar login**:
   ```bash
   curl -X POST "http://localhost:8000/users/login" \
   -H "Content-Type: application/json" \
   -d '{
     "email": "ana.rodriguez@applestore.com",
     "password": "admin123"
   }'
   ```

#### ⚠️ **IMPORTANTE**: Eliminar el router de migración en producción:
- Comentar la línea en `main.py`: `app.include_router(migration_router)`
- O eliminar el archivo `routes/migration/migrationRoutes.py`

---

### **Opción 2: Script de Base de Datos**

Ejecutar dentro del contenedor Docker:
```bash
docker exec -it applestore_be-backend-1 python3 /app/scripts/migrate_passwords.py
```

---

### **Opción 3: Manual SQL**

Ejecutar en la base de datos MySQL:
```sql
-- Generar hashes y ejecutar estos UPDATEs manualmente
UPDATE users SET password = 'HASH_GENERADO' WHERE email = 'ana.rodriguez@applestore.com';
-- Repetir para cada usuario...
```

---

## 🎯 **Credenciales Válidas Después de la Migración**

| Email | Password | Rol |
|-------|----------|-----|
| ana.rodriguez@applestore.com | admin123 | ADMIN |
| carlos.mendoza@applestore.com | admin456 | ADMIN |
| beatriz.silva@gmail.com | user123 | USER |
| david.gonzalez@outlook.com | user456 | USER |

---

## 🔄 **Para Futuros Deployments**

### **Mejora Arquitectónica**: 
En lugar de hashes pre-generados en SQL, usar un script de inicialización:

1. **Crear `init_users.py`**:
   ```python
   from auth.auth_utils import hash_password
   from services.user.userService import create_user_db
   
   def init_default_users():
       users = [
           ("admin", "Ana Rodríguez", "ana.rodriguez@applestore.com", "admin123"),
           ("admin", "Carlos Mendoza", "carlos.mendoza@applestore.com", "admin456"),
           ("user", "Beatriz Silva", "beatriz.silva@gmail.com", "user123"),
           ("user", "David González", "david.gonzalez@outlook.com", "user456")
       ]
       
       for role, name, email, password in users:
           create_user_db(name, email, password, role)
   ```

2. **Ejecutar al inicializar la aplicación**:
   ```python
   # En main.py o en un script de startup
   @app.on_event("startup")
   async def startup_event():
       init_default_users()
   ```

---

## 📁 **Archivos Creados**

1. `routes/migration/migrationRoutes.py` - Endpoints temporales
2. `scripts/migrate_passwords.py` - Script de migración DB
3. `scripts/generate_hashed_passwords.py` - Generador de SQL
4. `scripts/update_passwords_sql.py` - Actualizador de archivo SQL
5. `scripts/fix_passwords.py` - Información y ayuda

---

## 🚀 **Prueba Rápida**

```bash
# 1. Migrar contraseñas
curl -X POST "http://localhost:8000/admin/migrate/hash-passwords"

# 2. Login con admin
curl -X POST "http://localhost:8000/users/login" \
-H "Content-Type: application/json" \
-d '{"email": "ana.rodriguez@applestore.com", "password": "admin123"}'

# 3. Usar el token para acceder a rutas protegidas
curl -X GET "http://localhost:8000/users/me" \
-H "Authorization: Bearer TU_TOKEN_JWT"
```

**¡Listo!** Las contraseñas se hashean automáticamente y el sistema funciona correctamente.
