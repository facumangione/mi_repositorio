#!/usr/bin/env python3
import sys
import os
import socket
import argparse

# Agregar el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.protocol import Protocol, MessageType, create_request


def test_ping(host, port):
    print("\n" + "=" * 60)
    print("TEST 1: PING/PONG")
    print("=" * 60)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    
    # Enviar ping
    ping = {"type": MessageType.PING}
    print(f"Enviando: {ping}")
    Protocol.send_message_sync(sock, ping)
    
    # Recibir respuesta
    response = Protocol.receive_message_sync(sock)
    print(f" Respuesta: {response}")
    
    sock.close()
    
    if response.get('success'):
        print(" Test PING/PONG: OK")
    else:
        print(" Test PING/PONG: FAILED")
    
    return response.get('success', False)


def test_performance(host, port, url='http://example.com'):
    print("\n" + "=" * 60)
    print(f"⚡ TEST 2: ANÁLISIS DE RENDIMIENTO")
    print("=" * 60)
    print(f"URL: {url}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect((host, port))
    
    # Enviar request
    request = create_request('performance_request', url)
    print(f"Enviando request de performance...")
    Protocol.send_message_sync(sock, request)
    
    # Recibir respuesta
    print(" Esperando respuesta...")
    response = Protocol.receive_message_sync(sock)
    
    sock.close()
    
    if response.get('success'):
        result = response.get('result', {})
        print(f"\n Análisis completado:")
        print(f"     Tiempo de carga: {result.get('load_time_ms', 0):.2f} ms")
        print(f"    Tamaño total: {result.get('total_size_kb', 0):.2f} KB")
        print(f"    Número de requests: {result.get('num_requests', 0)}")
        print(f"   Status code: {result.get('status_code', 0)}")
        
        resources = result.get('resources', {})
        print(f"\n   Recursos:")
        print(f"      Scripts: {resources.get('scripts', 0)}")
        print(f"      tylesheets: {resources.get('stylesheets', 0)}")
        print(f"      Imágenes: {resources.get('images', 0)}")
        
        return True
    else:
        print(f"Error: {response.get('error', 'Unknown error')}")
        return False


def test_images(host, port):
    print("\n" + "=" * 60)
    print(" TEST 3: PROCESAMIENTO DE IMÁGENES")
    print("=" * 60)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect((host, port))
    
    # URLs de imágenes de prueba
    image_urls = [
        'https://via.placeholder.com/300',
        'https://via.placeholder.com/400',
    ]
    
    request = {
        'type': 'images_request',
        'url': 'https://example.com',
        'data': {
            'image_urls': image_urls,
            'max_images': 2
        }
    }
    
    print(f" Enviando request para procesar {len(image_urls)} imágenes...")
    Protocol.send_message_sync(sock, request)
    
    print(" Procesando imágenes...")
    response = Protocol.receive_message_sync(sock)
    
    sock.close()
    
    if response.get('success'):
        results = response.get('result', [])
        print(f"\nProcesadas {len(results)} imágenes:")
        
        for i, img in enumerate(results, 1):
            print(f"\n   Imagen {i}:")
            print(f"      URL: {img.get('url', 'N/A')}")
            size = img.get('original_size', {})
            print(f"      Tamaño original: {size.get('width')}x{size.get('height')}")
            print(f"      Formato: {img.get('format', 'N/A')}")
            print(f"      Tamaño: {img.get('size_bytes', 0)} bytes")
            thumb_size = len(img.get('thumbnail', ''))
            print(f"      Thumbnail: {thumb_size} chars (base64)")
        
        return True
    else:
        print(f"Error: {response.get('error', 'Unknown error')}")
        return False


def test_screenshot(host, port, url='http://example.com'):
    print("\n" + "=" * 60)
    print(" TEST 4: CAPTURA DE SCREENSHOT")
    print("=" * 60)
    print(f"URL: {url}")
    print("  Nota: Requiere Selenium + ChromeDriver instalado")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(60)  # Screenshots pueden tardar más
    sock.connect((host, port))
    
    request = create_request('screenshot_request', url, timeout=15)
    print(f" Enviando request de screenshot...")
    Protocol.send_message_sync(sock, request)
    
    print("Capturando screenshot (puede tardar)...")
    response = Protocol.receive_message_sync(sock)
    
    sock.close()
    
    if response.get('success'):
        screenshot_b64 = response.get('result', '')
        print(f"\n Screenshot capturado:")
        print(f"   Tamaño: {len(screenshot_b64)} chars (base64)")
        print(f"   ~{len(screenshot_b64) * 3 // 4 // 1024} KB")
        return True
    else:
        error = response.get('error', 'Unknown error')
        print(f"Error: {error}")
        
        if 'Selenium' in error or 'WebDriver' in error:
            print("\n Para habilitar screenshots:")
            print("   pip install selenium")
            print("   # Instalar ChromeDriver o usar screenshot fallback")
        
        return False


def run_all_tests(host, port, url='http://example.com'):
    """Ejecuta todos los tests."""
    print("\n" + "=" * 60)
    print("SUITE DE TESTS - SERVIDOR DE PROCESAMIENTO")
    print("=" * 60)
    print(f"Servidor: {host}:{port}")
    print(f"URL de prueba: {url}")
    
    results = {
        'ping': False,
        'performance': False,
        'images': False,
        'screenshot': False
    }
    
    try:
        # Test 1: Ping
        results['ping'] = test_ping(host, port)
        
        # Test 2: Performance
        results['performance'] = test_performance(host, port, url)
        
        # Test 3: Images
        results['images'] = test_images(host, port)
        
        # Test 4: Screenshot
        results['screenshot'] = test_screenshot(host, port, url)
        
    except ConnectionRefusedError:
        print("\n ERROR: No se pudo conectar al servidor")
        print(f"   Asegúrate de que el servidor esté corriendo en {host}:{port}")
        return False
    
    except Exception as e:
        print(f"\n ERROR INESPERADO: {e}")
        return False
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE TESTS")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "PASS" if passed else "❌ FAIL"
        print(f"{test_name.upper():.<20} {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests pasados")
    
    return total_passed == total_tests


def main():
    parser = argparse.ArgumentParser(description='Cliente de prueba del servidor de procesamiento')
    parser.add_argument('--host', default='localhost', help='Host del servidor')
    parser.add_argument('--port', type=int, default=8001, help='Puerto del servidor')
    parser.add_argument('--url', default='http://example.com', help='URL de prueba')
    parser.add_argument('--test', choices=['ping', 'performance', 'images', 'screenshot', 'all'],
                       default='all', help='Test específico a ejecutar')
    
    args = parser.parse_args()
    
    if args.test == 'all':
        success = run_all_tests(args.host, args.port, args.url)
    elif args.test == 'ping':
        success = test_ping(args.host, args.port)
    elif args.test == 'performance':
        success = test_performance(args.host, args.port, args.url)
    elif args.test == 'images':
        success = test_images(args.host, args.port)
    elif args.test == 'screenshot':
        success = test_screenshot(args.host, args.port, args.url)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())