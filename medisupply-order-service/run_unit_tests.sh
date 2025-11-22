#!/bin/bash
# Script para ejecutar solo las pruebas unitarias

echo "🧪 Ejecutando pruebas unitarias del Order Service..."
echo ""

# Activar el entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ejecutar solo tests unitarios
pytest tests/unit/ -v -m unit --cov=app "$@"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Todas las pruebas unitarias pasaron"
else
    echo "❌ Algunas pruebas unitarias fallaron"
fi

exit $EXIT_CODE

