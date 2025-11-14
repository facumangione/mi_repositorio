#!/bin/bash

# Script de Diagnóstico para TP2

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          DIAGNÓSTICO DE SISTEMA - TP2                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Función para verificar puerto
check_port() {
    local port=$1
    local name=$2
    
    if lsof -i:$port > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Puerto $port ($name) - ACTIVO"
        lsof -i:$port | grep LISTEN | awk '{print "  PID:", $2, "Comando:", $1}'
        return 0
    else
        echo -e "${RED}✗${NC} Puerto $port ($name) - NO ACTIVO"
        return 1
    fi
}

# Función para test de conectividad
test_connection() {
    local host=$1
    local port=$2
    local name=$3
    
    if nc -z -w1 $host $port 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Conectividad a $name ($host:$port)"
        return 0
    else
        echo -e "${RED}✗${NC} No se puede conectar a $name ($host:$port)"
        return 1
    fi
}

# Función para test HTTP
test_http() {
    local url=$1
    local name=$2
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "200" ] || [ "$response" = "503" ]; then
        echo -e "${GREEN}✓${NC} HTTP $name - Status: $response"
        return 0
    else
        echo -e "${RED}✗${NC} HTTP $name - Status: $response (esperado 200 o 503)"
        return 1
    fi
}

echo "═══════════════════════════════════════════════════════════"
echo "1. VERIFICACIÓN DE PUERTOS"
echo "═══════════════════════════════════════════════════════════"
echo ""

check_port 8000 "Servidor A"
server_a_running=$?

check_port 8001 "Servidor B"
server_b_running=$?

echo ""

# Si los servidores no están corriendo, mostrar cómo iniciarlos
if [ $server_a_running -ne 0 ] || [ $server_b_running -ne 0 ]; then
    echo -e "${YELLOW}⚠ SERVIDORES NO ESTÁN CORRIENDO${NC}"
    echo ""
    echo "Para iniciar los servidores, abre dos terminales:"
    echo ""
    echo -e "${BLUE}TERMINAL 1 (Servidor B):${NC}"
    echo "  cd ~/Escritorio/mi_repositorio/TP2"
    echo "  source venv/bin/activate"
    echo "  python server_processing.py -i localhost -p 8001 -n 4"
    echo ""
    echo -e "${BLUE}TERMINAL 2 (Servidor A):${NC}"
    echo "  cd ~/Escritorio/mi_repositorio/TP2"
    echo "  source venv/bin/activate"
    echo "  python server_scraping.py -i localhost -p 8000 --processing-host localhost --processing-port 8001"
    echo ""
    exit 1
fi

echo "═══════════════════════════════════════════════════════════"
echo "2. PRUEBAS DE CONECTIVIDAD"
echo "═══════════════════════════════════════════════════════════"
echo ""

test_connection localhost 8000 "Servidor A"
test_connection localhost 8001 "Servidor B"
test_connection 127.0.0.1 8000 "Servidor A (loopback)"
test_connection 127.0.0.1 8001 "Servidor B (loopback)"

echo ""

echo "═══════════════════════════════════════════════════════════"
echo "3. PRUEBAS HTTP"
echo "═══════════════════════════════════════════════════════════"
echo ""

test_http "http://localhost:8000/health" "Health Check"
test_http "http://localhost:8000/info" "Info Endpoint"

echo ""

echo "═══════════════════════════════════════════════════════════"
echo "4. PRUEBA DE SCRAPING BÁSICO"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "Probando scraping de http://example.com..."
response=$(curl -s "http://localhost:8000/scrape?url=http://example.com" 2>/dev/null)

if [ -z "$response" ]; then
    echo -e "${RED}✗${NC} No se recibió respuesta del servidor"
else
    # Verificar que sea JSON válido
    if echo "$response" | jq . > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Respuesta JSON válida recibida"
        
        # Verificar campos críticos
        status=$(echo "$response" | jq -r '.status' 2>/dev/null)
        has_scraping=$(echo "$response" | jq 'has("scraping_data")' 2>/dev/null)
        has_processing=$(echo "$response" | jq 'has("processing_data")' 2>/dev/null)
        has_performance=$(echo "$response" | jq '.processing_data | has("performance")' 2>/dev/null)
        
        echo "  Status: $status"
        
        if [ "$has_scraping" = "true" ]; then
            echo -e "  ${GREEN}✓${NC} scraping_data presente"
        else
            echo -e "  ${RED}✗${NC} scraping_data faltante"
        fi
        
        if [ "$has_processing" = "true" ]; then
            echo -e "  ${GREEN}✓${NC} processing_data presente"
        else
            echo -e "  ${RED}✗${NC} processing_data faltante"
        fi
        
        if [ "$has_performance" = "true" ]; then
            echo -e "  ${GREEN}✓${NC} performance data presente"
            
            # Mostrar datos de performance
            load_time=$(echo "$response" | jq -r '.processing_data.performance.load_time_ms' 2>/dev/null)
            size=$(echo "$response" | jq -r '.processing_data.performance.total_size_kb' 2>/dev/null)
            
            if [ "$load_time" != "null" ] && [ "$load_time" != "" ]; then
                echo "    Load time: ${load_time}ms"
            fi
            
            if [ "$size" != "null" ] && [ "$size" != "" ]; then
                echo "    Total size: ${size}KB"
            fi
        else
            echo -e "  ${YELLOW}⚠${NC} performance data faltante o es null"
            
            # Verificar si hay error
            perf_error=$(echo "$response" | jq -r '.processing_data.performance_error' 2>/dev/null)
            if [ "$perf_error" != "null" ] && [ "$perf_error" != "" ]; then
                echo -e "  ${RED}Error:${NC} $perf_error"
            fi
        fi
        
    else
        echo -e "${RED}✗${NC} Respuesta no es JSON válido"
        echo "Primeros 200 caracteres de la respuesta:"
        echo "$response" | head -c 200
    fi
fi

echo ""

echo "═══════════════════════════════════════════════════════════"
echo "5. PRUEBA DE COMUNICACIÓN SOCKET"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Test simple de socket usando Python
python3 << 'EOF'
import socket
import sys
import json
import struct

def test_socket():
    try:
        # Conectar
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('localhost', 8001))
        
        # Enviar PING simple
        ping = {"type": "ping"}
        json_data = json.dumps(ping).encode('utf-8')
        length = len(json_data)
        header = struct.pack('!I', length)
        sock.sendall(header + json_data)
        
        # Recibir respuesta
        header = sock.recv(4)
        if len(header) < 4:
            print("✗ Respuesta incompleta")
            return False
            
        length = struct.unpack('!I', header)[0]
        data = b''
        while len(data) < length:
            chunk = sock.recv(min(4096, length - len(data)))
            if not chunk:
                break
            data += chunk
        
        response = json.loads(data.decode('utf-8'))
        
        if response.get('success'):
            print("✓ Socket PING exitoso")
            print(f"  Respuesta: {response.get('result', {})}")
            return True
        else:
            print("✗ Socket PING falló")
            print(f"  Error: {response.get('error', 'Unknown')}")
            return False
            
    except ConnectionRefusedError:
        print("✗ Conexión rechazada - Servidor B no responde")
        return False
    except socket.timeout:
        print("✗ Timeout - Servidor B no respondió a tiempo")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        try:
            sock.close()
        except:
            pass

if test_socket():
    sys.exit(0)
else:
    sys.exit(1)
EOF

socket_test=$?

if [ $socket_test -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Comunicación socket funcionando"
else
    echo -e "${RED}✗${NC} Problema con comunicación socket"
fi

echo ""

echo "═══════════════════════════════════════════════════════════"
echo "6. RESUMEN"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Contar tests pasados
tests_passed=0
tests_total=5

[ $server_a_running -eq 0 ] && ((tests_passed++))
[ $server_b_running -eq 0 ] && ((tests_passed++))

# Conectividad básica
nc -z -w1 localhost 8000 > /dev/null 2>&1 && ((tests_passed++))

# HTTP health
curl -s "http://localhost:8000/health" > /dev/null 2>&1 && ((tests_passed++))

# Socket test
[ $socket_test -eq 0 ] && ((tests_passed++))

percentage=$((tests_passed * 100 / tests_total))

echo "Tests pasados: $tests_passed/$tests_total ($percentage%)"
echo ""

if [ $percentage -eq 100 ]; then
    echo -e "${GREEN}✓ SISTEMA FUNCIONANDO CORRECTAMENTE${NC}"
    echo ""
    echo "Puedes ejecutar los tests completos con:"
    echo "  ./run_all_tests.sh"
elif [ $percentage -ge 60 ]; then
    echo -e "${YELLOW}⚠ SISTEMA PARCIALMENTE FUNCIONAL${NC}"
    echo ""
    echo "Revisa los errores arriba y verifica:"
    echo "  1. Que ambos servidores estén corriendo"
    echo "  2. Que no haya errores en los logs"
    echo "  3. Que los puertos no estén bloqueados"
else
    echo -e "${RED}✗ SISTEMA CON PROBLEMAS GRAVES${NC}"
    echo ""
    echo "Acciones recomendadas:"
    echo "  1. Reiniciar ambos servidores"
    echo "  2. Verificar logs en cada terminal"
    echo "  3. Ejecutar: ./restart_all.sh"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"