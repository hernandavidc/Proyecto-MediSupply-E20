#!/bin/bash

# Script para simular la ejecución de GitHub Actions localmente
# Útil para probar antes de hacer push

set -e  # Salir si cualquier comando falla

echo "🧪 Simulando GitHub Actions - Tests de Microservicios"
echo "================================================="

# Detectar cambios (simulado)
echo "🔍 Detectando cambios en servicios..."

# Verificar si hay cambios en user-service
if git diff --name-only HEAD~1 2>/dev/null | grep -q "^user-service/" || [ "$1" == "force-user" ]; then
    echo "  ✅ Cambios detectados en user-service"
    USER_SERVICE_CHANGED=true
else
    echo "  ⏭️  Sin cambios en user-service"
    USER_SERVICE_CHANGED=false
fi

# Simular otros servicios
echo "  ⏭️  inventory-service: Próximamente"
echo "  ⏭️  order-service: Próximamente"

echo ""

# Ejecutar tests de user-service si hay cambios
if [ "$USER_SERVICE_CHANGED" == "true" ]; then
    echo "🧪 Ejecutando tests de User Service..."
    echo "======================================="
    
    cd user-service
    
    # Verificar si existe el entorno virtual
    if [ ! -d "venv" ]; then
        echo "📦 Creando entorno virtual..."
        python3 -m venv venv
    fi
    
    echo "📦 Activando entorno virtual..."
    source venv/bin/activate
    
    echo "📦 Instalando dependencias..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    echo "🧪 Ejecutando tests..."
    export DATABASE_URL="sqlite:///./test.db"
    export SECRET_KEY="test_secret_key_for_testing_only"
    
    # Ejecutar tests con pytest directamente
    pytest tests/ -v --cov=app --cov-report=term-missing
    TEST_RESULT=$?
    
    cd ..
    
    if [ $TEST_RESULT -eq 0 ]; then
        echo "✅ Tests de User Service completados exitosamente"
        USER_SERVICE_RESULT="success"
    else
        echo "❌ Tests de User Service fallaron"
        USER_SERVICE_RESULT="failure"
    fi
else
    echo "⏭️  Tests de User Service omitidos (sin cambios)"
    USER_SERVICE_RESULT="skipped"
fi

echo ""
echo "📊 Resumen de Resultados"
echo "======================="

# Mostrar resumen similar al que aparecería en el PR
echo "### 📋 Servicios Analizados"
echo ""

if [ "$USER_SERVICE_RESULT" == "success" ]; then
    echo "- **👤 User Service**: ✅ Todos los tests pasaron"
elif [ "$USER_SERVICE_RESULT" == "failure" ]; then
    echo "- **👤 User Service**: ❌ Tests fallaron"
elif [ "$USER_SERVICE_RESULT" == "skipped" ]; then
    echo "- **👤 User Service**: ⏭️ Sin cambios - Tests omitidos"
fi

echo "- **📦 Inventory Service**: ⏭️ Próximamente"
echo "- **🛒 Order Service**: ⏭️ Próximamente"
echo ""

# Determinar estado general
if [ "$USER_SERVICE_RESULT" == "failure" ]; then
    echo "🔴 **ESTADO GENERAL: FALLÓ**"
    echo ""
    echo "❌ Algunos tests fallaron - El merge estaría bloqueado"
    echo ""
    echo "### 🔧 Para corregir:"
    echo "1. Revisa los errores mostrados arriba"
    echo "2. Ejecuta: cd user-service && pytest tests/ -v"
    echo "3. Corrige los errores y vuelve a probar"
    exit 1
elif [ "$USER_SERVICE_CHANGED" == "true" ]; then
    echo "🟢 **ESTADO GENERAL: EXITOSO**"
    echo ""
    echo "✅ Todos los tests pasaron - El PR estaría listo para merge"
else
    echo "🟡 **ESTADO GENERAL: SIN CAMBIOS**"
    echo ""
    echo "⏭️ No se detectaron cambios que requieran tests"
fi

echo ""
echo "🎉 Simulación completada"
