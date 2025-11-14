#!/bin/bash
cd ~/Escritorio/mi_repositorio/TP2
source venv/bin/activate

echo "🔄 Reiniciando sistema completo..."
echo ""

# Matar procesos anteriores
echo "1️⃣ Limpiando procesos anteriores..."
pkill -f "server_processing.py" 2>/dev/null
pkill -f "server_scraping.py" 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:8001 | xargs kill -9 2>/dev/null
sleep 2

# Verificar puertos libres
echo "2️⃣ Verificando puertos..."
if lsof -i:8000 > /dev/null 2>&1; then
    echo "❌ Puerto 8000 aún ocupado"
    exit 1
fi
if lsof -i:8001 > /dev/null 2>&1; then
    echo "❌ Puerto 8001 aún ocupado"
    exit 1
fi
echo "✅ Puertos libres"
echo ""

echo "3️⃣ Instrucciones:"
echo ""
echo "TERMINAL 1:"
echo "  cd ~/Escritorio/mi_repositorio/TP2"
echo "  source venv/bin/activate"
echo "  python server_processing.py -i localhost -p 8001 -n 4"
echo ""
echo "TERMINAL 2:"
echo "  cd ~/Escritorio/mi_repositorio/TP2"
echo "  source venv/bin/activate"
echo "  python server_scraping.py -i localhost -p 8000 --processing-host localhost --processing-port 8001"
echo ""
echo "Presiona ENTER cuando ambos servidores estén corriendo..."
read

echo ""
echo "4️⃣ Verificando servidores..."
sleep 2

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Servidor A corriendo"
else
    echo "❌ Servidor A no responde"
    exit 1
fi

if nc -z localhost 8001 2>/dev/null; then
    echo "✅ Servidor B corriendo"
else
    echo "❌ Servidor B no responde"
    exit 1
fi

echo ""
echo "5️⃣ Verificando multiprocessing..."
python verify_multiprocessing.py

if [ $? -eq 0 ]; then
    echo ""
    echo "6️⃣ Ejecutando tests completos..."
    echo "Presiona ENTER para continuar..."
    read
    ./run_all_tests.sh
else
    echo "❌ Verificación de multiprocessing falló"
    exit 1
fi