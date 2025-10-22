#!/bin/bash

# Test local deployment with Docker Compose
set -e

echo "🧪 Iniciando pruebas locales con Docker Compose..."

# Limpiar contenedores anteriores
echo "🧹 Limpiando contenedores anteriores..."
docker-compose down -v

# Construir y levantar servicios
echo "🔨 Construyendo y levantando servicios..."
docker-compose up --build -d

# Esperar que los servicios estén listos
echo "⏳ Esperando que los servicios estén listos..."
sleep 30

# Verificar estado de los servicios
echo "📊 Estado de los contenedores:"
docker-compose ps

# Probar endpoints
echo ""
echo "🔍 Probando endpoints..."

# User Service
echo "👤 Probando User Service..."
curl -f http://localhost:8001/health || echo "❌ User Service no responde"
curl -f http://localhost:8001/ || echo "❌ User Service root no responde"

# Supplier Service
echo "🏥 Probando Supplier Service..."
curl -f http://localhost:8010/healthz || echo "❌ Supplier Service no responde"
curl -f http://localhost:8010/ || echo "❌ Supplier Service root no responde"

# Probar algunos endpoints específicos
echo ""
echo "🔍 Probando endpoints específicos..."

# User Service endpoints
echo "👤 User Service - /api/v1/users:"
curl -s http://localhost:8001/api/v1/users | head -c 100 || echo "❌ Error"

# Supplier Service endpoints
echo "🏥 Supplier Service - /api/v1/proveedores:"
curl -s http://localhost:8010/api/v1/proveedores | head -c 100 || echo "❌ Error"

echo "🏥 Supplier Service - /api/v1/paises:"
curl -s http://localhost:8010/api/v1/paises | head -c 100 || echo "❌ Error"

echo ""
echo "✅ Pruebas completadas!"
echo ""
echo "📋 Servicios disponibles:"
echo "  - User Service: http://localhost:8001"
echo "  - Supplier Service: http://localhost:8010"
echo "  - User Service Docs: http://localhost:8001/docs"
echo "  - Supplier Service Docs: http://localhost:8010/docs"
echo ""
echo "🛑 Para detener los servicios: docker-compose down"