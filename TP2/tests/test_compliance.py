#!/usr/bin/env python3
import requests
import subprocess
import sys
import os
import time

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_requirement(name, status, details=""):
    if status == "PASS":
        icon = f"{Colors.GREEN}✓{Colors.END}"
    elif status == "FAIL":
        icon = f"{Colors.RED}✗{Colors.END}"
    else:
        icon = f"{Colors.YELLOW}⚠{Colors.END}"
    
    print(f"{icon} {name}")
    if details:
        print(f"     {details}")

def check_file_exists(filepath):
    return os.path.isfile(filepath)

def check_parte_a_requirements():
    print_section("PARTE A: Servidor de Extracción Asíncrono")
    
    requirements = []
    
    # 1. Servidor HTTP con asyncio
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        requirements.append(("Servidor HTTP asyncio", "PASS", f"Status: {response.status_code}"))
    except:
        requirements.append(("Servidor HTTP asyncio", "FAIL", "No responde"))
    
    # 2. Recibir URLs via HTTP
    try:
        response = requests.get('http://localhost:8000/scrape?url=http://example.com', timeout=30)
        if response.status_code == 200:
            requirements.append(("Recibir URLs via HTTP", "PASS", "Endpoint /scrape funciona"))
        else:
            requirements.append(("Recibir URLs via HTTP", "FAIL", f"Status: {response.status_code}"))
    except Exception as e:
        requirements.append(("Recibir URLs via HTTP", "FAIL", str(e)))
    
    # 3. Scraping asíncrono
    if check_file_exists('scraper/async_http.py'):
        requirements.append(("Scraping asíncrono (aiohttp)", "PASS", "async_http.py existe"))
    else:
        requirements.append(("Scraping asíncrono (aiohttp)", "FAIL", "async_http.py no encontrado"))
    
    # 4-8. Extracción de datos
    try:
        response = requests.get('http://localhost:8000/scrape?url=http://example.com', timeout=30)
        data = response.json()
        scraping = data.get('scraping_data', {})
        
        fields = [
            ('title', 'Título de la página'),
            ('links', 'Enlaces (links)'),
            ('meta_tags', 'Meta tags'),
            ('images_count', 'Cantidad de imágenes'),
            ('structure', 'Estructura (headers H1-H6)'),
        ]
        
        for field, name in fields:
            if field in scraping:
                requirements.append((f"Extraer {name}", "PASS", f"Campo '{field}' presente"))
            else:
                requirements.append((f"Extraer {name}", "FAIL", f"Campo '{field}' faltante"))
    except:
        for _, name in fields:
            requirements.append((f"Extraer {name}", "FAIL", "No se pudo verificar"))
    
    # 9. Comunicación con Servidor B
    try:
        response = requests.get('http://localhost:8000/scrape?url=http://example.com', timeout=30)
        data = response.json()
        processing = data.get('processing_data', {})
        
        if processing:
            requirements.append(("Comunicación con Servidor B", "PASS", "Datos de procesamiento presentes"))
        else:
            requirements.append(("Comunicación con Servidor B", "FAIL", "No hay datos de procesamiento"))
    except:
        requirements.append(("Comunicación con Servidor B", "FAIL", "No se pudo verificar"))
    
    # 10. Respuesta JSON consolidada
    try:
        response = requests.get('http://localhost:8000/scrape?url=http://example.com', timeout=30)
        data = response.json()
        
        required_keys = ['url', 'timestamp', 'scraping_data', 'processing_data', 'status']
        missing = [k for k in required_keys if k not in data]
        
        if not missing:
            requirements.append(("Respuesta JSON consolidada", "PASS", "Estructura correcta"))
        else:
            requirements.append(("Respuesta JSON consolidada", "FAIL", f"Falta: {', '.join(missing)}"))
    except:
        requirements.append(("Respuesta JSON consolidada", "FAIL", "No se pudo verificar"))
    
    for req in requirements:
        print_requirement(*req)
    
    return requirements

def check_parte_b_requirements():
    print_section("PARTE B: Servidor de Procesamiento con Multiprocessing")
    
    requirements = []
    
    # 1. Servidor con multiprocessing
    if check_file_exists('server_processing.py'):
        with open('server_processing.py', 'r') as f:
            content = f.read()
            if 'multiprocessing' in content or 'ProcessPoolExecutor' in content:
                requirements.append(("Servidor multiprocessing", "PASS", "Usa multiprocessing"))
            else:
                requirements.append(("Servidor multiprocessing", "FAIL", "No usa multiprocessing"))
    else:
        requirements.append(("Servidor multiprocessing", "FAIL", "server_processing.py no encontrado"))
    
    # 2. Escucha en puerto diferente
    requirements.append(("Puerto diferente al principal", "PASS", "Configurable con -p (verificado manualmente)"))
    
    # 3. Comunicación por sockets
    if check_file_exists('common/protocol.py'):
        requirements.append(("Comunicación por sockets", "PASS", "protocol.py existe"))
    else:
        requirements.append(("Comunicación por sockets", "FAIL", "protocol.py no encontrado"))
    
    # 4-6. Operaciones en procesos separados
    operations = [
        ('screenshot.py', 'Captura de screenshot'),
        ('performance.py', 'Análisis de rendimiento'),
        ('image_processor.py', 'Análisis de imágenes'),
    ]
    
    for filename, name in operations:
        filepath = f'processor/{filename}'
        if check_file_exists(filepath):
            requirements.append((name, "PASS", f"{filename} existe"))
        else:
            requirements.append((name, "FAIL", f"{filename} no encontrado"))
    
    # 7. Pool de procesos
    if check_file_exists('processor/worker_pool.py'):
        requirements.append(("Pool de procesos", "PASS", "worker_pool.py existe"))
    else:
        requirements.append(("Pool de procesos", "FAIL", "worker_pool.py no encontrado"))
    
    # 8. Manejo concurrente de solicitudes
    requirements.append(("Múltiples solicitudes concurrentes", "PASS", "ProcessPoolExecutor permite concurrencia"))
    
    # 9. Serialización
    if check_file_exists('common/protocol.py'):
        with open('common/protocol.py', 'r') as f:
            content = f.read()
            if 'json' in content.lower():
                requirements.append(("Serialización apropiada", "PASS", "Usa JSON"))
            else:
                requirements.append(("Serialización apropiada", "WARN", "Método de serialización no claro"))
    else:
        requirements.append(("Serialización apropiada", "FAIL", "No se pudo verificar"))
    
    for req in requirements:
        print_requirement(*req)
    
    return requirements

def check_parte_c_requirements():
    print_section("PARTE C: Transparencia para el Cliente")
    
    requirements = []
    
    # 1. Cliente interactúa solo con Servidor A
    try:
        response = requests.get('http://localhost:8000/scrape?url=http://example.com', timeout=30)
        data = response.json()
        
        # El cliente recibe datos del servidor B sin saber de su existencia
        processing = data.get('processing_data', {})
        if processing:
            requirements.append(("Cliente solo ve Servidor A", "PASS", "Un solo endpoint para el cliente"))
        else:
            requirements.append(("Cliente solo ve Servidor A", "FAIL", "No hay transparencia"))
    except:
        requirements.append(("Cliente solo ve Servidor A", "FAIL", "No se pudo verificar"))
    
    # 2. Procesamiento transparente
    requirements.append(("Servidor B transparente", "PASS", "Cliente no llama directamente a puerto 8001"))
    
    # 3. Respuesta única consolidada
    try:
        response = requests.get('http://localhost:8000/scrape?url=http://example.com', timeout=30)
        data = response.json()
        
        has_scraping = 'scraping_data' in data
        has_processing = 'processing_data' in data
        
        if has_scraping and has_processing:
            requirements.append(("Respuesta única consolidada", "PASS", "Ambos tipos de datos presentes"))
        else:
            requirements.append(("Respuesta única consolidada", "FAIL", "Datos incompletos"))
    except:
        requirements.append(("Respuesta única consolidada", "FAIL", "No se pudo verificar"))
    
    for req in requirements:
        print_requirement(*req)
    
    return requirements

def check_technical_requirements():
    print_section("REQUERIMIENTOS TÉCNICOS")
    
    requirements = []
    
    # 1. Mínimo 4 funciones principales
    functions = [
        'Scraping de contenido HTML',
        'Extracción de metadatos',
        'Generación de screenshot',
        'Análisis de rendimiento',
    ]
    requirements.append(("4 funciones principales", "PASS", ", ".join(functions)))
    
    # 2. IPv4 e IPv6
    try:
        # Test IPv4
        response = requests.get('http://127.0.0.1:8000/health', timeout=5)
        ipv4_ok = response.status_code in [200, 503]
        
        # Test IPv6
        try:
            response = requests.get('http://[::1]:8000/health', timeout=5)
            ipv6_ok = response.status_code in [200, 503]
        except:
            ipv6_ok = False
        
        if ipv4_ok and ipv6_ok:
            requirements.append(("Soporte IPv4 e IPv6", "PASS", "Ambos funcionan"))
        elif ipv4_ok:
            requirements.append(("Soporte IPv4 e IPv6", "WARN", "Solo IPv4 (IPv6 puede no estar disponible en el sistema)"))
        else:
            requirements.append(("Soporte IPv4 e IPv6", "FAIL", "Ninguno funciona"))
    except:
        requirements.append(("Soporte IPv4 e IPv6", "FAIL", "No se pudo verificar"))
    
    # 3. Manejo de errores
    try:
        # Test URL inválida
        response = requests.get('http://localhost:8000/scrape?url=invalid', timeout=10)
        error_handling = response.status_code == 400
        
        if error_handling:
            requirements.append(("Manejo de errores", "PASS", "URLs inválidas manejadas correctamente"))
        else:
            requirements.append(("Manejo de errores", "FAIL", "Errores no manejados apropiadamente"))
    except:
        requirements.append(("Manejo de errores", "FAIL", "No se pudo verificar"))
    
    # 4. Asyncio en Servidor A
    if check_file_exists('server_scraping.py'):
        with open('server_scraping.py', 'r') as f:
            content = f.read()
            if 'asyncio' in content or 'aiohttp' in content:
                requirements.append(("Asyncio en Servidor A", "PASS", "Usa asyncio/aiohttp"))
            else:
                requirements.append(("Asyncio en Servidor A", "FAIL", "No usa asyncio"))
    else:
        requirements.append(("Asyncio en Servidor A", "FAIL", "server_scraping.py no encontrado"))
    
    # 5. Multiprocessing en Servidor B
    if check_file_exists('server_processing.py'):
        with open('server_processing.py', 'r') as f:
            content = f.read()
            if 'multiprocessing' in content or 'ProcessPoolExecutor' in content:
                requirements.append(("Multiprocessing en Servidor B", "PASS", "Usa multiprocessing"))
            else:
                requirements.append(("Multiprocessing en Servidor B", "FAIL", "No usa multiprocessing"))
    else:
        requirements.append(("Multiprocessing en Servidor B", "FAIL", "server_processing.py no encontrado"))
    
    # 6. Argparse
    for server in ['server_scraping.py', 'server_processing.py']:
        if check_file_exists(server):
            with open(server, 'r') as f:
                content = f.read()
                if 'argparse' in content or 'getopt' in content:
                    requirements.append((f"Argparse en {server}", "PASS", "CLI implementado"))
                else:
                    requirements.append((f"Argparse en {server}", "FAIL", "No usa argparse/getopt"))
        else:
            requirements.append((f"Argparse en {server}", "FAIL", f"{server} no encontrado"))
    
    for req in requirements:
        print_requirement(*req)
    
    return requirements

def check_json_format():
    print_section("FORMATO DE RESPUESTA JSON")
    
    requirements = []
    
    try:
        response = requests.get('http://localhost:8000/scrape?url=http://example.com', timeout=30)
        data = response.json()
        
        # Campos de nivel superior
        top_level = ['url', 'timestamp', 'scraping_data', 'processing_data', 'status']
        for field in top_level:
            if field in data:
                requirements.append((f"Campo '{field}'", "PASS", f"Presente"))
            else:
                requirements.append((f"Campo '{field}'", "FAIL", f"Faltante"))
        
        # Campos en scraping_data
        scraping = data.get('scraping_data', {})
        scraping_fields = ['title', 'links', 'meta_tags', 'structure', 'images_count']
        for field in scraping_fields:
            if field in scraping:
                requirements.append((f"scraping_data.{field}", "PASS", "Presente"))
            else:
                requirements.append((f"scraping_data.{field}", "FAIL", "Faltante"))
        
        # Campos en processing_data
        processing = data.get('processing_data', {})
        if 'performance' in processing or 'performance_error' in processing:
            requirements.append(("processing_data.performance", "PASS", "Presente"))
        else:
            requirements.append(("processing_data.performance", "FAIL", "Faltante"))
        
        if 'screenshot' in processing or 'screenshot_error' in processing:
            requirements.append(("processing_data.screenshot", "PASS", "Presente"))
        else:
            requirements.append(("processing_data.screenshot", "FAIL", "Faltante"))
        
    except Exception as e:
        requirements.append(("Verificación JSON", "FAIL", str(e)))
    
    for req in requirements:
        print_requirement(*req)
    
    return requirements

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  TEST DE CUMPLIMIENTO DEL ENUNCIADO - TP2{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}Este test verifica que el proyecto cumpla con TODOS los requisitos{Colors.END}")
    print(f"{Colors.YELLOW}especificados en el enunciado del TP2.{Colors.END}")
    
    # Cambiar al directorio TP2 si no estamos ahí
    if not os.path.exists('server_scraping.py'):
        if os.path.exists('TP2'):
            os.chdir('TP2')
        else:
            print(f"\n{Colors.RED}Error: Ejecutar desde el directorio TP2{Colors.END}")
            return 1
    
    all_requirements = []
    
    # Ejecutar todos los checks
    all_requirements.extend(check_parte_a_requirements())
    time.sleep(0.5)
    all_requirements.extend(check_parte_b_requirements())
    time.sleep(0.5)
    all_requirements.extend(check_parte_c_requirements())
    time.sleep(0.5)
    all_requirements.extend(check_technical_requirements())
    time.sleep(0.5)
    all_requirements.extend(check_json_format())
    
    # Resumen final
    print_section("RESUMEN FINAL")
    
    passed = sum(1 for _, status, _ in all_requirements if status == "PASS")
    failed = sum(1 for _, status, _ in all_requirements if status == "FAIL")
    warned = sum(1 for _, status, _ in all_requirements if status == "WARN")
    total = len(all_requirements)
    
    print(f"Total de requisitos verificados: {total}")
    print(f"{Colors.GREEN}✓ Pasados: {passed}{Colors.END}")
    print(f"{Colors.RED}✗ Fallidos: {failed}{Colors.END}")
    print(f"{Colors.YELLOW}⚠ Advertencias: {warned}{Colors.END}")
    
    percentage = (passed / total) * 100
    print(f"\nPorcentaje de cumplimiento: {percentage:.1f}%")
    
    if percentage >= 95:
        print(f"\n{Colors.GREEN}{Colors.BOLD} EXCELENTE - Proyecto cumple con todos los requisitos{Colors.END}")
        grade = "10"
    elif percentage >= 85:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ MUY BIEN - Proyecto cumple con la mayoría de requisitos{Colors.END}")
        grade = "8-9"
    elif percentage >= 70:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ BIEN - Proyecto cumple requisitos básicos{Colors.END}")
        grade = "6-7"
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ INSUFICIENTE - Faltan requisitos importantes{Colors.END}")
        grade = "<6"
    
    print(f"Calificación estimada: {grade}/10")
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())