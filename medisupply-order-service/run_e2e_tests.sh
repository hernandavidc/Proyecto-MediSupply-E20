#!/bin/bash
# Script para ejecutar solo las pruebas end-to-end

echo "🧪 Ejecutando pruebas end-to-end del Order Service..."
echo ""

# Activar el entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ejecutar solo tests e2e
pytest tests/e2e/ -v -m e2e --cov=app "$@"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Todas las pruebas e2e pasaron"
else
    echo "❌ Algunas pruebas e2e fallaron"
fi

exit $EXIT_CODE

