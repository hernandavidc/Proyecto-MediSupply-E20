#!/bin/bash
# Script para construir imágenes Docker del supplier-service
# Incluye imagen principal e imagen de inicialización

set -e

echo "🏗️ Construyendo imágenes Docker para MediSupply Supplier Service..."

# Verificar que estamos en el directorio correcto
if [ ! -f "Dockerfile" ] || [ ! -f "Dockerfile.init" ]; then
    echo "❌ Error: Ejecutar desde el directorio medisupply-supplier-service"
    exit 1
fi

# Obtener variables de entorno
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
REGISTRY=${REGISTRY:-"us-central1-docker.pkg.dev"}
IMAGE_TAG=${IMAGE_TAG:-"latest"}

echo "📦 Configuración:"
echo "   - PROJECT_ID: $PROJECT_ID"
echo "   - REGISTRY: $REGISTRY"
echo "   - IMAGE_TAG: $IMAGE_TAG"

# Construir imagen principal
echo "🚀 Construyendo imagen principal..."
docker build -t $REGISTRY/$PROJECT_ID/medisupply/supplier-service:$IMAGE_TAG .

# Construir imagen de inicialización
echo "🔧 Construyendo imagen de inicialización..."
docker build -f Dockerfile.init -t $REGISTRY/$PROJECT_ID/medisupply/supplier-service-init:$IMAGE_TAG .

echo "✅ Imágenes construidas exitosamente:"
echo "   - $REGISTRY/$PROJECT_ID/medisupply/supplier-service:$IMAGE_TAG"
echo "   - $REGISTRY/$PROJECT_ID/medisupply/supplier-service-init:$IMAGE_TAG"

# Opcional: hacer push de las imágenes
if [ "$PUSH_IMAGES" = "true" ]; then
    echo "📤 Subiendo imágenes al registry..."
    docker push $REGISTRY/$PROJECT_ID/medisupply/supplier-service:$IMAGE_TAG
    docker push $REGISTRY/$PROJECT_ID/medisupply/supplier-service-init:$IMAGE_TAG
    echo "✅ Imágenes subidas exitosamente"
fi

echo "🎉 Construcción completada"
