# 🤖 GitHub Actions - Tests Automáticos en PRs

Este proyecto implementa un sistema completo de tests automáticos para un monorepo de microservicios usando GitHub Actions.

## 🎯 Características Principales

### ✅ **Tests Automáticos en PRs**
- Se ejecutan automáticamente cuando se abre/actualiza un PR
- Detecta inteligentemente qué servicios cambiaron
- Ejecuta solo los tests de servicios modificados
- Bloquea el merge si los tests fallan

### 🏗️ **Arquitectura de Monorepo**
- Diseñado para múltiples microservicios
- Cada servicio tiene sus tests independientes
- Escalable para futuros servicios
- Matriz de Python para compatibilidad múltiple

### 📊 **Reportes Inteligentes**
- Comentarios automáticos en PRs con resultados
- Actualización en tiempo real del estado
- Resumen claro de qué pasó/falló
- Instrucciones para corregir errores

## 📁 Estructura de Archivos

```
.github/
├── workflows/
│   └── tests.yml                 # Workflow principal de GitHub Actions
├── BRANCH_PROTECTION.md          # Guía de configuración de branch protection
└── README.md                     # Esta documentación

user-service/
├── tests/                        # Suite completa de tests
│   ├── unit/                     # Tests unitarios
│   ├── integration/              # Tests de integración
│   ├── conftest.py              # Configuración de pytest
│   └── README.md                # Documentación de tests
├── run_tests.sh                 # Script de ejecución de tests
└── requirements.txt             # Dependencias con libs de testing

test-local.sh                    # Script para probar localmente
```

## 🚀 Cómo Funciona

### 1. **Detección de Cambios**
```yaml
detect-changes:
  # Usa dorny/paths-filter para detectar cambios por servicio
  # Solo ejecuta tests de servicios modificados
```

### 2. **Ejecución de Tests por Servicio**
```yaml
test-user-service:
  # Se ejecuta solo si user-service/ cambió
  # Matriz de Python 3.11 y 3.12
  # Tests completos: schemas, auth, services, models
```

### 3. **Reporte de Resultados**
```yaml
report-results:
  # Comenta en el PR con resultados detallados
  # Actualiza comentario existente
  # Instrucciones para corregir errores
```

### 4. **Verificación Final**
```yaml
check-overall-status:
  # Falla si cualquier test requerido falló
  # Permite branch protection basado en este status
```

## 🛡️ Configuración de Branch Protection

### Pasos para Configurar:

1. **Ve a Settings → Branches → Add rule**
2. **Branch pattern**: `main`
3. **Configuraciones requeridas**:
   - ✅ Require PR before merging
   - ✅ Require status checks: `✅ Estado General`
   - ✅ Require up-to-date branches
   - ✅ Require conversation resolution

### Resultado:
- **❌ Merge bloqueado** si tests fallan
- **✅ Merge permitido** solo con tests exitosos
- **🔄 Auto-actualización** en cada push

## 🧪 Testing Local

### Probar antes de hacer push:
```bash
# Probar todos los cambios detectados
./test-local.sh

# Forzar tests de user-service
./test-local.sh force-user
```

### Ejecutar tests directamente:
```bash
cd user-service
source venv/bin/activate
export DATABASE_URL="sqlite:///./test.db"
./run_tests.sh
```

## 📈 Escalabilidad para Futuros Servicios

### Agregar nuevo servicio (ej: inventory-service):

1. **En `.github/workflows/tests.yml`**:
```yaml
detect-changes:
  outputs:
    inventory-service: ${{ steps.changes.outputs.inventory-service }}

filters: |
  inventory-service:
    - 'inventory-service/**'

test-inventory-service:
  name: 🧪 Tests Inventory Service
  needs: detect-changes
  if: needs.detect-changes.outputs.inventory-service == 'true'
  # ... configuración similar a user-service
```

2. **Actualizar branch protection**:
   - Agregar `🧪 Tests Inventory Service` a required status checks

3. **Crear estructura de tests**:
```bash
inventory-service/
├── tests/
├── requirements.txt
└── run_tests.sh
```

## 🎨 Ejemplo de Comentario en PR

```markdown
## 🧪 Resultados de Tests - Microservicios

### 📋 Servicios Analizados

- **👤 User Service**: ✅ Todos los tests pasaron
- **📦 Inventory Service**: ⏭️ Sin cambios - Tests omitidos
- **🛒 Order Service**: ⏭️ Próximamente

### 🎯 Resumen

🟢 **Todos los tests pasaron** - El PR está listo para revisión y merge.

### ✨ Tests ejecutados:
- Validación de schemas
- Tests de autenticación  
- Tests de lógica de negocio
- Tests de integración

---
*🤖 Este comentario se actualiza automáticamente en cada push*
```

## 🔧 Mantenimiento

### Tests que se ejecutan por servicio:
- **Schemas**: Validación de datos con Pydantic
- **Auth**: Hash de contraseñas, JWT tokens
- **Services**: Lógica de negocio (CRUD operations)
- **Models**: Integración con base de datos
- **Routes**: Tests end-to-end de API endpoints

### Variables de entorno utilizadas:
- `DATABASE_URL`: SQLite para tests aislados
- `SECRET_KEY`: Clave de testing para JWT
- Matrix de Python: 3.11 y 3.12

## 🚨 Solución de Problemas

### Tests fallan localmente:
```bash
cd user-service
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./run_tests.sh
```

### Action falla en GitHub:
1. Revisa logs en pestaña "Actions"
2. Verifica que requirements.txt esté actualizado
3. Prueba localmente con `./test-local.sh`

### Branch protection no funciona:
1. Verifica que rule esté en branch `main`
2. Confirma status check names exactos
3. Asegúrate que "Include administrators" esté habilitado

## 🎉 Beneficios

- **🛡️ Calidad**: No se permite código roto en main
- **⚡ Eficiencia**: Solo ejecuta tests necesarios
- **👥 Colaboración**: Feedback claro en PRs
- **📈 Escalabilidad**: Fácil agregar nuevos servicios
- **🔧 Mantenibilidad**: Tests bien organizados y documentados
