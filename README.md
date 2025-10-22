# 🏥 MediSupply - Plataforma Integral de Suministro Médico

MediSupply es una plataforma integral para optimizar la cadena de suministro médico en América Latina. Integra adquisición, inventario, ventas y logística para garantizar la entrega puntual de suministros médicos y equipos biomédicos.

## 🎯 Descripción del Proyecto

MediSupply es un sistema distribuido de microservicios diseñado para gestionar integralmente la cadena de suministro médico, incluyendo:

- **Gestión de Usuarios y Autenticación**: Control de acceso seguro con JWT
- **Gestión de Proveedores**: Administración de proveedores médicos
- **Inventario Médico**: Control de stock de suministros y equipos
- **Gestión de Pedidos**: Procesamiento de órdenes de compra
- **Logística y Distribución**: Seguimiento de entregas
- **Reportes y Analytics**: Análisis de la cadena de suministro

## 🏗️ Arquitectura de Microservicios

```
MediSupply Platform
├── 👤 User Service (Implementado)           # Autenticación y gestión de usuarios
├── 🏥 Supplier Service (Implementado)       # Gestión de proveedores y productos
├── 📦 Inventory Service (Planificado)       # Control de inventario
├── 🛒 Order Service (Planificado)           # Gestión de pedidos
├── 🚚 Logistics Service (Planificado)       # Seguimiento de entregas
└── 📊 Analytics Service (Planificado)       # Reportes y métricas
```

### Servicios Disponibles

#### 👤 User Service (`user-service`)
- **Puerto**: 8001 (local), 8000 (container)
- **Funcionalidad**: Gestión de usuarios, autenticación y autorización
- **Endpoints**: `/api/v1/users/*`, `/api/v1/providers/*`
- **Documentación**: http://localhost:8001/docs

#### 🏥 Supplier Service (`medisupply-supplier-service`)
- **Puerto**: 8010 (local), 8000 (container)
- **Funcionalidad**: Gestión de proveedores, productos, planes de venta y vendedores
- **Endpoints**: 
  - `/api/v1/proveedores/*` - Gestión de proveedores
  - `/api/v1/productos/*` - Gestión de productos
  - `/api/v1/planes/*` - Planes de venta
  - `/api/v1/vendedores/*` - Gestión de vendedores
  - `/api/v1/paises/*` - Catálogo de países
  - `/api/v1/certificaciones/*` - Certificaciones sanitarias
  - `/api/v1/categorias/*` - Categorías de productos
- **Documentación**: http://localhost:8010/docs

### Estado Actual de Servicios

| Servicio | Estado | Puerto | Base de Datos | Descripción |
|----------|--------|--------|---------------|-------------|
| **User Service** | ✅ Implementado | 8001 | PostgreSQL | Autenticación JWT, gestión de usuarios |
| **Supplier Service** | ✅ Implementado | 8010 | PostgreSQL | Gestión de proveedores, productos y vendedores |
| **Inventory Service** | 🔄 Planificado | 8003 | PostgreSQL | Control de stock y productos |
| **Order Service** | 🔄 Planificado | 8004 | PostgreSQL | Procesamiento de pedidos |
| **Logistics Service** | 🔄 Planificado | 8005 | PostgreSQL | Seguimiento de entregas |

## 🚀 Inicio

### Pre-requisitos

- **Docker** & **Docker Compose** (recomendado)
- **Python 3.11+** (para desarrollo local)
- **PostgreSQL 15+** (si no usas Docker)
- **Git**

### 🐳 Iniciar con Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/Proyecto-MediSupply-E20.git
cd Proyecto-MediSupply-E20

# 2. Iniciar todos los servicios
docker-compose up --build -d

# 3. Verificar que los servicios estén ejecutándose
docker-compose ps

# 4. Probar servicios
./test-local.sh

# 5. Verificar el estado de salud
curl http://localhost:8001/health
curl http://localhost:8010/healthz
```

### 🔧 Desarrollo Local (Sin Docker)

```bash
# User Service
cd user-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py

# Supplier Service
cd medisupply-supplier-service
python3 -m venv venv
source venv/bin/activate
export PYTHONPATH=$(pwd)
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🧪 Testing

### Tests Automáticos (GitHub Actions)
Los tests se ejecutan automáticamente en GitHub Actions cuando hay cambios en:
- `user-service/` - Ejecuta tests del User Service
- `medisupply-supplier-service/` - Ejecuta tests del Supplier Service

### Tests Locales

```bash
# Probar todos los servicios
./test-local.sh

# Tests por servicio
# User Service
cd user-service
source venv/bin/activate
export DATABASE_URL="sqlite:///./test.db"
export SECRET_KEY="test_secret_key_for_testing_only"
pytest tests/ -v --cov=app --cov-report=term-missing

# Supplier Service
cd medisupply-supplier-service
source venv/bin/activate
export DATABASE_URL="sqlite:///./test.db"
export SECRET_KEY="test_secret_key_for_testing_only"
export PYTHONPATH=$(pwd)
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Tipos de Tests Implementados

- **Tests Unitarios**: Validación de lógica de negocio
- **Tests de Integración**: Endpoints y base de datos
- **Tests de Schemas**: Validación con Pydantic
- **Tests de Autenticación**: JWT tokens y passwords
- **Tests de Modelos**: Interacción con base de datos

## 📚 Documentación de APIs

### User Service (Disponible)

- **Health Check**: http://localhost:8001/health
- **Documentación**: http://localhost:8001/docs

### Supplier Service (Disponible)

- **Health Check**: http://localhost:8010/healthz
- **Documentación**: http://localhost:8010/docs

### Endpoints Principales

```bash
# User Service - Registrar usuario
POST http://localhost:8001/api/v1/users/register
{
  "name": "Juan Pérez",
  "email": "juan@ejemplo.com", 
  "password": "miPassword123"
}

# User Service - Generar token JWT
POST http://localhost:8001/api/v1/users/generate-token
{
  "email": "juan@ejemplo.com",
  "password": "miPassword123"
}

# Supplier Service - Listar proveedores
GET http://localhost:8010/api/v1/proveedores

# Supplier Service - Listar países
GET http://localhost:8010/api/v1/paises
```

## 🔄 CI/CD y Deploy

### Flujos Automáticos

El proyecto incluye workflows de GitHub Actions:

1. **Tests Automáticos**: Se ejecutan en cada PR
2. **Deploy a GKE**: Se ejecuta en push a `main`

### 🧪 Sistema de Tests en PRs

- **Detección Inteligente**: Solo ejecuta tests de servicios modificados
- **Matriz de Python**: Tests en Python 3.13
- **Reportes Automáticos**: Comentarios en PRs con resultados
- **Branch Protection**: Bloquea merge si tests fallan

### 🚀 Despliegue en Producción

#### Desarrollo Local (Docker Compose)
```bash
# Levantar todos los servicios
docker-compose up --build -d

# Probar servicios
./test-local.sh

# Detener servicios
docker-compose down
```

#### Producción (Kubernetes)
```bash
# 1. Construir y subir imágenes
export PROJECT_ID=tu-proyecto-gcp
./scripts/build-and-push-images.sh

# 2. Desplegar a Kubernetes
./scripts/deploy-to-k8s.sh
```

## 📊 Monitoreo

### Health Checks
- **User Service**: http://localhost:8001/health
- **Supplier Service**: http://localhost:8010/healthz

### Métricas
- Cobertura de código: >80%
- Tests de integración y unitarios
- Health checks automáticos

### Ver Logs en Tiempo Real

```bash
# Docker Compose
docker-compose logs -f medisupply-user-service
docker-compose logs -f medisupply-supplier-service

# Kubernetes
kubectl logs -f deployment/user-service-deployment -n medisupply
kubectl logs -f deployment/supplier-service-deployment -n medisupply
```

## ➕ Agregar Nuevos Servicios

### 1. Estructura del Nuevo Servicio

```bash
# Crear nuevo servicio (ejemplo: inventory-service)
mkdir inventory-service
cd inventory-service

# Estructura recomendada
inventory-service/
├── app/
│   ├── api/v1/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── Dockerfile
├── requirements.txt
├── pytest.ini
└── README.md
```

### 2. Configurar Docker Compose

Agregar al `docker-compose.yml`:

```yaml
services:
  medisupply-inventory-service:
    build: 
      context: ./inventory-service
      dockerfile: Dockerfile
    container_name: medisupply-inventory-service
    restart: unless-stopped
    ports:
      - "8003:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@medisupply-inventory-db:5432/inventory_db
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      medisupply-inventory-db:
        condition: service_healthy
    networks:
      - medisupply-network

  medisupply-inventory-db:
    image: postgres:15-alpine
    container_name: medisupply-inventory-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: inventory_db
    ports:
      - "5435:5432"
    volumes:
      - medisupply-inventory-db-data:/var/lib/postgresql/data
    networks:
      - medisupply-network

volumes:
  medisupply-inventory-db-data:
    driver: local
```

### 3. Integrar en CI/CD (Tests)

Modificar `.github/workflows/tests.yml`:

```yaml
# En el job detect-changes, agregar:
outputs:
  inventory-service: ${{ steps.changes.outputs.inventory-service }}

# En steps.changes.with.filters, agregar:
filters: |
  inventory-service:
    - 'inventory-service/**'

# Agregar nuevo job:
test-inventory-service:
  name: 🧪 Tests Inventory Service  
  needs: detect-changes
  if: needs.detect-changes.outputs.inventory-service == 'true'
  runs-on: ubuntu-latest
  strategy:
    matrix:
      python-version: ['3.13']
  
  steps:
  - uses: actions/checkout@v4
  - name: Set up Python ${{ matrix.python-version }}
    uses: actions/setup-python@v4
    with:
      python-version: ${{ matrix.python-version }}
      
  - name: Install dependencies
    run: |
      cd inventory-service
      python -m pip install --upgrade pip
      pip install -r requirements.txt
      
  - name: Run tests
    env:
      DATABASE_URL: sqlite:///./test.db
      SECRET_KEY: test_secret_key_for_testing_only
      PYTHONPATH: ${{ github.workspace }}/inventory-service
    run: |
      cd inventory-service
      pytest tests/ -v --cov=app --cov-report=term-missing
```

### 4. Integrar en Deploy (GKE)

1. **Crear manifiestos de Kubernetes**:

```bash
k8s/services/inventory-service/
├── inventory-service-configmap.yaml
├── inventory-service-deployment.yaml  
├── inventory-service-secret.yaml
└── inventory-service-service.yaml
```

2. **Modificar scripts de despliegue**:

```bash
# En scripts/deploy-to-k8s.sh, agregar:
echo "🔧 Desplegando inventory-service..."
kubectl apply -f k8s/services/inventory-service/

echo "⏳ Esperando inventory-service..."
kubectl wait --for=condition=Ready pod -l app=inventory-service -n medisupply --timeout=300s
```

## 🔒 Configuración de Seguridad

### Variables de Entorno Requeridas

```bash
# Para desarrollo local (.env)
DATABASE_URL=postgresql://user:password@localhost:5432/db_name
SECRET_KEY=your-super-secret-jwt-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=true

# Para producción (Kubernetes secrets)
GCP_PROJECT_ID=your-gcp-project
GCP_SA_KEY=base64-encoded-service-account-key
```

### Secretos de GitHub Actions

Configurar en Settings > Secrets and Variables > Actions:

- `GCP_PROJECT_ID`: ID del proyecto de Google Cloud
- `GCP_SA_KEY`: Clave JSON del Service Account (base64)

## 🐳 Despliegue en Kubernetes

### Arquitectura en GKE

```
Google Kubernetes Engine (GKE)
├── Namespace: medisupply
├── Databases:
│   ├── PostgreSQL (users_db)
│   └── PostgreSQL (suppliers_db)
├── Services:
│   ├── user-service (Port 80)
│   └── supplier-service (Port 80)
├── Ingress:
│   └── medisupply-ingress (Load Balancer)
└── Persistent Volumes:
    └── Database storage
```

### Comandos de Despliegue Manual

```bash
# Autenticarse en GCP
gcloud auth login
gcloud config set project YOUR-PROJECT-ID

# Conectarse al cluster
gcloud container clusters get-credentials medisupply-cluster --region us-central1

# Desplegar manualmente
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/database/
kubectl apply -f k8s/services/
kubectl apply -f k8s/ingress/

# Verificar despliegue
kubectl get pods -n medisupply
kubectl get services -n medisupply
kubectl get ingress -n medisupply
```

---

## 🎉 Tecnologías Utilizadas

| Categoría | Tecnologías |
|-----------|-------------|
| **Backend** | Python 3.13+, FastAPI, SQLAlchemy |
| **Base de Datos** | PostgreSQL 15, SQLite (tests) |
| **Autenticación** | JWT, bcrypt, OAuth2 |
| **Containerización** | Docker, Docker Compose |
| **Orquestación** | Kubernetes, Google GKE |
| **CI/CD** | GitHub Actions |
| **Testing** | pytest, pytest-cov, faker |
| **Monitoreo** | Health checks, Logs |
| **Cloud** | Google Cloud Platform |

---

**🏥 MediSupply - Optimizando la cadena de suministro médico en América Latina** 

*Proyecto desarrollado como parte del programa de Maestría en Ingeniería de Software (MISW) de la Universidad de los Andes*