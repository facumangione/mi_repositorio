#!/bin/bash

# Script de reinicio con verificación mejorada

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          REINICIO COMPLETO DEL SISTEMA - TP2               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "server_scraping.py" ]; then
    echo -e "${RED}✗ Error: Ejecutar desde el directorio TP2${NC}"
    exit 1
fi

# Activar entorno virtual
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠ Entorno virtual no encontrado${NC}"
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo "PASO 1: Limpiando procesos anteriores"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Matar procesos Python relacionados
pkill -9 -f "server_processing.py" 2>/dev/null
pkill -9 -f "server_scraping.py" 2>/dev/null

# Liberar puertos
for port in 8000 8001; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "Matando proceso en puerto $port (PID: $pid)"
        kill -9 $pid 2>/dev/null
    fi
done

sleep 2

# Verificar que los puertos estén libres
ports_free=true
for port in 8000 8001; do
    if lsof -i:$port > /dev/null 2>&1; then
        echo -e "${RED}✗ Puerto $port todavía ocupado${NC}"
        ports_free=false
    else
        echo -e "${GREEN}✓ Puerto $port libre${NC}"
    fi
done

if [ "$ports_free" = false ]; then
    echo -e "${RED}Error: No se pudieron liberar todos los puertos${NC}"
    exit 1
fi

echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo "PASO 2: Verificando archivos corregidos"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Verificar que los archivos clave existen
files_ok=true
required_files=(
    "server_processing.py"
    "server_scraping.py"
    "api/processing_client.py"
    "processor/performance.py"
    "processor/worker_pool.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file - FALTANTE"
        files_ok=false
    fi
done

if [ "$files_ok" = false ]; then
    echo -e "${RED}Error: Faltan archivos requeridos${NC}"
    exit 1
fi

echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo "PASO 3: Iniciando servidores en segundo plano"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Crear directorio para logs si no existe
mkdir -p logs

# Iniciar Servidor B (procesamiento)
echo "Iniciando Servidor B (procesamiento) en puerto 8001..."
python server_processing.py -i localhost -p 8001 -n 4 > logs/server_b.log 2>&1 &
SERVER_B_PID=$!
echo "  PID: $SERVER_B_PID"

# Esperar a que el servidor B inicie
sleep 3

# Verificar que el servidor B esté corriendo
if ! ps -p $SERVER_B_PID > /dev/null; then
    echo -e "${RED}✗ Servidor B falló al iniciar${NC}"
    echo "Ver logs/server_b.log para detalles"
    exit 1
fi

if ! nc -z localhost 8001 2>/dev/null; then
    echo -e "${RED}✗ Servidor B no responde en puerto 8001${NC}"
    kill -9 $SERVER_B_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Servidor B corriendo${NC}"
echo ""

# Iniciar Servidor A (scraping)
echo "Iniciando Servidor A (scraping) en puerto 8000..."
python server_scraping.py -i localhost -p 8000 --processing-host localhost --processing-port 8001 > logs/server_a.log 2>&1 &
SERVER_A_PID=$!
echo "  PID: $SERVER_A_PID"

# Esperar a que el servidor A inicie
sleep 3

# Verificar que el servidor A esté corriendo
if ! ps -p $SERVER_A_PID > /dev/null; then
    echo -e "${RED}✗ Servidor A falló al iniciar${NC}"
    echo "Ver logs/server_a.log para detalles"
    kill -9 $SERVER_B_PID 2>/dev/null
    exit 1
fi

if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}✗ Servidor A no responde en puerto 8000${NC}"
    kill -9 $SERVER_A_PID $SERVER_B_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✓ Servidor A corriendo${NC}"
echo ""

# Guardar PIDs para poder detenerlos después
echo "$SERVER_A_PID" > logs/server_a.pid
echo "$SERVER_B_PID" > logs/server_b.pid

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo "PASO 4: Verificando conectividad entre servidores"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Esperar un poco más para asegurar que todo esté listo
sleep 2

# Verificar health de Servidor A
health_response=$(curl -s http://localhost:8000/health)
processing_available=$(echo "$health_response" | jq -r '.processing_server.available' 2>/dev/null)

if [ "$processing_available" = "true" ]; then
    echo -e "${GREEN}✓ Servidor A puede comunicarse con Servidor B${NC}"
else
    echo -e "${YELLOW}⚠ Servidor A no puede comunicarse con Servidor B${NC}"
    echo "  Esto puede causar que algunos tests fallen"
    echo "  Respuesta health:"
    echo "$health_response" | jq . 2>/dev/null || echo "$health_response"
fi

echo ""

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo "PASO 5: Prueba rápida del sistema"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

echo "Realizando scraping de prueba..."
test_response=$(curl -s "http://localhost:8000/scrape?url=http://example.com")

if [ -z "$test_response" ]; then
    echo -e "${RED}✗ No se recibió respuesta${NC}"
else
    # Verificar que sea JSON válido
    if echo "$test_response" | jq . > /dev/null 2>&1; then
        status=$(echo "$test_response" | jq -r '.status')
        has_perf=$(echo "$test_response" | jq 'has("processing_data") and (.processing_data | has("performance"))')
        
        if [ "$status" = "success" ]; then
            echo -e "${GREEN}✓ Scraping exitoso${NC}"
            
            if [ "$has_perf" = "true" ]; then
                echo -e "${GREEN}✓ Datos de performance presentes${NC}"
            else
                echo -e "${YELLOW}⚠ Datos de performance faltantes${NC}"
            fi
        else
            echo -e "${YELLOW}⚠ Scraping completó con errores${NC}"
        fi
    else
        echo -e "${RED}✗ Respuesta no es JSON válido${NC}"
    fi
fi

echo ""

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              SISTEMA INICIADO                              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✓ Ambos servidores corriendo en segundo plano${NC}"
echo ""
echo "PIDs:"
echo "  Servidor A (8000): $SERVER_A_PID"
echo "  Servidor B (8001): $SERVER_B_PID"
echo ""
echo "Logs:"
echo "  Servidor A: logs/server_a.log"
echo "  Servidor B: logs/server_b.log"
echo ""
echo "Comandos útiles:"
echo "  Ver logs A: tail -f logs/server_a.log"
echo "  Ver logs B: tail -f logs/server_b.log"
echo "  Detener todo: ./stop_servers.sh"
echo "  Ejecutar tests: ./run_all_tests.sh"
echo "  Diagnóstico: ./diagnose.sh"
echo ""

# Preguntar si quiere ejecutar tests
read -p "¿Ejecutar tests ahora? (s/n): " run_tests

if [ "$run_tests" = "s" ] || [ "$run_tests" = "S" ]; then
    echo ""
    sleep 2
    ./run_all_tests.sh
fi