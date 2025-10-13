#!/bin/bash

# Script para crear el cluster GKE

# Variables de configuración
PROJECT_ID="tu-project-id"
CLUSTER_NAME="medisupply-cluster"
ZONE="us-central1-a"  # Zona de menor costo
REGION="us-central1"

echo "🚀 Creando cluster GKE para MediSupply..."

# Crear cluster
gcloud container clusters create $CLUSTER_NAME \
    --zone=$ZONE \
    --machine-type=e2-micro \
    --num-nodes=2 \
    --min-nodes=1 \
    --max-nodes=3 \
    --enable-autoscaling \
    --disk-size=10GB \
    --disk-type=pd-standard \
    --enable-autorepair \
    --enable-autoupgrade \
    --maintenance-window-start=2023-01-01T09:00:00Z \
    --maintenance-window-end=2023-01-01T17:00:00Z \
    --maintenance-window-recurrence="FREQ=WEEKLY;BYDAY=SA" \
    --no-enable-cloud-logging \
    --no-enable-cloud-monitoring \
    --preemptible

echo "✅ Cluster creado exitosamente!"

# Obtener credenciales
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE

echo "🔐 Credenciales configuradas"

# Verificar conexión
kubectl get nodes

echo "📋 Para eliminar el cluster cuando no lo necesites:"
echo "gcloud container clusters delete $CLUSTER_NAME --zone=$ZONE"
