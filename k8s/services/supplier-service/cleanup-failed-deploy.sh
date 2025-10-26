#!/bin/bash
# Script para limpiar el deployment fallido del supplier-service

echo "🧹 Limpiando deployment fallido del supplier-service..."

# Eliminar deployment actual
kubectl delete deployment supplier-service-deployment -n medisupply

# Esperar a que los pods terminen
sleep 10

echo "✅ Limpieza completada. El próximo deploy aplicará la configuración correcta."

