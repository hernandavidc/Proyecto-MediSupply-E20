# Guía de Uso del API Gateway

## Descripción

El API Gateway (Nginx) unifica todos los servicios de MediSupply en **un solo puerto: 8080**.

## Iniciar el Gateway

```bash
# Iniciar todos los servicios incluyendo el gateway
docker-compose up -d

# Ver logs del gateway
docker-compose logs -f api-gateway

# Verificar que está funcionando
curl http://localhost:8080/health
```

## Endpoints Unificados

### 🔑 User Service (Autenticación)

**Base URL:** `http://localhost:8080/users/`

```bash
# Registrar usuario
curl -X POST http://localhost:8080/users/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'

# Generar token
curl -X POST http://localhost:8080/users/api/v1/users/generate-token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Ver información del usuario actual
curl http://localhost:8080/users/api/v1/users/me \
  -H "Authorization: Bearer TU_TOKEN"

# Health check
curl http://localhost:8080/users/health
```

### 📦 Supplier Service (Proveedores)

**Base URL:** `http://localhost:8080/suppliers/`

```bash
# Listar países
curl http://localhost:8080/suppliers/api/v1/paises \
  -H "Authorization: Bearer TU_TOKEN"

# Listar certificaciones
curl http://localhost:8080/suppliers/api/v1/certificaciones \
  -H "Authorization: Bearer TU_TOKEN"

# Listar categorías de suministros
curl http://localhost:8080/suppliers/api/v1/categorias-suministros \
  -H "Authorization: Bearer TU_TOKEN"

# Listar proveedores
curl http://localhost:8080/suppliers/api/v1/proveedores \
  -H "Authorization: Bearer TU_TOKEN"

# Listar productos
curl http://localhost:8080/suppliers/api/v1/productos \
  -H "Authorization: Bearer TU_TOKEN"

# Crear proveedor
curl -X POST http://localhost:8080/suppliers/api/v1/proveedores \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN" \
  -d '{
    "razon_social": "Mi Empresa S.A.",
    "paises_operacion": [1, 2],
    "certificaciones_sanitarias": [1, 3],
    "categorias_suministradas": [1, 2],
    "capacidad_cadena_frio": ["2-8°C"],
    "estado": "PENDIENTE"
  }'

# Documentación Swagger
# http://localhost:8080/suppliers/supplier-docs

# Health check
curl http://localhost:8080/suppliers/healthz
```

### 🏥 Client Service (Clientes)

**Base URL:** `http://localhost:8080/clients/`

```bash
# Crear cliente
curl -X POST http://localhost:8080/clients/api/v1/clientes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN" \
  -d '{
    "nombre": "Hospital San José",
    "nit": "9001234567",
    "direccion": "Calle 123 #45-67, Bogotá, Colombia",
    "nombre_contacto": "María González",
    "telefono_contacto": "3101234567",
    "email_contacto": "contacto@hospitalsanjose.com"
  }'

# Listar clientes
curl "http://localhost:8080/clients/api/v1/clientes?page=1&page_size=10" \
  -H "Authorization: Bearer TU_TOKEN"

# Obtener cliente por ID
curl http://localhost:8080/clients/api/v1/clientes/UUID_CLIENTE \
  -H "Authorization: Bearer TU_TOKEN"

# Validar NIT
curl http://localhost:8080/clients/api/v1/clientes/validate-nit/9001234567

# Documentación Swagger
# http://localhost:8080/clients/docs

# Health check
curl http://localhost:8080/clients/health
```

## Ejemplo Completo: Flujo de Trabajo

```bash
# 1. Registrar usuario
curl -X POST http://localhost:8080/users/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Admin",
    "email": "admin@medisupply.com",
    "password": "admin123"
  }'

# 2. Obtener token
TOKEN=$(curl -X POST http://localhost:8080/users/api/v1/users/generate-token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@medisupply.com",
    "password": "admin123"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"

# 3. Listar países (supplier-service)
curl http://localhost:8080/suppliers/api/v1/paises \
  -H "Authorization: Bearer $TOKEN"

# 4. Crear cliente (client-service)
curl -X POST http://localhost:8080/clients/api/v1/clientes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "nombre": "Hospital General",
    "nit": "9007654321",
    "direccion": "Av. Principal 456",
    "nombre_contacto": "Dr. Pérez",
    "telefono_contacto": "3209876543",
    "email_contacto": "info@hospitalgeneral.com"
  }'

# 5. Ver mi información de usuario
curl http://localhost:8080/users/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

## Ventajas del API Gateway

✅ **Un solo puerto (8080)** para todos los servicios  
✅ **Rutas organizadas** por servicio (`/users/`, `/suppliers/`, `/clients/`)  
✅ **CORS configurado** automáticamente  
✅ **Health checks** unificados  
✅ **Fácil de escalar** agregando más servicios

## Documentación Swagger

- **User Service:** http://localhost:8080/users/docs
- **Supplier Service:** http://localhost:8080/suppliers/supplier-docs
- **Client Service:** http://localhost:8080/clients/docs

## Comparación: Antes vs Después

### ❌ Antes (Sin Gateway)
```bash
# Múltiples puertos
curl http://localhost:8001/api/v1/users/me      # User
curl http://localhost:8010/api/v1/paises        # Supplier
curl http://localhost:8002/api/v1/clientes      # Client
```

### ✅ Después (Con Gateway)
```bash
# Un solo puerto
curl http://localhost:8080/users/api/v1/users/me
curl http://localhost:8080/suppliers/api/v1/paises
curl http://localhost:8080/clients/api/v1/clientes
```

## Troubleshooting

### El gateway no responde
```bash
# Verificar que está corriendo
docker ps | grep api-gateway

# Ver logs
docker-compose logs api-gateway

# Reiniciar
docker-compose restart api-gateway
```

### Error 502 Bad Gateway
```bash
# Verificar que todos los servicios están arriba
docker-compose ps

# Reiniciar servicios
docker-compose restart medisupply-user-service medisupply-supplier-service medisupply-client-service
```

### Cambios en nginx.conf no se aplican
```bash
# Reiniciar el gateway después de modificar nginx.conf
docker-compose restart api-gateway

# O recargar la configuración sin reiniciar
docker exec medisupply-api-gateway nginx -s reload
```

## Acceso Directo (Sin Gateway)

Los servicios individuales siguen accesibles en sus puertos originales:
- User Service: http://localhost:8001
- Supplier Service: http://localhost:8010
- Client Service: http://localhost:8002

Esto es útil para desarrollo y debugging.
