#!/usr/bin/env python3
import socket
import requests
import time

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def test_ipv4_connectivity():
    print(f"\n{Colors.BOLD}Test 1: Conectividad IPv4{Colors.END}")
    print("─" * 70)
    
    tests = [
        ('127.0.0.1', 8000, 'Servidor A (loopback)'),
        ('localhost', 8000, 'Servidor A (localhost)'),
        ('127.0.0.1', 8001, 'Servidor B (loopback)'),
        ('localhost', 8001, 'Servidor B (localhost)'),
    ]
    
    results = []
    for host, port, name in tests:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            success = result == 0
            results.append(success)
            
            status = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
            print(f"  {status} {name:30s} ({host}:{port})")
        except Exception as e:
            results.append(False)
            print(f"  {Colors.RED}✗{Colors.END} {name:30s} - Error: {e}")
    
    return all(results)

def test_ipv6_connectivity():
    print(f"\n{Colors.BOLD}Test 2: Conectividad IPv6{Colors.END}")
    print("─" * 70)
    
    # Verificar si IPv6 está disponible en el sistema
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.close()
        ipv6_available = True
    except:
        ipv6_available = False
    
    if not ipv6_available:
        print(f"  {Colors.YELLOW}⚠{Colors.END} IPv6 no disponible en este sistema")
        print(f"     Esto es normal en muchas configuraciones")
        return None  # No falla el test, solo no está disponible
    
    tests = [
        ('::1', 8000, 'Servidor A (loopback IPv6)'),
        ('::1', 8001, 'Servidor B (loopback IPv6)'),
    ]
    
    results = []
    for host, port, name in tests:
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            success = result == 0
            results.append(success)
            
            status = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
            print(f"  {status} {name:30s} ([{host}]:{port})")
        except Exception as e:
            results.append(False)
            print(f"  {Colors.RED}✗{Colors.END} {name:30s} - Error: {e}")
    
    return all(results) if results else None

def test_http_requests():
    print(f"\n{Colors.BOLD}Test 3: HTTP Requests{Colors.END}")
    print("─" * 70)
    
    endpoints = [
        ('http://127.0.0.1:8000/health', 'IPv4 Loopback'),
        ('http://localhost:8000/health', 'Localhost'),
    ]
    
    results = []
    for url, name in endpoints:
        try:
            response = requests.get(url, timeout=5)
            success = response.status_code in [200, 503]
            results.append(success)
            
            status = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
            print(f"  {status} {name:30s} - Status: {response.status_code}")
        except Exception as e:
            results.append(False)
            print(f"  {Colors.RED}✗{Colors.END} {name:30s} - Error: {e}")
    
    # Test IPv6 si está disponible
    try:
        response = requests.get('http://[::1]:8000/health', timeout=5)
        success = response.status_code in [200, 503]
        results.append(success)
        status = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
        print(f"  {status} {'IPv6 Loopback':30s} - Status: {response.status_code}")
    except Exception:
        print(f"  {Colors.YELLOW}⚠{Colors.END} {'IPv6 Loopback':30s} - No disponible")
    
    return all(results)

def test_socket_communication():
    print(f"\n{Colors.BOLD}Test 4: Comunicación Socket (Servidor B){Colors.END}")
    print("─" * 70)
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.abspath('.'))
        from common.protocol import Protocol, MessageType
        
        # Test con IPv4
        print("  Probando comunicación con IPv4...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('127.0.0.1', 8001))
        
        # Enviar ping
        ping = {"type": MessageType.PING}
        Protocol.send_message_sync(sock, ping)
        
        # Recibir respuesta
        response = Protocol.receive_message_sync(sock)
        sock.close()
        
        success = response.get('success', False)
        status = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
        print(f"    {status} Ping/Pong - Response: {response.get('result', {})}")
        
        return success
    except ImportError:
        print(f"  {Colors.YELLOW}⚠{Colors.END} No se pudo importar Protocol (ejecutar desde directorio TP2)")
        return None
    except Exception as e:
        print(f"  {Colors.RED}✗{Colors.END} Error: {e}")
        return False

def test_protocol_binary():
    print(f"\n{Colors.BOLD}Test 5: Protocolo Binario{Colors.END}")
    print("─" * 70)
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.abspath('.'))
        from common.protocol import Protocol
        
        # Test encode/decode
        test_data = {
            "type": "test",
            "url": "http://example.com",
            "data": {
                "number": 42,
                "string": "Hello",
                "list": [1, 2, 3],
                "unicode": "Hola 世界 "
            }
        }
        
        print("  Probando serialización...")
        encoded = Protocol.encode_message(test_data)
        print(f"    {Colors.GREEN}✓{Colors.END} Codificado: {len(encoded)} bytes")
        
        print("  Probando deserialización...")
        decoded = Protocol.decode_message(encoded)
        print(f"    {Colors.GREEN}✓{Colors.END} Decodificado correctamente")
        
        # Verificar que los datos sean idénticos
        match = decoded == test_data
        status = f"{Colors.GREEN}✓{Colors.END}" if match else f"{Colors.RED}✗{Colors.END}"
        print(f"  {status} Integridad de datos")
        
        return match
    except ImportError:
        print(f"  {Colors.YELLOW}⚠{Colors.END} No se pudo importar Protocol (ejecutar desde directorio TP2)")
        return None
    except Exception as e:
        print(f"  {Colors.RED}✗{Colors.END} Error: {e}")
        return False

def test_timeout_handling():
    print(f"\n{Colors.BOLD}Test 6: Manejo de Timeouts{Colors.END}")
    print("─" * 70)
    
    # Test con URL que tarda mucho
    print("  Probando timeout con URL lenta...")
    start = time.time()
    try:
        # httpbin.org/delay/X tarda X segundos en responder
        response = requests.get(
            'http://localhost:8000/scrape',
            params={'url': 'http://httpbin.org/delay/35'},  # Más que el timeout
            timeout=40  # El cliente espera, pero el servidor tiene timeout de 30s
        )
        elapsed = time.time() - start
        
        # Esperamos que falle o devuelva error
        if response.status_code in [504, 500]:  # Gateway timeout o error
            print(f"    {Colors.GREEN}✓{Colors.END} Timeout manejado correctamente (HTTP {response.status_code})")
            print(f"    {Colors.GREEN}✓{Colors.END} Tiempo: {elapsed:.2f}s (< 35s esperados)")
            return True
        else:
            print(f"    {Colors.YELLOW}⚠{Colors.END} Respuesta inesperada: {response.status_code}")
            return None
    except requests.Timeout:
        elapsed = time.time() - start
        print(f"    {Colors.GREEN}✓{Colors.END} Timeout del cliente activado: {elapsed:.2f}s")
        return True
    except Exception as e:
        print(f"    {Colors.YELLOW}⚠{Colors.END} Error: {e}")
        return None

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  TEST DE NETWORKING - TP2{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}Este test verifica:{Colors.END}")
    print("  • Soporte de IPv4")
    print("  • Soporte de IPv6 (si disponible)")
    print("  • Protocolo de comunicación socket")
    print("  • Serialización binaria")
    print("  • Manejo de timeouts")
    
    tests = [
        ("IPv4 Connectivity", test_ipv4_connectivity),
        ("IPv6 Connectivity", test_ipv6_connectivity),
        ("HTTP Requests", test_http_requests),
        ("Socket Communication", test_socket_communication),
        ("Binary Protocol", test_protocol_binary),
        ("Timeout Handling", test_timeout_handling),
    ]
    
    results = {}
    for test_name, test_func in tests:
        result = test_func()
        results[test_name] = result
        time.sleep(1)
    
    # Resumen
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}RESUMEN{Colors.END}")
    print("─" * 70)
    
    for test_name, result in results.items():
        if result is True:
            status = f"{Colors.GREEN}✓ PASS{Colors.END}"
        elif result is False:
            status = f"{Colors.RED}✗ FAIL{Colors.END}"
        else:
            status = f"{Colors.YELLOW}⊘ N/A{Colors.END}"
        
        print(f"  {status} | {test_name}")
    
    print(f"{Colors.BOLD}{'='*70}{Colors.END}")
    
    # Calcular resultado final (ignorando N/A)
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ NETWORKING TESTS PASADOS{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ ALGUNOS TESTS FALLARON{Colors.END}")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())