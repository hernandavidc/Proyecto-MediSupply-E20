#!/bin/bash
# Script para ejecutar solo las pruebas de integración

echo "🧪 Ejecutando pruebas de integración del Order Service..."
echo ""

# Activar el entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ejecutar solo tests de integración
pytest tests/integration/ -v -m integration --cov=app "$@"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Todas las pruebas de integración pasaron"
else
    echo "❌ Algunas pruebas de integración fallaron"
fi

exit $EXIT_CODE

