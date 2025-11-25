# 🚀 Pruebas de Performance - MediSupply

Pruebas de performance end-to-end contra el edge-proxy de producción.

## 📊 Última Ejecución

**Fecha**: 25 de Noviembre de 2025  
**Resultados**: Ver [PERFORMANCE_TEST_RESULTS_FINAL.md](./PERFORMANCE_TEST_RESULTS_FINAL.md) ⭐  
**Status**: ✅ **EXITOSO** - 7 de 9 tests pasaron | Todos los SLAs cumplidos  
**Tiempo Promedio**: 315ms | **Rating**: ⭐⭐⭐⭐⭐

## 📋 SLAs a Validar

| Métrica | Objetivo | Test |
|---------|----------|------|
| **Localización** | ≤1s | Bodegas, Vehículos |
| **Optimización de Rutas** | ≤3s | Cálculo de ruta óptima |
| **Throughput de Órdenes** | 100-400 pedidos/min | Creación masiva de órdenes |
| **Endpoints Generales** | ≤2s | Lista productos, clientes, etc. |

## 🔧 Instalación

```bash
cd performance-tests

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## 🧪 Tipos de Pruebas

### 1. **Response Time Tests** (pytest-benchmark)

Miden el tiempo de respuesta de endpoints individuales.

```bash
# Ejecutar todas las pruebas de tiempo de respuesta
pytest test_response_time.py -v

# Con reporte detallado de benchmark
pytest test_response_time.py -v --benchmark-only

# Guardar resultados en JSON
pytest test_response_time.py --benchmark-json=results.json

# Ver comparaciones entre ejecuciones
pytest-benchmark compare results.json
```

**Ejemplo de salida:**
```
test_login_performance                  PASSED (mean: 0.235s, max: 0.421s) ✅
test_list_bodegas_performance          PASSED (mean: 0.512s, max: 0.892s) ✅ SLA ≤1s
test_route_optimization_performance    PASSED (mean: 2.145s, max: 2.987s) ✅ SLA ≤3s
```

### 2. **Load Tests** (Locust)

Simulan carga de múltiples usuarios concurrentes.

#### Modo Interactivo (con UI web)

```bash
locust -f locustfile.py --host=https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app
```

Abre http://localhost:8089 y configura:
- **Number of users**: 10
- **Spawn rate**: 2 users/second
- **Run time**: 1m

#### Modo Headless (sin UI)

```bash
# Test rápido: 10 usuarios, 1 minuto
locust -f locustfile.py \
  --host=https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app \
  --users 10 --spawn-rate 2 --run-time 1m --headless

# Test de carga media: 50 usuarios, 5 minutos
locust -f locustfile.py \
  --host=https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app \
  --users 50 --spawn-rate 5 --run-time 5m --headless

# Test de carga alta: 100 usuarios, 10 minutos
locust -f locustfile.py \
  --host=https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app \
  --users 100 --spawn-rate 10 --run-time 10m --headless
```

#### Test específico de Throughput de Órdenes

```bash
# Medir creación de órdenes (SLA: 100-400/min)
locust -f locustfile.py \
  --host=https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app \
  --users 20 --spawn-rate 5 --run-time 2m --headless \
  OrderCreationUser
```

**Ejemplo de salida:**
```
======================================================================
📊 RESULTADOS DE PERFORMANCE
======================================================================
⏱️  Tiempo de ejecución: 120.45s (2.01 min)
📦 Órdenes creadas: 456
🚀 Throughput: 227.11 órdenes/minuto
----------------------------------------------------------------------
✅ SLA CUMPLIDO: 227.11 está dentro del rango 100-400 órdenes/min
======================================================================
```

## 📊 Estructura de Archivos

```
performance-tests/
├── config.py                # Configuración (URLs, SLAs, credenciales)
├── conftest.py             # Fixtures de pytest
├── test_response_time.py   # Tests de tiempo de respuesta (benchmark)
├── locustfile.py           # Tests de carga (Locust)
├── requirements.txt        # Dependencias
└── README.md              # Esta documentación
```

## 🎯 Clases de Usuario en Locust

### `MediSupplyUser`
Usuario general que realiza operaciones comunes:
- Listar productos (peso: 3)
- Listar clientes (peso: 2)
- Listar órdenes (peso: 2)
- Listar vendedores (peso: 1)
- Localización de bodegas/vehículos (peso: 1)

### `OrderCreationUser`
Usuario especializado en crear órdenes para medir throughput:
- Crear órdenes continuamente (peso: 10)
- Objetivo: 100-400 órdenes/minuto

## 📈 Interpretación de Resultados

### pytest-benchmark

```python
stats.mean    # Tiempo promedio de respuesta
stats.max     # Tiempo máximo (peor caso)
stats.min     # Tiempo mínimo (mejor caso)
stats.stddev  # Desviación estándar
```

### Locust

```
Request/s    # Requests por segundo
Failures     # Requests fallidos
Average (ms) # Tiempo de respuesta promedio
Min (ms)     # Tiempo mínimo
Max (ms)     # Tiempo máximo
```

## 🚨 Criterios de Éxito

### Response Time Tests
- ✅ **Localización**: Mean < 1.0s, Max < 1.5s
- ✅ **Rutas**: Mean < 3.0s, Max < 4.5s
- ✅ **Endpoints generales**: Mean < 2.0s, Max < 3.0s

### Load Tests
- ✅ **Error rate**: < 1%
- ✅ **Response time 95th percentile**: < 3s
- ✅ **Throughput órdenes**: 100-400/min

## 🔍 Troubleshooting

### Error: "No se pudo obtener token de autenticación"
Verifica las credenciales en `config.py` o variables de entorno.

### Error: 404 en endpoints
Verifica que el edge-proxy esté desplegado y accesible.

### Performance degradada
1. Verifica la carga actual del sistema
2. Revisa logs del edge-proxy y microservicios
3. Considera escalar los recursos (HPA en Kubernetes)

## 📝 Ejemplo de Ejecución Completa

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar tests de tiempo de respuesta
pytest test_response_time.py -v --benchmark-only

# 3. Ejecutar test de carga ligera
locust -f locustfile.py \
  --host=https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app \
  --users 10 --spawn-rate 2 --run-time 2m --headless

# 4. Ejecutar test de throughput de órdenes
locust -f locustfile.py \
  --host=https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app \
  --users 20 --spawn-rate 5 --run-time 2m --headless \
  OrderCreationUser
```

## 🔄 Integración con CI/CD

Agregar al pipeline:

```yaml
performance-tests:
  stage: test
  script:
    - cd performance-tests
    - pip install -r requirements.txt
    - pytest test_response_time.py --benchmark-only --benchmark-json=results.json
    - locust -f locustfile.py --host=$EDGE_PROXY_URL --users 10 --spawn-rate 2 --run-time 1m --headless
  artifacts:
    paths:
      - performance-tests/results.json
```

## 📚 Referencias

- [pytest-benchmark docs](https://pytest-benchmark.readthedocs.io/)
- [Locust docs](https://docs.locust.io/)
- [Plan de Pruebas MediSupply - Sección 2.4.3 (Performance)](../docs/test-plan.md)

