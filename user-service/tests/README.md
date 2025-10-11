# Tests para User Service

Este directorio contiene la suite completa de tests para el servicio de usuarios.

## Estructura de Tests

```
tests/
├── __init__.py                    # Configuración del paquete de tests
├── conftest.py                    # Fixtures compartidas y configuración de pytest
├── pytest.ini                    # Configuración de pytest
├── unit/                          # Tests unitarios
│   ├── __init__.py
│   ├── test_auth.py              # Tests para funciones de autenticación
│   ├── test_models.py            # Tests para modelos de base de datos
│   ├── test_schemas.py           # Tests para schemas de Pydantic
│   └── test_user_service.py      # Tests para la lógica de negocio
└── integration/                   # Tests de integración
    ├── __init__.py
    └── test_user_routes.py       # Tests para endpoints de API
```

## Tipos de Tests

### Tests Unitarios
- **test_auth.py**: Tests para funciones de hash de contraseñas y tokens JWT
- **test_models.py**: Tests para el modelo User de SQLAlchemy
- **test_schemas.py**: Tests para validación de datos con Pydantic
- **test_user_service.py**: Tests para la lógica de negocio del UserService

### Tests de Integración
- **test_user_routes.py**: Tests end-to-end para los endpoints de la API

## Ejecutar Tests

### Prerequisitos
```bash
# Instalar todas las dependencias (producción + testing)
pip install -r requirements.txt
```

### Ejecutar todos los tests
```bash
pytest
```

### Ejecutar solo tests unitarios
```bash
pytest tests/unit/
```

### Ejecutar solo tests de integración
```bash
pytest tests/integration/
```

### Ejecutar con coverage
```bash
pytest --cov=app --cov-report=html
```

### Ejecutar tests específicos
```bash
# Por archivo
pytest tests/unit/test_auth.py

# Por clase
pytest tests/unit/test_auth.py::TestPasswordHashing

# Por método específico
pytest tests/unit/test_auth.py::TestPasswordHashing::test_verify_password_with_correct_password
```

### Opciones útiles
```bash
# Ejecutar con output verbose
pytest -v

# Ejecutar con output detallado
pytest -vv

# Parar en el primer error
pytest -x

# Ejecutar tests en paralelo (requiere pytest-xdist)
pytest -n auto

# Ejecutar solo tests que fallaron en la última ejecución
pytest --lf
```

## Cobertura de Tests

Los tests cubren las siguientes funcionalidades:

### Autenticación (`test_auth.py`)
- ✅ Hash de contraseñas con bcrypt
- ✅ Verificación de contraseñas
- ✅ Creación de tokens JWT
- ✅ Verificación de tokens JWT
- ✅ Manejo de tokens expirados e inválidos

### Modelos (`test_models.py`)
- ✅ Creación de usuarios en base de datos
- ✅ Validación de campos requeridos
- ✅ Unicidad de email
- ✅ Timestamps automáticos
- ✅ Valores por defecto

### Schemas (`test_schemas.py`)
- ✅ Validación de UserCreate
- ✅ Validación de UserLogin
- ✅ Serialización de UserResponse
- ✅ Validación de emails
- ✅ Manejo de caracteres especiales

### Servicio de Usuario (`test_user_service.py`)
- ✅ Creación de usuarios
- ✅ Autenticación de usuarios
- ✅ Login y generación de tokens
- ✅ Obtención de usuarios por ID y email
- ✅ Manejo de errores y excepciones
- ✅ Tests de integración con base de datos

### Rutas de API (`test_user_routes.py`)
- ✅ Registro de usuarios
- ✅ Login y generación de tokens
- ✅ Endpoints protegidos con autenticación
- ✅ Health check
- ✅ Validación de datos de entrada
- ✅ Manejo de errores HTTP

## Configuración de Testing

### Base de Datos
Los tests utilizan SQLite en memoria para aislamiento completo:
- Cada test obtiene una base de datos limpia
- No hay interferencia entre tests
- Ejecución rápida

### Mocking
Los tests unitarios utilizan mocks para:
- Aislar la lógica de negocio
- Simular respuestas de base de datos
- Controlar dependencias externas

## Mejores Prácticas

1. **Aislamiento**: Cada test es independiente
2. **Nombres descriptivos**: Los nombres de tests explican qué se está probando
3. **AAA Pattern**: Arrange, Act, Assert en cada test
4. **Edge Cases**: Se prueban casos límite y errores
5. **Mocking**: Se mockan dependencias externas en tests unitarios
6. **Integration**: Los tests de integración prueban el flujo completo

## Agregar Nuevos Tests

Al agregar nuevas funcionalidades:

1. **Tests Unitarios**: Para lógica de negocio aislada
2. **Tests de Integración**: Para endpoints y flujos completos
4. **Mocks**: Para dependencias externas

Ejemplo de nuevo test:
```python
def test_new_functionality(self, db_session):
    # Arrange
    setup_data = ...
    
    # Act
    result = service.new_functionality(setup_data)
    
    # Assert
    assert result.expected_property == expected_value
```
