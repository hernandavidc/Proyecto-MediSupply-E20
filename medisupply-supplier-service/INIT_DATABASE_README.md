# 🚀 Script de Inicialización de Base de Datos - MediSupply Supplier Service

Este documento describe el sistema de inicialización automática de datos base que se ejecuta en cada deploy para poblar la base de datos con información necesaria.

## 📋 Descripción

El sistema incluye:
- **Script de inicialización Python**: Crea datos base necesarios
- **Init Container**: Se ejecuta automáticamente en Kubernetes antes del servicio principal
- **Integración con CI/CD**: Construcción y despliegue automático
- **Datos base**: Catálogos, proveedores, vendedores y productos de ejemplo

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub Push   │───▶│  GitHub Actions  │───▶│   GKE Cluster   │
│   (main branch) │    │   (Build & Deploy)│    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │ Init Container  │
                                               │ (init-database) │
                                               └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │ Supplier Service│
                                               │   (Main App)    │
                                               └─────────────────┘
```

## 📁 Archivos del Sistema

### Scripts de Inicialización
- `scripts/init_database.py` - Script principal de inicialización
- `scripts/init_db.sh` - Script shell para init container
- `test_init.sh` - Script de prueba local

### Docker
- `Dockerfile.init` - Dockerfile para init container
- `Dockerfile` - Dockerfile principal del servicio

### Kubernetes
- `k8s/services/supplier-service/supplier-service-deployment.yaml` - Deployment con init container

### CI/CD
- `.github/workflows/deploy.yml` - Workflow de GitHub Actions

## 🔧 Datos Inicializados

### 1. Catálogos Base
- **Países**: Colombia, Perú, Ecuador, México, Chile, Argentina, Brasil
- **Certificaciones**: FDA, EMA, INVIMA, DIGEMID, COFEPRIS, ANVISA, ISP
- **Categorías**: Medicamentos especiales, controlados, insumos quirúrgicos, etc.

### 2. Proveedores de Ejemplo
- **Farmacéutica Internacional S.A.S** - Múltiples países, medicamentos especiales
- **MedSupply Global Ltda** - Insumos quirúrgicos y reactivos
- **BioMedical Solutions Inc** - Pruebas diagnósticas y equipos
- **PharmaTech Colombia** - Solo Colombia, estado pendiente
- **Global Health Supplies** - Cobertura completa

### 3. Vendedores de Ejemplo
- María González (Colombia)
- Carlos Rodríguez (Colombia)
- Ana Martínez (Perú)
- Luis Fernández (Ecuador)
- Sofia Herrera (México)

### 4. Productos de Ejemplo
- Paracetamol 500mg
- Ibuprofeno 400mg

## 🚀 Proceso de Deploy

### 1. GitHub Actions Workflow
```yaml
# Construcción de imágenes
- Build main supplier-service image
- Build init container image (Dockerfile.init)
- Push ambas imágenes al registry

# Despliegue en Kubernetes
- Aplicar manifiestos actualizados
- Init container ejecuta inicialización
- Servicio principal inicia después
```

### 2. Init Container
```bash
# Flujo de ejecución
1. Esperar conexión a base de datos
2. Ejecutar scripts/init_database.py
3. Crear datos base si no existen
4. Completar exitosamente
5. Servicio principal inicia
```

### 3. Verificación
- Health checks en `/healthz`
- Logs de inicialización disponibles
- Datos verificables via API

## 🧪 Pruebas Locales

### Ejecutar Inicialización Local
```bash
cd medisupply-supplier-service
./test_init.sh
```

### Verificar Datos
```bash
# Verificar productos
curl http://localhost:8000/api/v1/productos/

# Verificar proveedores
curl http://localhost:8000/api/v1/proveedores/

# Verificar catálogos
curl http://localhost:8000/api/v1/catalogs/paises
curl http://localhost:8000/api/v1/catalogs/certificaciones
curl http://localhost:8000/api/v1/catalogs/categorias
```

## 🔍 Monitoreo y Logs

### Logs del Init Container
```bash
kubectl logs -l app=supplier-service -n medisupply -c init-database
```

### Estado del Deploy
```bash
kubectl get pods -n medisupply
kubectl describe pod <pod-name> -n medisupply
```

### Verificar Inicialización
```bash
# Conectar a la base de datos y verificar datos
kubectl exec -it <postgres-pod> -n medisupply -- psql -U postgres -d medisupply_supplier
```

## 🛠️ Configuración

### Variables de Entorno Requeridas
```bash
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key
```

### Configuración de Kubernetes
- **Init Container**: Usa misma configuración que servicio principal
- **Recursos**: Mínimos (solo durante inicialización)
- **Timeout**: 600 segundos para completar inicialización

## 🔄 Flujo de Datos

1. **Deploy Trigger**: Push a branch `main`
2. **Build Phase**: Construcción de imágenes Docker
3. **Deploy Phase**: Aplicación de manifiestos Kubernetes
4. **Init Phase**: Ejecución de init container
5. **Service Phase**: Inicio del servicio principal
6. **Verification**: Health checks y verificación de datos

## 🎯 Beneficios

- ✅ **Automatización**: Sin intervención manual en cada deploy
- ✅ **Consistencia**: Datos base siempre disponibles
- ✅ **Escalabilidad**: Funciona con múltiples réplicas
- ✅ **Confiabilidad**: Rollback automático en caso de error
- ✅ **Monitoreo**: Logs detallados del proceso
- ✅ **Flexibilidad**: Fácil modificación de datos base

## 🚨 Troubleshooting

### Init Container Falla
```bash
# Ver logs detallados
kubectl logs <pod-name> -c init-database -n medisupply

# Verificar conectividad a BD
kubectl exec -it <pod-name> -c init-database -n medisupply -- nc -z postgres-service 5432
```

### Datos No Se Crean
```bash
# Verificar si ya existen
kubectl exec -it <postgres-pod> -n medisupply -- psql -U postgres -d medisupply_supplier -c "SELECT COUNT(*) FROM paises;"

# Forzar recreación (eliminar datos existentes)
kubectl exec -it <postgres-pod> -n medisupply -- psql -U postgres -d medisupply_supplier -c "DELETE FROM productos; DELETE FROM proveedores; DELETE FROM vendedores;"
```

### Timeout en Deploy
```bash
# Aumentar timeout en deployment
kubectl patch deployment supplier-service-deployment -n medisupply -p '{"spec":{"progressDeadlineSeconds":1200}}'
```

## 📈 Métricas y Monitoreo

- **Tiempo de inicialización**: ~30-60 segundos
- **Datos creados**: ~20 registros base
- **Tamaño de imagen init**: ~200MB
- **Recursos utilizados**: CPU: 100m, Memory: 128Mi

## 🔮 Futuras Mejoras

- [ ] Inicialización incremental (solo datos faltantes)
- [ ] Configuración por ambiente (dev/staging/prod)
- [ ] Backup automático antes de inicialización
- [ ] Métricas de inicialización en Prometheus
- [ ] Notificaciones de estado de inicialización
