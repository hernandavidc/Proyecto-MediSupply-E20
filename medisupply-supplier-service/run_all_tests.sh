#!/bin/bash
# Script maestro para ejecutar todos los tipos de pruebas del bulk upload

set -e

echo "🧪 Ejecutando suite completa de pruebas para carga masiva de productos..."

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

# Instalar dependencias de testing
echo "📋 Instalando dependencias de testing..."
pip install pytest pytest-cov httpx

# Función para ejecutar pruebas con reporte
run_tests() {
    local test_type=$1
    local test_path=$2
    local report_dir=$3
    
    echo ""
    echo "🚀 Ejecutando pruebas $test_type..."
    echo "📁 Directorio: $test_path"
    
    if pytest "$test_path" -v --tb=short --cov=app --cov-report=html --cov-report=term-missing --cov-report=html:"$report_dir"; then
        echo "✅ Pruebas $test_type completadas exitosamente"
        echo "📊 Reporte disponible en $report_dir/index.html"
    else
        echo "❌ Pruebas $test_type fallaron"
        return 1
    fi
}

# Ejecutar pruebas unitarias
echo ""
echo "🔬 === PRUEBAS UNITARIAS ==="
run_tests "unitarias" "tests/unit/" "htmlcov_unit"

# Ejecutar pruebas de integración
echo ""
echo "🔗 === PRUEBAS DE INTEGRACIÓN ==="
run_tests "de integración" "tests/integration/" "htmlcov_integration"

# Ejecutar pruebas end-to-end
echo ""
echo "🌐 === PRUEBAS END-TO-END ==="
run_tests "end-to-end" "tests/e2e/" "htmlcov_e2e"

# Ejecutar todas las pruebas juntas para cobertura total
echo ""
echo "📈 === COBERTURA TOTAL ==="
echo "🎯 Ejecutando todas las pruebas para cobertura completa..."
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing --cov-report=html:htmlcov_total

echo ""
echo "🎉 === RESUMEN FINAL ==="
echo "✅ Todas las pruebas completadas exitosamente"
echo ""
echo "📊 Reportes de cobertura disponibles:"
echo "   - Unitarias: htmlcov_unit/index.html"
echo "   - Integración: htmlcov_integration/index.html"
echo "   - End-to-end: htmlcov_e2e/index.html"
echo "   - Total: htmlcov_total/index.html"
echo ""
echo "🧪 Tipos de pruebas ejecutadas:"
echo "   - Pruebas unitarias: Validación de funciones individuales"
echo "   - Pruebas de integración: Interacción entre componentes"
echo "   - Pruebas end-to-end: Flujo completo de usuario"
echo ""
echo "🚀 El sistema de carga masiva está completamente probado y listo para producción"
