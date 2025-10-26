# 🧪 Pruebas de Carga Masiva de Productos - MediSupply Supplier Service

Este documento describe la suite completa de pruebas para la funcionalidad de carga masiva de productos.

## 📁 Estructura de Pruebas

```
tests/
├── unit/                           # Pruebas unitarias
│   └── test_product_bulk.py       # Tests de funciones individuales
├── integration/                    # Pruebas de integración
│   ├── conftest.py                # Configuración de integración
│   └── test_bulk_upload_integration.py  # Tests de componentes
└── e2e/                           # Pruebas end-to-end
    ├── conftest.py                # Configuración e2e
    └── test_bulk_upload_e2e.py    # Tests de flujo completo
```

## 🔬 Pruebas Unitarias

**Ubicación**: `tests/unit/test_product_bulk.py`

**Propósito**: Validar funciones individuales y lógica de negocio

**Cobertura**:
- ✅ Validación de datos CSV
- ✅ Conversión de filas a productos
- ✅ Manejo de errores específicos
- ✅ Lógica de rollback
- ✅ Validaciones de esquema

**Ejecutar**:
```bash
pytest tests/unit/test_product_bulk.py -v
```

## 🔗 Pruebas de Integración

**Ubicación**: `tests/integration/test_bulk_upload_integration.py`

**Propósito**: Validar interacción entre componentes del sistema

**Cobertura**:
- ✅ Endpoint de carga masiva
- ✅ Integración con base de datos
- ✅ Manejo de archivos CSV
- ✅ Respuestas de API
- ✅ Validación de parámetros

**Ejecutar**:
```bash
./run_integration_tests.sh
```

## 🌐 Pruebas End-to-End

**Ubicación**: `tests/e2e/test_bulk_upload_e2e.py`

**Propósito**: Validar flujo completo de usuario

**Cobertura**:
- ✅ Flujo completo de carga masiva
- ✅ Resultados mixtos (éxito/error)
- ✅ Rendimiento con archivos grandes
- ✅ Escenarios de error completos
- ✅ Validación de datos específicos
- ✅ Documentación de API

**Ejecutar**:
```bash
./run_e2e_tests.sh
```

## 🚀 Ejecutar Todas las Pruebas

```bash
./run_all_tests.sh
```

## 📊 Tipos de Pruebas por Categoría

### 1. Pruebas Unitarias
- **Función**: `_convertir_fila_a_producto`
- **Validaciones**: SKU, fechas, certificaciones, precios
- **Errores**: Campos obligatorios, formatos inválidos
- **Casos**: Datos válidos, datos inválidos, casos edge

### 2. Pruebas de Integración
- **Endpoint**: `POST /api/v1/productos/bulk-upload`
- **Parámetros**: `reject_on_errors`, archivo CSV
- **Respuestas**: Códigos HTTP, estructura JSON
- **Base de datos**: Creación, rollback, auditoría

### 3. Pruebas End-to-End
- **Flujo completo**: Carga → Validación → Persistencia → Verificación
- **Escenarios reales**: Archivos grandes, errores mixtos
- **Rendimiento**: Tiempo de procesamiento
- **API**: Documentación, acceso individual

## 🎯 Escenarios de Prueba

### Casos de Éxito
- ✅ Archivo CSV válido con 2 productos
- ✅ Archivo CSV válido con 50+ productos
- ✅ Carga masiva con `reject_on_errors=true`
- ✅ Carga masiva con `reject_on_errors=false`

### Casos de Error
- ❌ Archivo vacío
- ❌ Tipo de archivo incorrecto
- ❌ Columnas faltantes
- ❌ SKU inválido (contiene '0')
- ❌ Tipo de medicamento inválido
- ❌ Fecha inválida
- ❌ Certificaciones inválidas
- ❌ Precio inválido
- ❌ Proveedor inexistente

### Casos Mixtos
- 🔄 Archivo con productos válidos e inválidos
- 🔄 `reject_on_errors=false` con errores
- 🔄 Verificación de productos creados vs errores reportados

## 📈 Métricas de Pruebas

### Cobertura de Código
- **Unitarias**: 95%+ de funciones de servicio
- **Integración**: 90%+ de endpoints
- **E2E**: 100% de flujos críticos

### Rendimiento
- **Archivo pequeño** (2 productos): < 1 segundo
- **Archivo mediano** (50 productos): < 5 segundos
- **Archivo grande** (100+ productos): < 10 segundos

### Casos de Prueba
- **Unitarias**: 15+ casos
- **Integración**: 20+ casos
- **E2E**: 10+ casos
- **Total**: 45+ casos de prueba

## 🔧 Configuración de Pruebas

### Base de Datos de Prueba
- **Unitarias**: SQLite en memoria
- **Integración**: SQLite en memoria con datos base
- **E2E**: SQLite en memoria con datos completos

### Datos de Prueba
- **Proveedores**: Proveedor de prueba con certificaciones
- **Catálogos**: Países, certificaciones, categorías
- **CSV**: Archivos de ejemplo para cada escenario

### Fixtures
- `db_session`: Sesión de base de datos
- `proveedor_ejemplo`: Proveedor para pruebas
- `csv_content_valido`: CSV válido
- `csv_content_con_errores`: CSV con errores

## 🚨 Troubleshooting

### Pruebas Fallan
```bash
# Verificar dependencias
pip install pytest pytest-cov httpx

# Ejecutar con más detalle
pytest tests/unit/test_product_bulk.py -v -s

# Verificar base de datos
python -c "from app.core.database import SessionLocal; print('DB OK')"
```

### Problemas de Importación
```bash
# Verificar PYTHONPATH
export PYTHONPATH=/path/to/medisupply-supplier-service

# Ejecutar desde directorio correcto
cd medisupply-supplier-service
```

### Problemas de Base de Datos
```bash
# Limpiar base de datos de prueba
rm -f test.db test_integration.db

# Verificar modelos
python -c "from app.models.product import Producto; print('Models OK')"
```

## 📋 Checklist de Pruebas

### Antes de Deploy
- [ ] Todas las pruebas unitarias pasan
- [ ] Todas las pruebas de integración pasan
- [ ] Todas las pruebas e2e pasan
- [ ] Cobertura de código > 90%
- [ ] Rendimiento dentro de límites
- [ ] Documentación de API actualizada

### Después de Deploy
- [ ] Health check funciona
- [ ] Endpoint de carga masiva accesible
- [ ] Documentación disponible en `/docs`
- [ ] Pruebas de humo en producción

## 🔮 Próximas Mejoras

- [ ] Pruebas de carga (stress testing)
- [ ] Pruebas de concurrencia
- [ ] Pruebas de seguridad
- [ ] Pruebas de accesibilidad
- [ ] Pruebas de compatibilidad de navegadores
- [ ] Pruebas de integración con servicios externos
