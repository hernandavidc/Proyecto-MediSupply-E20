medisupply-supplier-service

Microservicio que implementa HU-001 - Registro de proveedores.

Estructura:
- app/main.py
- app/core (config, database, dependencies)
- app/models (Proveedor, ProveedorAuditoria, catalogs)
- app/schemas (Pydantic schemas)
- app/services (business logic)
- app/api/v1 (routes)

Endpoints relevantes (ruta base `/api/v1`):
- GET /paises
- GET /certificaciones
- GET /categorias-suministros
- GET /proveedores
- POST /proveedores
- GET /proveedores/{id}
- PUT /proveedores/{id}
- DELETE /proveedores/{id}

Uso local rápido:
- Copiar `.env.example` a `.env` y ajustar `DATABASE_URL`.
- docker build -t medisupply-supplier-service .
- docker run -p 8002:8000 --env-file .env medisupply-supplier-service

