#!/bin/bash
# Script helper para ejecutar pruebas de performance

set -e

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
EDGE_PROXY_URL=${EDGE_PROXY_URL:-"https://medisupply-edge-proxy-n5jhaxtfma-uc.a.run.app"}

echo -e "${BLUE}🚀 MediSupply Performance Tests${NC}"
echo -e "${BLUE}================================${NC}\n"

# Verificar que estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Debes ejecutar este script desde el directorio performance-tests${NC}"
    exit 1
fi

# Función para mostrar menú
show_menu() {
    echo -e "${YELLOW}Selecciona el tipo de prueba:${NC}"
    echo "1) Response Time Tests (pytest-benchmark)"
    echo "2) Load Test - Ligero (10 usuarios, 1 min)"
    echo "3) Load Test - Medio (50 usuarios, 5 min)"
    echo "4) Load Test - Alto (100 usuarios, 10 min)"
    echo "5) Throughput Test - Órdenes (20 usuarios, 2 min)"
    echo "6) Ejecutar TODO (Response Time + Load Test Ligero)"
    echo "7) Instalar dependencias"
    echo "8) Salir"
    echo ""
    read -p "Opción: " choice
}

# Función para instalar dependencias
install_deps() {
    echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
    
    if [ ! -d "venv" ]; then
        echo "Creando entorno virtual..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencias instaladas${NC}\n"
}

# Función para response time tests
run_response_time_tests() {
    echo -e "${YELLOW}🧪 Ejecutando Response Time Tests...${NC}"
    echo -e "${BLUE}SLAs: Localización ≤1s, Rutas ≤3s, General ≤2s${NC}\n"
    
    source venv/bin/activate 2>/dev/null || true
    pytest test_response_time.py -v --benchmark-only
    
    echo -e "\n${GREEN}✅ Response Time Tests completados${NC}\n"
}

# Función para load tests
run_load_test() {
    local users=$1
    local spawn_rate=$2
    local run_time=$3
    local description=$4
    
    echo -e "${YELLOW}🔥 Ejecutando Load Test - ${description}${NC}"
    echo -e "${BLUE}Usuarios: ${users} | Spawn rate: ${spawn_rate}/s | Duración: ${run_time}${NC}\n"
    
    source venv/bin/activate 2>/dev/null || true
    locust -f locustfile.py \
        --host="${EDGE_PROXY_URL}" \
        --users ${users} \
        --spawn-rate ${spawn_rate} \
        --run-time ${run_time} \
        --headless
    
    echo -e "\n${GREEN}✅ Load Test completado${NC}\n"
}

# Función para throughput test
run_throughput_test() {
    echo -e "${YELLOW}📦 Ejecutando Throughput Test - Órdenes${NC}"
    echo -e "${BLUE}SLA: 100-400 órdenes/minuto${NC}\n"
    
    source venv/bin/activate 2>/dev/null || true
    locust -f locustfile.py \
        --host="${EDGE_PROXY_URL}" \
        --users 20 \
        --spawn-rate 5 \
        --run-time 2m \
        --headless \
        OrderCreationUser
    
    echo -e "\n${GREEN}✅ Throughput Test completado${NC}\n"
}

# Menú principal
while true; do
    show_menu
    
    case $choice in
        1)
            run_response_time_tests
            ;;
        2)
            run_load_test 10 2 "1m" "Ligero"
            ;;
        3)
            run_load_test 50 5 "5m" "Medio"
            ;;
        4)
            run_load_test 100 10 "10m" "Alto"
            ;;
        5)
            run_throughput_test
            ;;
        6)
            echo -e "${BLUE}🎯 Ejecutando suite completa de pruebas...${NC}\n"
            run_response_time_tests
            sleep 2
            run_load_test 10 2 "1m" "Ligero"
            echo -e "\n${GREEN}🎉 Suite completa finalizada${NC}\n"
            ;;
        7)
            install_deps
            ;;
        8)
            echo -e "${GREEN}👋 ¡Hasta luego!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Opción inválida${NC}\n"
            ;;
    esac
    
    read -p "Presiona Enter para continuar..."
    clear
done

