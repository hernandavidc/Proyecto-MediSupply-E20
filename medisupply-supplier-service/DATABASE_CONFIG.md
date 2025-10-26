# Configuración de Base de Datos - Supplier Service

## Resumen

El servicio `medisupply-supplier-service` soporta dos modos de operación según el entorno:

### 1. Desarrollo/Testing Local (SQLite)
Por defecto, el servicio usa SQLite para facilitar el desarrollo y testing local.

**Configuración:**
```bash
DATABASE_URL=sqlite:///./supplier.db
```

**Cuándo usar:**
- Desarrollo local
- Ejecución de tests unitarios
- Desarrollo de nuevas funcionalidades

### 2. Producción (PostgreSQL)
En producción (Kubernetes), el servicio DEBE usar PostgreSQL.

**Configuración en Kubernetes:**
```bash
DATABASE_URL=postgresql://mediadmin:MediSupply2024@postgres-service:5432/suppliers_db
```

Esta configuración se define en `k8s/services/supplier-service/supplier-service-secret.yaml`

**Cuándo usar:**
- Despliegue en Kubernetes/GKE
- Entornos de producción
- Entornos de staging

## Configuración Actual

### Archivo de Configuración
`app/core/config.py` está configurado para:
- Usar SQLite por defecto (para desarrollo)
- Soportar PostgreSQL cuando se provea la variable de entorno `DATABASE_URL`
- Leer configuración desde variables de entorno o archivo `.env`

### Kubernetes
El deployment en Kubernetes (`k8s/services/supplier-service/supplier-service-secret.yaml`) define:
- `DATABASE_URL` con conexión a PostgreSQL
- Conexión al servicio `postgres-service` en el namespace `medisupply`
- Base de datos `suppliers_db`

### Inicialización de Base de Datos
El servicio incluye un `initContainer` que:
1. Espera a que PostgreSQL esté listo (`wait-for-db`)
2. Ejecuta `scripts/init_database.py` para poblar datos base (países, certificaciones, categorías)

## Verificación

Para verificar qué base de datos está usando el servicio:

```bash
# Revisar logs del pod
kubectl logs -n medisupply deployment/supplier-service-deployment

# Verificar configuración
kubectl describe deployment -n medisupply supplier-service-deployment

# Revisar secretos
kubectl get secret -n medisupply supplier-service-secret -o yaml
```

## Migración de Datos

Al cambiar de SQLite a PostgreSQL en producción:
1. Los datos de catálogos se crean automáticamente vía `init-database`
2. Los datos de negocios deben migrarse manualmente o mediante scripts de migración
3. Se recomienda backup antes de migrar

## Troubleshooting

### Error: "Could not translate host name postgres-service"
- Verificar que el servicio PostgreSQL esté corriendo en Kubernetes
- Verificar conectividad entre pods
- Revisar configuración de red en Kubernetes

### Error: "Peer authentication failed"
- Verificar credenciales en `supplier-service-secret.yaml`
- Verificar que el usuario existe en PostgreSQL
- Revisar permisos en base de datos

### Error: "Database does not exist"
- Verificar que la base de datos `suppliers_db` existe
- Verificar permisos del usuario para crear tablas
- Revisar logs del initContainer

