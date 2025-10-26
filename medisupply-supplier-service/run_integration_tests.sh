#!/bin/bash
# Script para ejecutar pruebas de integración del bulk upload

set -e

echo "🧪 Ejecutando pruebas de integración para carga masiva de productos..."

# Verificar que estamos en el directorio correcto
if [ ! -f "pytest.ini" ]; then
    echo "❌ Error: Ejecutar desde el directorio medisupply-supplier-service"
    exit 1
fi

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "📦 Activando entorno virtual..."
    source venv/bin/activate
fi

# Instalar dependencias de testing si no están instaladas
echo "📋 Verificando dependencias..."
pip install pytest pytest-cov httpx

# Ejecutar pruebas de integración
echo "🚀 Ejecutando pruebas de integración..."

# Ejecutar pruebas específicas de bulk upload
echo "📊 Ejecutando tests de bulk upload..."
pytest tests/integration/test_bulk_upload_integration.py -v --tb=short

# Ejecutar todas las pruebas de integración
echo "🎯 Ejecutando todas las pruebas de integración..."
pytest tests/integration/ -v --tb=short

# Generar reporte de cobertura
echo "📈 Generando reporte de cobertura..."
pytest tests/integration/ --cov=app --cov-report=html --cov-report=term-missing

echo "✅ Pruebas de integración completadas"
echo "📊 Reporte de cobertura disponible en htmlcov/index.html"
