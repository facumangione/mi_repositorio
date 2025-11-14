#!/bin/bash

# Script mejorado para reiniciar el sistema completo

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}"
echo "═══════════════════════════════════════════════════════════════════"
echo "  REINICIO COMPLETO DEL SISTEMA - TP2"
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${NC}"

# 1. Limpiar procesos anteriores
echo -e "${YELLOW}1️⃣ Limpiando procesos anteriores...${NC}"
pkill -9 -f "server_processing.py" 2>/dev/null
pkill -9 -f "server_scraping.py" 2>/dev/null
sleep 2

# 2. Liberar puertos
echo -e "${YELLOW}2️⃣ Liberando puertos 8000 y 8001...${NC}"
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8001 | xargs kill -9 2>/dev/null
sleep 1

# 3. Verificar que los puertos estén libres
echo -e "${YELLOW}3️⃣ Verificando puertos...${NC}"
if lsof -i:8000 > /dev/null 2>&1; then
    echo -e "${RED}❌ Puerto 8000 aún ocupado${NC}"
    exit 1
fi
if lsof -i:8001 > /dev/null 2>&1; then
    echo -e "${RED}❌ Puerto 8001 aún ocupado${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Puertos libres${NC}"
echo ""

# 4. Iniciar Servidor B en background
echo -e "${YELLOW}4️⃣ Iniciando Servidor B (Procesamiento)...${NC}"
cd ~/Escritorio/mi_repositorio/TP2
source venv/bin/activate

# Iniciar en background con logs
python server_processing.py -i 0.0.0.0 -p 8001 -n 4 > logs/server_b.log 2>&1 &
SERVER_B_PID=$!
echo -e "   PID: ${SERVER_B_PID}"
echo ${SERVER_B_PID} > /tmp/server_b.pid

# Esperar a que inicie
sleep 3

# Verificar que esté corriendo
if ! ps -p ${SERVER_B_PID} > /dev/null; then
    echo -e "${RED}❌ Servidor B falló al iniciar${NC}"
    cat logs/server_b.log
    exit 1
fi

if ! nc -z localhost 8001 2>/dev/null; then
    echo -e "${RED}❌ Servidor B no responde en puerto 8001${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Servidor B corriendo (PID ${SERVER_B_PID})${NC}"
echo ""

# 5. Iniciar Servidor A en background
echo -e "${YELLOW}5️⃣ Iniciando Servidor A (Scraping)...${NC}"
python server_scraping.py -i 0.0.0.0 -p 8000 --processing-host localhost --processing-port 8001 > logs/server_a.log 2>&1 &
SERVER_A_PID=$!
echo -e "   PID: ${SERVER_A_PID}"
echo ${SERVER_A_PID} > /tmp/server_a.pid

# Esperar a que inicie
sleep 3

# Verificar que esté corriendo
if ! ps -p ${SERVER_A_PID} > /dev/null; then
    echo -e "${RED}❌ Servidor A falló al iniciar${NC}"
    cat logs/server_a.log
    kill ${SERVER_B_PID} 2>/dev/null
    exit 1
fi

if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Servidor A no responde en puerto 8000${NC}"
    kill ${SERVER_A_PID} ${SERVER_B_PID} 2>/dev/null
    exit 1
fi
echo -e "${GREEN}✅ Servidor A corriendo (PID ${SERVER_A_PID})${NC}"
echo ""

# 6. Verificar comunicación entre servidores
echo -e "${YELLOW}6️⃣ Verificando comunicación entre servidores...${NC}"
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "\"available\": true"; then
    echo -e "${GREEN}✅ Servidores comunicándose correctamente${NC}"
else
    echo -e "${YELLOW}⚠️  Servidor B no disponible según health check${NC}"
    echo "$HEALTH" | jq .
fi
echo ""

# 7. Resumen
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}✅ SISTEMA INICIADO CORRECTAMENTE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}📡 Servidor A (Scraping):${NC}      http://localhost:8000 (PID ${SERVER_A_PID})"
echo -e "${CYAN}🔧 Servidor B (Procesamiento):${NC} localhost:8001 (PID ${SERVER_B_PID})"
echo ""
echo -e "${CYAN}📝 Logs:${NC}"
echo -e "   tail -f logs/server_a.log"
echo -e "   tail -f logs/server_b.log"
echo ""
echo -e "${CYAN}🛑 Para detener:${NC}"
echo -e "   kill ${SERVER_A_PID} ${SERVER_B_PID}"
echo -e "   # o"
echo -e "   ./stop_all.sh"
echo ""

# 8. Ofrecer ejecutar tests
echo -e "${YELLOW}¿Ejecutar tests ahora? (s/n):${NC} "
read -r response
if [[ "$response" == "s" || "$response" == "S" ]]; then
    echo ""
    echo -e "${YELLOW}Ejecutando tests...${NC}"
    ./run_all_tests.sh
fi