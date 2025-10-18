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
├── 👤 User Service (Implementado)      # Autenticación y gestión de usuarios
├── 🏢 Provider Service (Planificado)  # Gestión de proveedores
├── 📦 Inventory Service (Planificado) # Control de inventario
├── 🛒 Order Service (Planificado)     # Gestión de pedidos
├── 🚚 Logistics Service (Planificado) # Seguimiento de entregas
└── 📊 Analytics Service (Planificado) # Reportes y métricas
```

### Estado Actual de Servicios

| Servicio | Estado | Puerto | Base de Datos | Descripción |
|----------|--------|--------|---------------|-------------|
| **User Service** | ✅ Implementado | 8001 | PostgreSQL | Autenticación JWT, gestión de usuarios |
| **Provider Service** | 🔄 Planificado | 8002 | PostgreSQL | Gestión de proveedores médicos |
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

# 4. Verificar el estado de salud
curl http://localhost:8001/health
```

### 🔧 Desarrollo Local (Sin Docker)

```bash
# 1. Navegar al servicio
cd user-service

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 5. Iniciar el servicio
python run.py
```

## 🧪 Ejecutar Tests

### Tests Automáticos (Recomendado)

```bash
# Ejecutar tests de todos los servicios que cambiaron
./test-local.sh

# Forzar tests de un servicio específico
./test-local.sh force-user
```

### Tests por Servicio

```bash
cd user-service

# Activar entorno virtual
source venv/bin/activate

# Configurar variables de test
export DATABASE_URL="sqlite:///./test.db"
export SECRET_KEY="test_secret_key_for_testing_only"

# Ejecutar todos los tests
pytest tests/ -v

# Tests con cobertura
pytest tests/ -v --cov=app --cov-report=term-missing

# Tests específicos
pytest tests/unit/ -v          # Solo tests unitarios
pytest tests/integration/ -v   # Solo tests de integración
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

### Endpoints Principales

```bash
# Registrar usuario
POST http://localhost:8001/api/v1/users/register
{
  "name": "Juan Pérez",
  "email": "juan@ejemplo.com", 
  "password": "miPassword123"
}

# Generar token JWT
POST http://localhost:8001/api/v1/users/generate-token
{
  "email": "juan@ejemplo.com",
  "password": "miPassword123"
}

# Ver mi información (requiere token)
GET http://localhost:8001/api/v1/users/me
Authorization: Bearer <token>
```

## 🔄 CI/CD y Deploy

### Flujos Automáticos

El proyecto incluye dos workflows principales de GitHub Actions:

1. **Tests Automáticos**: Se ejecutan en cada PR
2. **Deploy a GKE**: Se ejecuta en push a `main`

### 🧪 Sistema de Tests en PRs

- **Detección Inteligente**: Solo ejecuta tests de servicios modificados
- **Matriz de Python**: Tests en Python 3.11 y 3.12
- **Reportes Automáticos**: Comentarios en PRs con resultados
- **Branch Protection**: Bloquea merge si tests fallan

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
├── run_tests.sh
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
      - "5434:5432"
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
      python-version: ['3.11', '3.12']
  
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
    run: |
      cd inventory-service
      pytest tests/ -v --cov=app --cov-report=term-missing

# En el job check-overall-status, agregar:
- name: Check Inventory Service
  if: needs.detect-changes.outputs.inventory-service == 'true'
  run: |
    if [[ "${{ needs.test-inventory-service.result }}" == "failure" ]]; then
      echo "Inventory Service tests failed"
      exit 1
    fi
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

2. **Modificar `.github/workflows/deploy.yml`**:

```yaml
# En el step "Build and push images", agregar:
- name: Build and push inventory-service image
  run: |
    docker build -t $REGISTRY/$PROJECT_ID/medisupply/inventory-service:$GITHUB_SHA ./inventory-service
    docker tag $REGISTRY/$PROJECT_ID/medisupply/inventory-service:$GITHUB_SHA $REGISTRY/$PROJECT_ID/medisupply/inventory-service:latest
    docker push $REGISTRY/$PROJECT_ID/medisupply/inventory-service:$GITHUB_SHA
    docker push $REGISTRY/$PROJECT_ID/medisupply/inventory-service:latest

# En el step "Update Kubernetes manifests", agregar:
- name: Update inventory-service manifests
  run: |
    sed -i "s/PROJECT_ID/$PROJECT_ID/g" k8s/services/inventory-service/inventory-service-deployment.yaml
    sed -i "s/:latest/:$GITHUB_SHA/g" k8s/services/inventory-service/inventory-service-deployment.yaml

# En el step "Deploy to GKE", agregar:
- name: Deploy inventory-service
  run: |
    kubectl apply -f k8s/services/inventory-service/
    kubectl rollout status deployment/inventory-service-deployment -n medisupply --timeout=600s
```

### 5. Actualizar Scripts de Testing

Modificar `test-local.sh` para incluir el nuevo servicio:

```bash
# Verificar cambios en inventory-service
if git diff --name-only HEAD~1 2>/dev/null | grep -q "^inventory-service/" || [ "$1" == "force-inventory" ]; then
    echo "  ✅ Cambios detectados en inventory-service"
    INVENTORY_SERVICE_CHANGED=true
else
    echo "  ⏭️  Sin cambios en inventory-service"
    INVENTORY_SERVICE_CHANGED=false
fi

# Ejecutar tests si hay cambios
if [ "$INVENTORY_SERVICE_CHANGED" == "true" ]; then
    echo "🧪 Ejecutando tests de Inventory Service..."
    cd inventory-service
    source venv/bin/activate
    export DATABASE_URL="sqlite:///./test.db"
    pytest tests/ -v --cov=app --cov-report=term-missing
    # ... resto de la lógica
fi
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
│   ├── PostgreSQL (inventory_db)
│   └── PostgreSQL (orders_db)
├── Services:
│   ├── user-service (Port 80)
│   ├── inventory-service (Port 80)
│   └── order-service (Port 80)
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

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
# Docker Compose
docker-compose logs -f medisupply-user-service

# Kubernetes
kubectl logs -f deployment/user-service-deployment -n medisupply
kubectl logs -f -l app=postgres -n medisupply
```

### Health Checks

```bash
# Verificar estado de servicios
curl http://localhost:8001/health
curl http://localhost:8002/health  # inventory-service
curl http://localhost:8003/health  # order-service

# En Kubernetes
kubectl get pods -n medisupply
kubectl describe pod <pod-name> -n medisupply
```

---

## 🎉 Tecnologías Utilizadas

| Categoría | Tecnologías |
|-----------|-------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy |
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