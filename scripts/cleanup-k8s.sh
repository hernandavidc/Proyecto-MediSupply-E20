#!/bin/bash

# Script de limpieza pre-deploy para Kubernetes
# Optimizado para reducir tiempos de espera y forzar limpieza
set +e  # No fallar en errores, continuar limpieza

echo "🧹 Iniciando limpieza pre-deploy..."

# 1. Eliminar deployments con grace period reducido
echo "🗑️ Eliminando deployments antiguos..."
kubectl delete deployment user-service-deployment -n medisupply --grace-period=5 --timeout=10s --ignore-not-found=true 2>/dev/null || true
kubectl delete deployment supplier-service-deployment -n medisupply --grace-period=5 --timeout=10s --ignore-not-found=true 2>/dev/null || true
kubectl delete deployment client-service-deployment -n medisupply --grace-period=5 --timeout=10s --ignore-not-found=true 2>/dev/null || true

# 2. Forzar eliminación inmediata de pods problemáticos
echo "🔄 Forzando eliminación de pods en estado Terminating..."
PODS=$(kubectl get pods -n medisupply --field-selector=status.phase=Terminating -o name 2>/dev/null || echo "")
if [ ! -z "$PODS" ]; then
  echo "$PODS" | xargs -r kubectl delete --force --grace-period=0 --timeout=5s 2>/dev/null || true
fi

# 3. Esperar brevemente (con timeout corto) - no bloquear si no termina
echo "⏳ Esperando terminación de pods (timeout 15s)..."
kubectl wait --for=delete pod -l app=user-service -n medisupply --timeout=15s 2>/dev/null || true
kubectl wait --for=delete pod -l app=supplier-service -n medisupply --timeout=15s 2>/dev/null || true
kubectl wait --for=delete pod -l app=client-service -n medisupply --timeout=15s 2>/dev/null || true

# 4. Forzar eliminación final de pods que aún estén presentes
echo "🗑️ Eliminación forzada de pods restantes..."
kubectl delete pods -l app=user-service -n medisupply --force --grace-period=0 --ignore-not-found=true 2>/dev/null || true
kubectl delete pods -l app=supplier-service -n medisupply --force --grace-period=0 --ignore-not-found=true 2>/dev/null || true
kubectl delete pods -l app=client-service -n medisupply --force --grace-period=0 --ignore-not-found=true 2>/dev/null || true

# 5. ELIMINAR PostgreSQL y sus datos (sin esperar mucho)
echo "🗑️ Eliminando PostgreSQL completamente..."
kubectl delete deployment postgres-deployment -n medisupply --grace-period=5 --timeout=10s --ignore-not-found=true 2>/dev/null || true
kubectl delete pvc postgres-pvc -n medisupply --timeout=10s --ignore-not-found=true 2>/dev/null || true
kubectl delete secret postgres-secret -n medisupply --ignore-not-found=true 2>/dev/null || true
kubectl delete configmap postgres-init-scripts -n medisupply --ignore-not-found=true 2>/dev/null || true

# 6. Forzar eliminación de pods de PostgreSQL si están atascados
kubectl delete pods -l app=postgres -n medisupply --force --grace-period=0 --ignore-not-found=true 2>/dev/null || true

# 7. Esperar solo unos segundos (no bloquear)
echo "⏳ Esperando 5 segundos para limpieza final..."
sleep 5

# 8. Mostrar estado actual (sin fallar si hay pods restantes)
echo "📊 Estado actual del namespace:"
kubectl get pods -n medisupply 2>/dev/null || true
kubectl get pvc -n medisupply 2>/dev/null || true

echo "✅ Limpieza completada. Continuando con el deploy..."
