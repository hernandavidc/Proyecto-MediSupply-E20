#!/bin/bash

# Script para generar credenciales seguras para deploy manual
set -e

echo "🔐 Generando credenciales seguras..."

# Generar credenciales aleatorias
DB_USER="medisupply_$(openssl rand -hex 4)"
DB_PASSWORD="$(openssl rand -base64 32 | tr -d '=/+' | cut -c1-25)"
JWT_SECRET="$(openssl rand -hex 32)"

echo "✅ Credenciales generadas:"
echo "   - Usuario DB: $DB_USER"
echo "   - Password DB: [OCULTO]"
echo "   - JWT Secret: [OCULTO]"

# Crear archivos temporales con credenciales seguras
echo "📝 Aplicando credenciales a manifiestos..."

# Copiar archivos originales a temporales
cp k8s/database/postgres-secret.yaml k8s/database/postgres-secret.tmp.yaml
cp k8s/services/user-service/user-service-secret.yaml k8s/services/user-service/user-service-secret.tmp.yaml

# Reemplazar placeholders en archivos temporales
sed -i.bak "s/__POSTGRES_USER__/$DB_USER/g" k8s/database/postgres-secret.tmp.yaml
sed -i.bak "s/__POSTGRES_PASSWORD__/$DB_PASSWORD/g" k8s/database/postgres-secret.tmp.yaml
sed -i.bak "s/__POSTGRES_USER__/$DB_USER/g" k8s/services/user-service/user-service-secret.tmp.yaml
sed -i.bak "s/__POSTGRES_PASSWORD__/$DB_PASSWORD/g" k8s/services/user-service/user-service-secret.tmp.yaml
sed -i.bak "s/__JWT_SECRET_KEY__/$JWT_SECRET/g" k8s/services/user-service/user-service-secret.tmp.yaml

# Limpiar archivos backup
rm -f k8s/database/postgres-secret.tmp.yaml.bak
rm -f k8s/services/user-service/user-service-secret.tmp.yaml.bak

echo "🎯 Para aplicar las credenciales seguras:"
echo "   kubectl apply -f k8s/database/postgres-secret.tmp.yaml"
echo "   kubectl apply -f k8s/services/user-service/user-service-secret.tmp.yaml"
echo ""
echo "⚠️  Los archivos .tmp.yaml contienen credenciales sensibles"
echo "   NO los subas al repositorio. Se eliminarán automáticamente."

# Función de limpieza
cleanup() {
    echo "🧹 Limpiando archivos temporales..."
    rm -f k8s/database/postgres-secret.tmp.yaml
    rm -f k8s/services/user-service/user-service-secret.tmp.yaml
}

# Registrar función de limpieza al salir
trap cleanup EXIT
