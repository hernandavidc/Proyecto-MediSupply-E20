# 🧪 Estructura de Tests - MediSupply Supplier Service

## 📁 Organización de Tests

Los tests están organizados por tipo para facilitar el mantenimiento y la ejecución selectiva:

```
tests/
├── unit/                    # Tests unitarios
│   ├── test_carga_masiva.py
│   ├── test_product.py
│   ├── test_service.py
│   ├── test_schemas.py
│   ├── test_vendedor.py
│   └── test_plan.py
├── integration/             # Tests de integración
│   └── test_integracion_carga_masiva.py
├── e2e/                    # Tests end-to-end
│   └── test_smoke.py
└── conftest.py            # Configuración compartida
```

## 🎯 Tipos de Tests

### **Unit Tests** (`tests/unit/`)
- **Propósito**: Probar componentes individuales de forma aislada
- **Características**: 
  - Rápidos de ejecutar
  - No dependen de servicios externos
  - Usan mocks/stubs cuando es necesario
  - Base de datos en memoria
- **Ejemplos**: Validaciones, servicios individuales, esquemas

### **Integration Tests** (`tests/integration/`)
- **Propósito**: Probar la integración entre múltiples componentes
- **Características**:
  - Usan TestClient de FastAPI
  - Prueban flujos completos HTTP
  - Verifican persistencia en base de datos
  - Incluyen validaciones de negocio
- **Ejemplos**: Carga masiva completa, flujos de API

### **End-to-End Tests** (`tests/e2e/`)
- **Propósito**: Probar flujos completos del sistema
- **Características**:
  - Tests de humo (smoke tests)
  - Verifican que el sistema funciona end-to-end
  - Pueden usar servicios externos
- **Ejemplos**: Health checks, flujos críticos

## 🚀 Comandos de Ejecución

### **Scripts de Conveniencia**
```bash
# Tests unitarios
./run-unit-tests.sh

# Tests de integración
./run-integration-tests.sh

# Tests end-to-end
./run-e2e-tests.sh

# Todos los tests
./run-all-tests.sh
```

### **Comandos Pytest Directos**
```bash
# Por tipo de test
python -m pytest tests/unit/ -v -m "unit"
python -m pytest tests/integration/ -v -m "integration"
python -m pytest tests/e2e/ -v -m "e2e"

# Por marcador específico
python -m pytest -v -m "unit"
python -m pytest -v -m "integration"
python -m pytest -v -m "smoke"

# Con cobertura
python -m pytest tests/ --cov=app --cov-report=html

# Tests específicos
python -m pytest tests/unit/test_carga_masiva.py -v
python -m pytest tests/integration/test_integracion_carga_masiva.py -v
```

## 📊 Marcadores de Tests

Los tests están marcados para facilitar la ejecución selectiva:

- `@pytest.mark.unit`: Tests unitarios
- `@pytest.mark.integration`: Tests de integración  
- `@pytest.mark.e2e`: Tests end-to-end
- `@pytest.mark.smoke`: Tests de humo
- `@pytest.mark.slow`: Tests que tardan más tiempo

## 🔧 Configuración

### **pytest.ini**
- Configuración centralizada de pytest
- Marcadores definidos
- Opciones de cobertura
- Configuración de reportes

### **conftest.py**
- Fixtures compartidas entre tests
- Configuración de base de datos de prueba
- Setup/teardown común

## 📈 Cobertura de Tests

El proyecto mantiene una cobertura mínima del 80%:
- Reportes en terminal y HTML
- Cobertura por módulo
- Identificación de líneas no cubiertas

## 🎯 Mejores Prácticas

### **Naming Convention**
- Archivos: `test_*.py`
- Clases: `Test*`
- Funciones: `test_*`

### **Estructura de Tests**
```python
def test_descripcion_del_comportamiento():
    # Arrange - Preparar datos
    # Act - Ejecutar acción
    # Assert - Verificar resultado
```

### **Fixtures**
- Usar fixtures para setup común
- Fixtures con scope apropiado (function, class, module)
- Fixtures parametrizadas cuando sea necesario

### **Aislamiento**
- Cada test debe ser independiente
- Limpiar estado entre tests
- Usar base de datos en memoria para tests unitarios

## 🚨 Troubleshooting

### **Tests que fallan**
1. Verificar que las dependencias estén instaladas
2. Revisar la configuración de base de datos
3. Verificar que los marcadores estén correctos

### **Problemas de cobertura**
1. Ejecutar con `--cov=app` para ver cobertura detallada
2. Revisar reporte HTML en `htmlcov/index.html`
3. Identificar módulos con baja cobertura

### **Tests lentos**
1. Marcar tests lentos con `@pytest.mark.slow`
2. Ejecutar solo tests rápidos: `pytest -m "not slow"`
3. Optimizar fixtures y setup
