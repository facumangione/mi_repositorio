#!/bin/bash

# Script para detener todos los servidores

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🛑 Deteniendo servidores..."
echo ""

# Intentar detener usando PIDs guardados
if [ -f "logs/server_a.pid" ]; then
    pid=$(cat logs/server_a.pid)
    if ps -p $pid > /dev/null 2>&1; then
        echo "Deteniendo Servidor A (PID: $pid)..."
        kill $pid 2>/dev/null
        sleep 1
        # Si no se detuvo, forzar
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null
        fi
        echo -e "${GREEN}✓ Servidor A detenido${NC}"
    fi
    rm -f logs/server_a.pid
fi

if [ -f "logs/server_b.pid" ]; then
    pid=$(cat logs/server_b.pid)
    if ps -p $pid > /dev/null 2>&1; then
        echo "Deteniendo Servidor B (PID: $pid)..."
        kill $pid 2>/dev/null
        sleep 1
        # Si no se detuvo, forzar
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null
        fi
        echo -e "${GREEN}✓ Servidor B detenido${NC}"
    fi
    rm -f logs/server_b.pid
fi

# Matar todos los procesos relacionados por si acaso
pkill -f "server_processing.py" 2>/dev/null
pkill -f "server_scraping.py" 2>/dev/null

# Liberar puertos
for port in 8000 8001; do
    pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "Liberando puerto $port..."
        kill -9 $pid 2>/dev/null
    fi
done

sleep 1

# Verificar que todo esté detenido
all_stopped=true

for port in 8000 8001; do
    if lsof -i:$port > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠ Puerto $port todavía ocupado${NC}"
        all_stopped=false
    fi
done

if [ "$all_stopped" = true ]; then
    echo ""
    echo -e "${GREEN}✅ Todos los servidores detenidos${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠ Algunos puertos siguen ocupados${NC}"
    echo "Ejecuta: lsof -i:8000 && lsof -i:8001"
fi