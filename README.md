# Proyecto-MediSupply-E20
Proyecto Final MISW - Universidad de los Andes. MediSupply - Plataforma integral para optimizar la cadena de suministro médico en América Latina. Integra adquisición, inventario, ventas y logística para garantizar entrega puntual de suministros médicos y equipos biomédicos.

## 🏗️ Arquitectura de Microservicios

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

## 🚀 Despliegue

### Desarrollo Local (Docker Compose)
```bash
# Levantar todos los servicios
docker-compose up --build -d

# Probar servicios
./test-local.sh

# Detener servicios
docker-compose down
```

### Producción (Kubernetes)
```bash
# 1. Construir y subir imágenes
export PROJECT_ID=tu-proyecto-gcp
./scripts/build-and-push-images.sh

# 2. Desplegar a Kubernetes
./scripts/deploy-to-k8s.sh
```

## 🧪 Testing

### Tests Automáticos
Los tests se ejecutan automáticamente en GitHub Actions cuando hay cambios en:
- `user-service/` - Ejecuta tests del User Service
- `medisupply-supplier-service/` - Ejecuta tests del Supplier Service

### Tests Locales
```bash
# User Service
cd user-service
source venv/bin/activate
pytest tests/ -v

# Supplier Service
cd medisupply-supplier-service
source venv/bin/activate
export PYTHONPATH=$(pwd)
pytest tests/ -v
```

## 📊 Monitoreo

### Health Checks
- **User Service**: http://localhost:8001/health
- **Supplier Service**: http://localhost:8010/healthz

### Métricas
- Cobertura de código: >80%
- Tests de integración y unitarios
- Health checks automáticos 
