# Testing Documentation - Order Service

Este documento describe la estructura de pruebas y cómo ejecutarlas para el Order Service de MediSupply.

## Estructura de Pruebas

```
tests/
├── conftest.py                          # Fixtures compartidas (db_session, client)
├── __init__.py
├── unit/                                # Pruebas unitarias
│   ├── __init__.py
│   ├── test_smoke.py                    # Smoke tests básicos
│   └── test_auth.py                     # Tests de autenticación
├── integration/                         # Pruebas de integración
│   ├── __init__.py
│   ├── conftest.py                      # Fixtures de integración
│   └── test_orden_integration.py        # Integración entre módulos
├── e2e/                                 # Pruebas end-to-end
│   ├── __init__.py
│   ├── conftest.py                      # Fixtures e2e
│   └── test_orden_workflow_e2e.py       # Flujos completos
├── test_orden_service.py                # Tests del servicio de órdenes
├── test_orden_routes.py                 # Tests de rutas de órdenes
├── test_bodega_vehiculo_routes.py       # Tests de bodegas y vehículos
└── test_novedad_routes.py               # Tests de novedades
```

## Tipos de Pruebas

### 1. Pruebas Unitarias (`tests/unit/`)
Prueban componentes individuales en aislamiento:
- **test_smoke.py**: Verificaciones básicas de endpoints
- **test_auth.py**: Autenticación y autorización

### 2. Pruebas de Servicios (raíz de `tests/`)
Prueban la lógica de negocio en los servicios:
- **test_orden_service.py**: CRUD de órdenes, filtros, validaciones
- **test_orden_routes.py**: Endpoints HTTP de órdenes
- **test_bodega_vehiculo_routes.py**: Endpoints de bodegas y vehículos
- **test_novedad_routes.py**: Endpoints de novedades

### 3. Pruebas de Integración (`tests/integration/`)
Prueban la interacción entre múltiples componentes:
- **test_orden_integration.py**: Órdenes con vehículos, ciclo de vida completo

### 4. Pruebas End-to-End (`tests/e2e/`)
Prueban flujos completos del sistema:
- **test_orden_workflow_e2e.py**: Flujo completo desde creación hasta entrega

## Ejecutar Pruebas

### Todas las pruebas
```bash
./run_all_tests.sh
```

### Solo pruebas unitarias
```bash
./run_unit_tests.sh
```

### Solo pruebas de integración
```bash
./run_integration_tests.sh
```

### Solo pruebas end-to-end
```bash
./run_e2e_tests.sh
```

### Ejecutar pruebas específicas
```bash
pytest tests/test_orden_service.py -v
pytest tests/unit/test_smoke.py::test_root_endpoint -v
```

### Con cobertura
```bash
pytest --cov=app --cov-report=html
```

## Fixtures Disponibles

### `db_session`
Sesión de base de datos SQLite en memoria para cada test.
```python
def test_example(db_session):
    # db_session es una sesión SQLAlchemy
    orden = Orden(...)
    db_session.add(orden)
    db_session.commit()
```

### `client`
Cliente de prueba de FastAPI con base de datos compartida.
```python
def test_example(client):
    response = client.get("/api/v1/ordenes")
    assert response.status_code == 200
```

### `integration_db`
Base de datos para pruebas de integración (archivo temporal).

### `e2e_client`
Cliente para pruebas end-to-end con base de datos persistente.

## Cobertura de Pruebas

Los tests cubren:
- ✅ CRUD completo de órdenes
- ✅ Gestión de bodegas
- ✅ Gestión de vehículos
- ✅ Registro de novedades
- ✅ Filtros y búsquedas
- ✅ Validaciones de negocio
- ✅ Autenticación y autorización
- ✅ Ciclo de vida de órdenes (ABIERTO → ENTREGADO)
- ✅ Relaciones entre entidades
- ✅ Flujos end-to-end completos

## Configuración

Las pruebas utilizan:
- **SQLite en memoria** para pruebas rápidas
- **AUTH_DISABLED=true** para evitar dependencias externas
- **pytest.ini** para configuración global
- **conftest.py** para fixtures compartidas

## Reportes

Después de ejecutar las pruebas:
- **HTML**: `htmlcov/index.html` - Reporte visual de cobertura
- **Terminal**: Muestra resumen de cobertura
- **XML**: `coverage.xml` - Para herramientas CI/CD

## Mejores Prácticas

1. **Aislamiento**: Cada test debe ser independiente
2. **Claridad**: Nombres descriptivos (test_what_when_expected)
3. **Arrange-Act-Assert**: Estructura clara en 3 partes
4. **Fixtures**: Reutilizar configuración común
5. **Markers**: Usar @pytest.mark para categorizar

## CI/CD

Las pruebas se ejecutan automáticamente en:
- Pull requests
- Commits a main/develop
- Antes de despliegues a producción

## Troubleshooting

### "No module named pytest"
```bash
pip install -r requirements.txt
```

### "Database is locked"
Las pruebas usan bases de datos separadas, pero si ocurre:
```bash
rm -f test*.db
```

### "Import error"
Asegúrate de estar en el directorio correcto:
```bash
cd medisupply-order-service
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

