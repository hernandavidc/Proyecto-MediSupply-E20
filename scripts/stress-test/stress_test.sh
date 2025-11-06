#!/bin/bash

# Script de Stress Testing para MediSupply
# Ejecuta múltiples requests a diferentes endpoints para estresar el sistema

BASE_URL="https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app/api/v1"
BASE_URL_NO_API="https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app"
ITERATIONS=5  # Número de iteraciones por ciclo
PARALLEL_REQUESTS=5  # Requests en paralelo

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "🔥 STRESS TEST - MediSupply API"
echo "=========================================="
echo "Base URL: $BASE_URL"
echo "Iteraciones por ciclo: $ITERATIONS"
echo "Requests en paralelo: $PARALLEL_REQUESTS"
echo "=========================================="
echo ""

# Función para hacer request y mostrar resultado
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local token=$4
    local description=$5
    
    local headers="-H 'Content-Type: application/json'"
    if [ ! -z "$token" ]; then
        headers="$headers -H 'Authorization: Bearer $token'"
    fi
    
    if [ "$method" = "GET" ]; then
        response=$(eval "curl -s -w '\n%{http_code}' -X GET '$BASE_URL$endpoint' $headers")
    else
        response=$(eval "curl -s -w '\n%{http_code}' -X $method '$BASE_URL$endpoint' $headers -d '$data'")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✅${NC} $description (HTTP $http_code)"
        return 0
    else
        echo -e "${RED}❌${NC} $description (HTTP $http_code)"
        echo "$body" | jq . 2>/dev/null || echo "$body"
        return 1
    fi
}

# Función para registrar usuario y retornar email
register_user() {
    local name=$1
    local email=$2
    local password=$3
    
    response=$(curl -s -X POST "$BASE_URL/users/register" \
        -H "Content-Type: application/json" \
        -d "{\"name\": \"$name\", \"email\": \"$email\", \"password\": \"$password\"}")
    
    if echo "$response" | jq -e '.id' > /dev/null 2>&1; then
        echo "$email"
        return 0
    fi
    return 1
}

# Función para obtener token
get_token() {
    local email=$1
    local password=$2
    
    response=$(curl -s -X POST "$BASE_URL/users/generate-token" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"$email\", \"password\": \"$password\"}")
    
    token=$(echo "$response" | jq -r '.access_token // empty' 2>/dev/null)
    echo "$token"
}

# Registrar algunos usuarios iniciales
echo "📝 Registrando usuarios iniciales..."
declare -a user_emails=()
for i in {1..5}; do
    email="testuser$i@mail.com"
    if register_user "Test User $i" "$email" "password123" > /dev/null 2>&1; then
        user_emails+=("$email")
        echo "✅ Usuario registrado: $email"
    else
        echo "⚠️  Usuario ya existe o error: $email"
        user_emails+=("$email")  # Intentar usar de todas formas
    fi
done
echo ""

# Obtener tokens para algunos usuarios
echo "🔑 Obteniendo tokens..."
declare -a tokens=()
for email in "${user_emails[@]:0:3}"; do
    token=$(get_token "$email" "password123")
    if [ ! -z "$token" ] && [ "$token" != "null" ]; then
        tokens+=("$token")
        echo "✅ Token obtenido para: $email"
    fi
done
echo ""

# Función para ejecutar un ciclo de stress test
run_stress_cycle() {
    local cycle=$1
    echo "=========================================="
    echo "🔄 CICLO $cycle - Ejecutando $ITERATIONS iteraciones"
    echo "=========================================="
    
    local success=0
    local failed=0
    
    for i in $(seq 1 $ITERATIONS); do
        echo ""
        echo "--- Iteración $i/$ITERATIONS ---"
        
        # 1. Consultar certificaciones
        if make_request "GET" "/certificaciones" "" "" "Consultar certificaciones"; then
            ((success++))
        else
            ((failed++))
        fi
        
        # 2. Consultar categorías
        if make_request "GET" "/categorias-suministros" "" "" "Consultar categorías"; then
            ((success++))
        else
            ((failed++))
        fi
        
        # 3. Consultar países
        if make_request "GET" "/paises" "" "" "Consultar países"; then
            ((success++))
        else
            ((failed++))
        fi
        
        # 4. Listar proveedores
        if make_request "GET" "/proveedores" "" "" "Listar proveedores"; then
            ((success++))
        else
            ((failed++))
        fi
        
        # 5. Listar productos
        if make_request "GET" "/productos" "" "" "Listar productos"; then
            ((success++))
        else
            ((failed++))
        fi
        
        # 6. Listar planes
        if make_request "GET" "/planes" "" "" "Listar planes"; then
            ((success++))
        else
            ((failed++))
        fi
        
        # 7. Health check (usa URL base sin /api/v1)
        response=$(curl -s -w '\n%{http_code}' -X GET "$BASE_URL_NO_API/health" -H 'Content-Type: application/json')
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | sed '$d')
        if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
            echo -e "${GREEN}✅${NC} Health check (HTTP $http_code)"
            ((success++))
        else
            echo -e "${RED}❌${NC} Health check (HTTP $http_code)"
            echo "$body" | jq . 2>/dev/null || echo "$body"
            ((failed++))
        fi
        
        # 8. Registrar nuevo usuario (cada 3 iteraciones)
        if [ $((i % 3)) -eq 0 ]; then
            email="stressuser$cycle-$i@test.com"
            if register_user "Stress User $cycle-$i" "$email" "password123" > /dev/null 2>&1; then
                echo -e "${GREEN}✅${NC} Usuario registrado: $email"
                ((success++))
            else
                echo -e "${YELLOW}⚠️${NC}  Usuario ya existe o error: $email"
                ((failed++))
            fi
        fi
        
        # 9. Generar token (si tenemos usuarios)
        if [ ${#user_emails[@]} -gt 0 ]; then
            random_email=${user_emails[$RANDOM % ${#user_emails[@]}]}
            token=$(get_token "$random_email" "password123")
            if [ ! -z "$token" ] && [ "$token" != "null" ]; then
                echo -e "${GREEN}✅${NC} Token generado para: $random_email"
                ((success++))
            else
                echo -e "${RED}❌${NC} Error generando token"
                ((failed++))
            fi
        fi
        
        # 10. Endpoints protegidos (si tenemos tokens)
        if [ ${#tokens[@]} -gt 0 ]; then
            random_token=${tokens[$RANDOM % ${#tokens[@]}]}
            if make_request "GET" "/users/me" "" "$random_token" "Obtener info usuario (protegido)"; then
                ((success++))
            else
                ((failed++))
            fi
        fi
        
        sleep 0.5  # Pequeña pausa entre requests
    done
    
    echo ""
    echo "=========================================="
    echo "📊 Resumen del Ciclo $cycle:"
    echo "   ✅ Exitosos: $success"
    echo "   ❌ Fallidos: $failed"
    echo "   📈 Total: $((success + failed))"
    echo "=========================================="
    echo ""
}

# Ejecutar múltiples ciclos
CYCLES=3
echo "🚀 Iniciando $CYCLES ciclos de stress test..."
echo ""

for cycle in $(seq 1 $CYCLES); do
    run_stress_cycle $cycle
    sleep 2  # Pausa entre ciclos
done

echo "=========================================="
echo "✨ Stress test completado"
echo "=========================================="

