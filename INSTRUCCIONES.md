# Instrucciones para levantar y administrar el proyecto AppleStore Backend

## 1. Requisitos previos
- Docker y Docker Compose instalados
- Archivo `.env` configurado (usar `.env.example` como base)

## 2. Estructura de contenedores
El proyecto usa tres contenedores independientes:
- **backend**: API FastAPI (puerto 8000)
- **mysql**: Base de datos MySQL (puerto 3307)
- **qdrant**: Base de datos vectorial Qdrant (puerto 6333)

## 3. Levantar todos los servicios

### Opción 1: Modo interactivo (ver logs en tiempo real)
```bash
docker compose up --build
```

### Opción 2: Modo detach (en segundo plano)
```bash
docker compose up --build -d
```

### Verificar que todos los servicios estén corriendo
```bash
docker compose ps
```

## 4. Acceder a la consola de cada contenedor

### Backend (FastAPI)
```bash
docker compose exec backend bash
```

### MySQL
```bash
docker compose exec mysql bash
```

### Conectar al cliente MySQL desde dentro del contenedor
```bash
docker compose exec mysql mysql -u applestore_user -p$MYSQL_PASSWORD applestore_db
```

### Conectar a MySQL desde tu máquina local
```bash
mysql -h localhost -P 3307 -u applestore_user -p applestore_db
```

### Qdrant
```bash
docker compose exec qdrant bash
```

## 5. Carga de datos y base de conocimiento (KB)

### Datos iniciales de MySQL
Los datos se cargan automáticamente al crear el contenedor:
- `app/data/mysql/1-schema.sql`: Estructura de tablas
- `app/data/mysql/2-data.sql`: Datos iniciales (usuarios, productos, ventas)

### Cargar base de conocimiento vectorial en Qdrant
```bash
# Desde fuera del contenedor
docker compose exec backend python data/qdrant/load_kb.py
docker compose exec backend python data/qdrant/verify_kb.py
# O desde dentro del contenedor backend
docker compose exec backend bash
python data/load_kb.py
```

Este script:
1. Extrae productos de MySQL
2. Genera embeddings usando sentence-transformers
3. Los carga en Qdrant como vectores

## 6. Verificar que todo funcione

### API Backend
```bash
curl http://localhost:8000/health
# Respuesta esperada: {"status":"healthy"}
```

### Qdrant
```bash
curl http://localhost:6333/health
# Debería responder sin errores
```

### MySQL (desde terminal)
```bash
docker compose exec mysql mysql -u applestore_user -p$MYSQL_PASSWORD -e "USE applestore_db; SELECT COUNT(*) FROM products;"
```

## 7. Comandos útiles

### Ver logs de servicios
```bash
docker compose logs backend
docker compose logs mysql
docker compose logs qdrant

# Logs en tiempo real
docker compose logs -f backend
```

### Reiniciar un servicio específico
```bash
docker compose restart backend
docker compose restart mysql
docker compose restart qdrant
```

### Limpiar todo y empezar desde cero
```bash
docker compose down -v
docker compose up --build
```

### Parar servicios
```bash
docker compose down
```

### Parar servicios y eliminar volúmenes (borra todos los datos)
```bash
docker compose down -v
```

## 8. Variables de entorno importantes

Asegúrate de tener estas variables en tu archivo `.env`:

```bash
# MySQL
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=applestore_db
MYSQL_USER=applestore_user
MYSQL_PASSWORD=applestore_password
MYSQL_HOST=mysql

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Aplicación
DEBUG=True
SECRET_KEY=your-secret-key-here
```

## 9. Estructura de datos

### Tablas en MySQL
- `users`: Usuarios (admins y users)
- `products`: Productos Apple
- `sales`: Ventas
- `sales_products`: Relación productos-ventas
- `chats`: Conversaciones
- `messages`: Mensajes de chats

### Colección en Qdrant
- `products_kb`: Embeddings de productos para búsqueda semántica

---

## Troubleshooting

### Si MySQL no inicia correctamente
```bash
docker compose logs mysql
```
Verifica que los archivos SQL en `app/data/mysql/` sean válidos.

### Si la carga de KB falla
Asegúrate de que MySQL esté completamente iniciado antes de ejecutar `load_kb.py`.

### Si hay problemas de permisos
```bash
sudo chown -R $USER:$USER .
```
