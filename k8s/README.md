# Estructura de carpetas para deployment en Kubernetes

k8s/
├── namespace.yaml                    # Namespace principal de medisupply
├── database/                         # PostgreSQL cluster
│   ├── postgres-secret.yaml         # Credenciales de base de datos
│   ├── postgres-deployment.yaml     # Deployment de PostgreSQL 15 (usa emptyDir, sin persistencia)
│   ├── postgres-service.yaml        # Service interno para DB
│   └── user-db-service.yaml         # Alias para user-service compatibility
├── services/                         # Microservicios
│   └── user-service/                # Servicio de usuarios y proveedores
│       ├── user-service-secret.yaml      # Secrets (JWT, DB URL)
│       ├── user-service-configmap.yaml   # Config (DEBUG, HOST, PORT)
│       ├── user-service-deployment.yaml  # Deployment con 2 replicas
│       └── user-service-service.yaml     # Service interno
└── ingress/                         # Punto de entrada único
    └── medisupply-ingress.yaml      # Load Balancer + routing

scripts/
├── create-gke-cluster.sh           # Script para crear cluster GKE optimizado
└── deploy-to-k8s.sh               # Script de deploy completo

.github/workflows/
└── deploy.yml                      # CI/CD automático en merge a main

## Comandos de Control de Infraestructura

### Escalar cluster a 0 nodos (pausar todo):
```bash
gcloud container clusters resize medisupply-cluster --num-nodes=0 --region=us-central1
```

### Reactivar cluster (1 nodo mínimo):
```bash
gcloud container clusters resize medisupply-cluster --num-nodes=1 --region=us-central1
```

### Pausar servicios específicos:
```bash
# Escalar user-service a 0 replicas
kubectl scale deployment user-service-deployment --replicas=0 -n medisupply

# Escalar PostgreSQL a 0 replicas  
kubectl scale deployment postgres-deployment --replicas=0 -n medisupply
```

### Reactivar servicios:
```bash
# Reactivar PostgreSQL
kubectl scale deployment postgres-deployment --replicas=1 -n medisupply

# Reactivar user-service
kubectl scale deployment user-service-deployment --replicas=2 -n medisupply
```

### Eliminar toda la infraestructura:
```bash
# Eliminar todos los recursos del namespace
kubectl delete namespace medisupply

# Eliminar cluster completo
gcloud container clusters delete medisupply-cluster --region=us-central1
```

### Estado actual de recursos:
```bash
# Ver estado de pods
kubectl get pods -n medisupply

# Ver estado del cluster
gcloud container clusters describe medisupply-cluster --region=us-central1

# Ver nodos del cluster
kubectl get nodes
```
