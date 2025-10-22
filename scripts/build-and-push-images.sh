#!/bin/bash

# Build and push Docker images to GCR
set -e

# Configuración
PROJECT_ID=${PROJECT_ID:-"your-gcp-project-id"}
REGION=${REGION:-"us-central1"}
GCR_REGISTRY="gcr.io"

echo "🐳 Construyendo y subiendo imágenes Docker..."

# Verificar que PROJECT_ID esté configurado
if [ "$PROJECT_ID" = "your-gcp-project-id" ]; then
    echo "❌ Error: PROJECT_ID no está configurado"
    echo "Ejecuta: export PROJECT_ID=tu-proyecto-gcp"
    exit 1
fi

# Configurar Docker para usar gcloud como helper
echo "🔐 Configurando autenticación con GCR..."
gcloud auth configure-docker

# Construir y subir user-service
echo "🔨 Construyendo user-service..."
cd user-service
docker build -t ${GCR_REGISTRY}/${PROJECT_ID}/medisupply-user-service:latest .
docker push ${GCR_REGISTRY}/${PROJECT_ID}/medisupply-user-service:latest
cd ..

# Construir y subir supplier-service
echo "🔨 Construyendo supplier-service..."
cd medisupply-supplier-service
docker build -t ${GCR_REGISTRY}/${PROJECT_ID}/medisupply-supplier-service:latest .
docker push ${GCR_REGISTRY}/${PROJECT_ID}/medisupply-supplier-service:latest
cd ..

echo "✅ Imágenes construidas y subidas exitosamente!"
echo ""
echo "📋 Imágenes disponibles:"
echo "  - ${GCR_REGISTRY}/${PROJECT_ID}/medisupply-user-service:latest"
echo "  - ${GCR_REGISTRY}/${PROJECT_ID}/medisupply-supplier-service:latest"
echo ""
echo "🚀 Ahora puedes ejecutar: ./scripts/deploy-to-k8s.sh"
