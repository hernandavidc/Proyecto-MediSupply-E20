#!/bin/bash
# Script para ejecutar TODAS las pruebas del order-service

echo "🧪 Ejecutando TODAS las pruebas del Order Service..."
echo ""

# Activar el entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ejecutar pytest con cobertura
pytest tests/ \
    --cov=app \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=xml \
    -v \
    "$@"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Todas las pruebas pasaron exitosamente"
    echo "📊 Reporte de cobertura generado en: htmlcov/index.html"
else
    echo "❌ Algunas pruebas fallaron (código de salida: $EXIT_CODE)"
fi

exit $EXIT_CODE

