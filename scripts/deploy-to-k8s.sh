#!/bin/bash

# Deploy completo a Kubernetes
set -e

echo "🚀 Iniciando deploy a GKE..."

# Aplicar namespace
echo "📋 Creando namespace..."
kubectl apply -f k8s/namespace.yaml

# Deploy de base de datos
echo "🗄️ Desplegando PostgreSQL..."
kubectl apply -f k8s/database/

# Esperar que postgres esté listo
echo "⏳ Esperando PostgreSQL..."
kubectl wait --for=condition=Ready pod -l app=postgres -n medisupply --timeout=300s

# Deploy de servicios
echo "🔧 Desplegando user-service..."
kubectl apply -f k8s/services/user-service/

# Esperar que el servicio esté listo
echo "⏳ Esperando user-service..."
kubectl wait --for=condition=Ready pod -l app=user-service -n medisupply --timeout=300s

# Deploy del ingress
echo "🌐 Desplegando ingress..."
kubectl apply -f k8s/ingress/

echo "✅ Deploy completado!"
echo ""
echo "📊 Estado de los pods:"
kubectl get pods -n medisupply

echo ""
echo "🌐 Ingress:"
kubectl get ingress -n medisupply

echo ""
echo "🔗 Servicios:"
kubectl get services -n medisupply

echo ""
echo "📋 Para obtener la IP externa del Load Balancer:"
echo "kubectl get ingress medisupply-ingress -n medisupply"
