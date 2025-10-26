#!/bin/bash
# Script para ejecutar pruebas end-to-end (e2e) del bulk upload

set -e

echo "🧪 Ejecutando pruebas end-to-end para carga masiva de productos..."

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

# Ejecutar pruebas end-to-end
echo "🚀 Ejecutando pruebas end-to-end..."

# Ejecutar tests e2e específicos
echo "📊 Ejecutando tests e2e de bulk upload..."
pytest tests/e2e/test_bulk_upload_e2e.py -v --tb=short

# Ejecutar todas las pruebas e2e
echo "🎯 Ejecutando todas las pruebas e2e..."
pytest tests/e2e/ -v --tb=short

# Generar reporte de cobertura específico para e2e
echo "📈 Generando reporte de cobertura e2e..."
pytest tests/e2e/ --cov=app --cov-report=html --cov-report=term-missing --cov-report=html:htmlcov_e2e

echo "✅ Pruebas end-to-end completadas"
echo "📊 Reporte de cobertura e2e disponible en htmlcov_e2e/index.html"
