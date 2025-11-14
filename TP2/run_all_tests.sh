#!/bin/bash

# run_all_tests.sh - Script Master para ejecutar todos los tests del TP2

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Banner
echo -e "${BOLD}${BLUE}"
echo "═══════════════════════════════════════════════════════════════════"
echo "  SUITE COMPLETA DE TESTS - TP2"
echo "  Sistema de Scraping y Análisis Web Distribuido"
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Verificar que estamos en el directorio correcto
if [ ! -f "server_scraping.py" ]; then
    echo -e "${RED}Error: Ejecutar desde el directorio TP2${NC}"
    exit 1
fi

# Verificar que los servidores están corriendo
echo -e "${YELLOW}Verificando que los servidores estén corriendo...${NC}"

SERVER_A_RUNNING=false
SERVER_B_RUNNING=false

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Servidor A (puerto 8000) - Corriendo"
    SERVER_A_RUNNING=true
else
    echo -e "  ${RED}✗${NC} Servidor A (puerto 8000) - NO responde"
fi

if nc -z localhost 8001 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Servidor B (puerto 8001) - Corriendo"
    SERVER_B_RUNNING=true
else
    echo -e "  ${RED}✗${NC} Servidor B (puerto 8001) - NO responde"
fi

if [ "$SERVER_A_RUNNING" = false ] || [ "$SERVER_B_RUNNING" = false ]; then
    echo ""
    echo -e "${YELLOW}${BOLD}Por favor inicia los servidores antes de ejecutar los tests:${NC}"
    echo ""
    echo -e "${CYAN}Terminal 1:${NC}"
    echo "  python server_processing.py -i localhost -p 8001 -n 4"
    echo ""
    echo -e "${CYAN}Terminal 2:${NC}"
    echo "  python server_scraping.py -i localhost -p 8000 --processing-host localhost --processing-port 8001"
    echo ""
    exit 1
fi

echo ""

# Array para guardar resultados
declare -a TEST_RESULTS

# Función para ejecutar un test
run_test() {
    local test_name=$1
    local test_script=$2
    local test_num=$3
    
    echo -e "${BOLD}${CYAN}┌────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${BOLD}${CYAN}│ TEST ${test_num}: ${test_name}${NC}"
    echo -e "${BOLD}${CYAN}└────────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    
    if python3 "$test_script"; then
        TEST_RESULTS+=("${test_name}:PASS")
        echo ""
        echo -e "${GREEN}${BOLD}✓ ${test_name} - PASADO${NC}"
    else
        TEST_RESULTS+=("${test_name}:FAIL")
        echo ""
        echo -e "${RED}${BOLD}✗ ${test_name} - FALLIDO${NC}"
    fi
    
    echo ""
    echo -e "${BOLD}Presiona ENTER para continuar al siguiente test...${NC}"
    read
}

# Ejecutar tests
run_test "Funcionalidad Básica" "tests/test_basic_functionality.py" "1"
run_test "Concurrencia" "tests/test_concurrency.py" "2"
run_test "Networking IPv4/IPv6" "tests/test_networking.py" "3"
run_test "Cumplimiento del Enunciado" "tests/test_compliance.py" "4"

# Resumen Final
echo -e "${BOLD}${BLUE}"
echo "═══════════════════════════════════════════════════════════════════"
echo "  RESUMEN FINAL DE TESTS"
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${NC}"

passed=0
failed=0

for result in "${TEST_RESULTS[@]}"; do
    test_name=$(echo "$result" | cut -d':' -f1)
    test_status=$(echo "$result" | cut -d':' -f2)
    
    if [ "$test_status" = "PASS" ]; then
        echo -e "  ${GREEN}✓ PASS${NC} | $test_name"
        ((passed++))
    else
        echo -e "  ${RED}✗ FAIL${NC} | $test_name"
        ((failed++))
    fi
done

total=$((passed + failed))
percentage=$((passed * 100 / total))

echo ""
echo -e "${BOLD}Tests ejecutados: $total${NC}"
echo -e "${GREEN}Pasados: $passed${NC}"
echo -e "${RED}Fallidos: $failed${NC}"
echo -e "${BOLD}Porcentaje: ${percentage}%${NC}"

echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}${BOLD}🎉 ¡TODOS LOS TESTS PASARON!${NC}"
    echo -e "${GREEN}${BOLD}El sistema cumple con todos los requisitos del TP2${NC}"
    exit_code=0
elif [ $percentage -ge 75 ]; then
    echo -e "${YELLOW}${BOLD}⚠ Mayoría de tests pasados${NC}"
    echo -e "${YELLOW}Revisar los tests fallidos para completar el sistema${NC}"
    exit_code=0
else
    echo -e "${RED}${BOLD}✗ Varios tests fallaron${NC}"
    echo -e "${RED}Se requieren correcciones importantes${NC}"
    exit_code=1
fi

echo -e "${BOLD}${BLUE}"
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${NC}"

exit $exit_code