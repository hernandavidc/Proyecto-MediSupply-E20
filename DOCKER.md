# User Service - Docker Setup

## 🐳 Ejecutar con Docker Compose

### Prerrequisitos
- Docker
- Docker Compose

### Comandos Rápidos

**Iniciar servicios:**
```bash
docker-compose up -d
```

**Ver logs:**
```bash
docker-compose logs -f user-service
```

**Parar servicios:**
```bash
docker-compose down
```

### Servicios Incluidos

1. **user-service** (Puerto 8001)
   - Microservicio FastAPI
   - Autenticación JWT
   - Health check
   
2. **user-db** (Puerto 5433)
   - PostgreSQL 15
   - Base de datos: `users_db`
   - Usuario: `user`
   - Password: `password`

### Endpoints Disponibles

- **API:** http://localhost:8001
- **Docs:** http://localhost:8001/docs
- **Health:** http://localhost:8001/health
- **Database:** localhost:5433

### Variables de Entorno

```env
DATABASE_URL=postgresql://user:password@user-db:5432/users_db
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=true
```

### Comandos de Desarrollo

```bash
# Construir imágenes
docker-compose build

# Iniciar en modo desarrollo
docker-compose up

# Ver estado de servicios
docker-compose ps

# Acceder al contenedor
docker-compose exec user-service bash

# Acceder a la base de datos
docker-compose exec user-db psql -U user -d users_db

# Reiniciar servicio específico
docker-compose restart user-service

# Limpiar todo
docker-compose down -v
```

### Health Checks

Los servicios incluyen health checks automáticos:

- **user-service:** Verifica que el endpoint `/health` responda
- **user-db:** Verifica conexión PostgreSQL

### Estructura Docker

```
proyecto-maestria/
├── docker-compose.yml          # Configuración principal
├── user-service/
│   ├── Dockerfile             # Imagen del microservicio
│   ├── start.sh              # Script de inicio
│   ├── .dockerignore         # Archivos ignorados
│   └── app/                  # Código fuente
└── dev.sh                    # Scripts de desarrollo
```

### Desarrollo

Para desarrollo activo:

1. **Modificar código:** Los cambios se reflejan automáticamente
2. **Ver logs:** `docker-compose logs -f user-service`
3. **Reiniciar:** `docker-compose restart user-service`

### Testing API

```bash
# Registrar usuario
curl -X POST "http://localhost:8001/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Login
curl -X POST "http://localhost:8001/api/v1/users/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```
