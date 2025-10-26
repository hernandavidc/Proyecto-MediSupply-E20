# Tests de Integración - User Service

Este directorio contiene los tests de integración para el User Service de MediSupply.

## Estructura

- `test_proveedor_routes.py`: Tests de integración para las rutas de proveedores
- `test_user_routes.py`: Tests de integración para las rutas de usuarios

## Requisitos

Los tests de integración requieren PostgreSQL ya que el modelo `Proveedor` utiliza tipos de PostgreSQL (`ARRAY`) que no son compatibles con SQLite.

## Ejecución Local

### Con PostgreSQL

```bash
# Asegúrate de tener PostgreSQL corriendo
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/users_db_test"
export SECRET_KEY="test_secret_key"

# Ejecutar todos los tests de integración
pytest tests/integration/ -v

# Ejecutar solo tests de proveedores
pytest tests/integration/test_proveedor_routes.py -v

# Ejecutar solo tests de usuarios
pytest tests/integration/test_user_routes.py -v
```

### Con Docker

```bash
# Iniciar PostgreSQL
docker run -d \
  --name test-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=users_db_test \
  -p 5432:5432 \
  postgres:15

# Ejecutar tests
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/users_db_test"
export SECRET_KEY="test_secret_key"
pytest tests/integration/ -v

# Limpiar
docker stop test-postgres && docker rm test-postgres
```

## GitHub Actions

Los tests de integración se ejecutan automáticamente en GitHub Actions con PostgreSQL 15 como servicio de base de datos.

## Tests Implementados

### Tests de Proveedores

1. **test_create_provider_success**: Creación exitosa de proveedor
2. **test_create_provider_invalid_data**: Validación de datos inválidos
3. **test_list_providers_empty**: Listar sin datos
4. **test_list_providers_with_data**: Listar con datos
5. **test_list_providers_pagination**: Paginación
6. **test_get_provider_by_id_success**: Obtener por ID exitoso
7. **test_get_provider_by_id_not_found**: Proveedor no encontrado
8. **test_update_provider_success**: Actualización exitosa
9. **test_delete_provider_success**: Eliminación exitosa
10. **test_provider_workflow_complete**: Flujo completo CRUD + auditoría

## Cobertura

Los tests de integración cubren:
- Endpoints completos de la API
- Validaciones de negocio
- Manejo de errores
- Auditoría de cambios
- Paginación y filtros
- Estados de proveedores

