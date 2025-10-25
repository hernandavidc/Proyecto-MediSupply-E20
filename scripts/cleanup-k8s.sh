#!/bin/bash

# Script de limpieza pre-deploy para Kubernetes
set -e

echo "🧹 Iniciando limpieza pre-deploy..."

# 1. Eliminar deployments problemáticos
echo "🗑️ Eliminando deployments antiguos..."
kubectl delete deployment user-service-deployment -n medisupply --ignore-not-found=true
kubectl delete deployment supplier-service-deployment -n medisupply --ignore-not-found=true

# 2. Forzar eliminación de pods en Terminating
echo "🔄 Eliminando pods en estado Terminating..."
kubectl get pods -n medisupply --field-selector=status.phase=Terminating -o name | xargs -r kubectl delete --force --grace-period=0 || true

# 3. Esperar limpieza completa de servicios
echo "⏳ Esperando limpieza completa de servicios..."
kubectl wait --for=delete pod -l app=user-service -n medisupply --timeout=60s || true
kubectl wait --for=delete pod -l app=supplier-service -n medisupply --timeout=60s || true

# 4. ELIMINAR COMPLETAMENTE PostgreSQL y sus datos
echo "🗑️ Eliminando PostgreSQL completamente..."
kubectl delete deployment postgres-deployment -n medisupply --ignore-not-found=true
kubectl delete pvc postgres-pvc -n medisupply --ignore-not-found=true
kubectl delete secret postgres-secret -n medisupply --ignore-not-found=true
kubectl delete configmap postgres-init-scripts -n medisupply --ignore-not-found=true

# 5. Esperar eliminación completa de PostgreSQL
echo "⏳ Esperando eliminación completa de PostgreSQL..."
kubectl wait --for=delete pod -l app=postgres -n medisupply --timeout=60s || true

# 6. Esperar un poco más para asegurar limpieza
echo "⏳ Esperando limpieza completa..."
sleep 10

# 7. Verificar estado limpio
echo "✅ Verificando estado limpio..."
kubectl get pods -n medisupply
kubectl get pvc -n medisupply

echo "🎉 Limpieza completada. PostgreSQL será recreado desde cero en el próximo deploy."
