#!/usr/bin/env python3
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def scrape_url(url, client_id):
    start = time.time()
    try:
        response = requests.get(
            'http://localhost:8000/scrape',
            params={'url': url},
            timeout=60
        )
        elapsed = time.time() - start
        
        success = response.status_code == 200
        data = response.json() if success else {}
        
        return {
            'client_id': client_id,
            'url': url,
            'success': success,
            'elapsed': elapsed,
            'status_code': response.status_code,
            'title': data.get('scraping_data', {}).get('title', 'N/A') if success else 'N/A'
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            'client_id': client_id,
            'url': url,
            'success': False,
            'elapsed': elapsed,
            'status_code': 0,
            'error': str(e)
        }

def test_sequential_requests():
    print(f"\n{Colors.BOLD}Test 1: Requests Secuenciales{Colors.END}")
    print("─" * 70)
    
    urls = [
        'http://example.com',
        'http://example.org',
        'http://example.net',
    ]
    
    results = []
    total_start = time.time()
    
    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] Scraping {url}...", end=' ', flush=True)
        result = scrape_url(url, i)
        results.append(result)
        
        if result['success']:
            print(f"{Colors.GREEN}✓{Colors.END} {result['elapsed']:.2f}s")
        else:
            print(f"{Colors.RED}✗{Colors.END} {result.get('error', 'Failed')}")
    
    total_time = time.time() - total_start
    successful = sum(1 for r in results if r['success'])
    
    print(f"\n  Resultados:")
    print(f"    Exitosos: {successful}/{len(urls)}")
    print(f"    Tiempo total: {total_time:.2f}s")
    print(f"    Promedio: {total_time/len(urls):.2f}s por request")
    
    return results, total_time

def test_concurrent_requests(num_clients=5):
    print(f"\n{Colors.BOLD}Test 2: Requests Concurrentes ({num_clients} clientes){Colors.END}")
    print("─" * 70)
    
    urls = [
        'http://example.com',
        'http://example.org',
        'http://example.net',
    ]
    
    # Repetir URLs para tener suficientes requests
    all_urls = (urls * ((num_clients // len(urls)) + 1))[:num_clients]
    
    results = []
    total_start = time.time()
    
    print(f"  Lanzando {num_clients} requests simultáneos...")
    
    with ThreadPoolExecutor(max_workers=num_clients) as executor:
        futures = {
            executor.submit(scrape_url, url, i): (url, i) 
            for i, url in enumerate(all_urls, 1)
        }
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            result = future.result()
            results.append(result)
            
            status = f"{Colors.GREEN}✓{Colors.END}" if result['success'] else f"{Colors.RED}✗{Colors.END}"
            print(f"    [{completed}/{num_clients}] Client {result['client_id']}: {status} {result['elapsed']:.2f}s")
    
    total_time = time.time() - total_start
    successful = sum(1 for r in results if r['success'])
    times = [r['elapsed'] for r in results if r['success']]
    
    print(f"\n  Resultados:")
    print(f"    Exitosos: {successful}/{num_clients}")
    print(f"    Tiempo total (wall-clock): {total_time:.2f}s")
    print(f"    Tiempo promedio por request: {statistics.mean(times):.2f}s")
    print(f"    Tiempo mínimo: {min(times):.2f}s")
    print(f"    Tiempo máximo: {max(times):.2f}s")
    print(f"    Desviación estándar: {statistics.stdev(times) if len(times) > 1 else 0:.2f}s")
    
    # Calcular throughput
    throughput = num_clients / total_time
    print(f"    Throughput: {throughput:.2f} requests/segundo")
    
    return results, total_time

def test_stress_many_clients(num_clients=10):
    print(f"\n{Colors.BOLD}Test 3: Stress Test ({num_clients} clientes){Colors.END}")
    print("─" * 70)
    
    url = 'http://example.com'
    
    results = []
    total_start = time.time()
    
    print(f"  Lanzando {num_clients} requests al mismo tiempo...")
    
    with ThreadPoolExecutor(max_workers=num_clients) as executor:
        futures = [
            executor.submit(scrape_url, url, i) 
            for i in range(1, num_clients + 1)
        ]
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
    
    total_time = time.time() - total_start
    successful = sum(1 for r in results if r['success'])
    failed = num_clients - successful
    
    if successful > 0:
        times = [r['elapsed'] for r in results if r['success']]
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
    else:
        avg_time = max_time = min_time = 0
    
    print(f"\n  Resultados:")
    print(f"    Exitosos: {Colors.GREEN}{successful}{Colors.END}")
    print(f"    Fallidos: {Colors.RED}{failed}{Colors.END}")
    print(f"    Tiempo total: {total_time:.2f}s")
    print(f"    Tiempo promedio: {avg_time:.2f}s")
    print(f"    Rango: {min_time:.2f}s - {max_time:.2f}s")
    
    # Evaluar resultado
    if successful == num_clients:
        print(f"\n  {Colors.GREEN}{Colors.BOLD}✓ Sistema maneja {num_clients} clientes sin problemas{Colors.END}")
    elif successful >= num_clients * 0.8:
        print(f"\n  {Colors.YELLOW}{Colors.BOLD}⚠ Sistema maneja mayoría de clientes pero hay algunas fallas{Colors.END}")
    else:
        print(f"\n  {Colors.RED}{Colors.BOLD}✗ Sistema tiene problemas bajo carga{Colors.END}")
    
    return results, total_time

def test_different_urls_concurrent():
    print(f"\n{Colors.BOLD}Test 4: URLs Diferentes en Paralelo{Colors.END}")
    print("─" * 70)
    
    urls = [
        ('http://example.com', 'Example.com'),
        ('http://example.org', 'Example.org'),
        ('http://example.net', 'Example.net'),
        ('https://www.ietf.org/', 'IETF'),
        ('https://httpbin.org/html', 'HTTPBin'),
    ]
    
    total_start = time.time()
    
    print(f"  Scraping {len(urls)} sitios diferentes simultáneamente...")
    
    results = []
    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        futures = {
            executor.submit(scrape_url, url, i): (url, name) 
            for i, (url, name) in enumerate(urls, 1)
        }
        
        for future in as_completed(futures):
            result = future.result()
            url, name = futures[future]
            results.append(result)
            
            if result['success']:
                print(f"    {Colors.GREEN}✓{Colors.END} {name}: {result['elapsed']:.2f}s - {result['title']}")
            else:
                error = result.get('error', 'Failed')
                print(f"    {Colors.RED}✗{Colors.END} {name}: {error}")
    
    total_time = time.time() - total_start
    successful = sum(1 for r in results if r['success'])
    
    print(f"\n  Resultados:")
    print(f"    Exitosos: {successful}/{len(urls)}")
    print(f"    Tiempo total: {total_time:.2f}s")
    
    if successful > 0:
        times = [r['elapsed'] for r in results if r['success']]
        print(f"    Tiempo promedio: {statistics.mean(times):.2f}s")
    
    return results, total_time

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  TEST DE CONCURRENCIA - TP2{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}Este test verifica:{Colors.END}")
    print("  • Asyncio maneja múltiples clientes correctamente")
    print("  • Multiprocessing procesa tasks en paralelo")
    print("  • El sistema escala bajo carga")
    print("  • No hay deadlocks o race conditions")
    
    input(f"\n{Colors.YELLOW}Presiona ENTER para comenzar...{Colors.END}")
    
    all_results = []
    
    # Test 1: Sequential
    seq_results, seq_time = test_sequential_requests()
    all_results.append(('Sequential', seq_results, seq_time))
    time.sleep(2)
    
    # Test 2: Concurrent (5 clients)
    conc_results, conc_time = test_concurrent_requests(5)
    all_results.append(('Concurrent (5)', conc_results, conc_time))
    time.sleep(2)
    
    # Test 3: Stress test (10 clients)
    stress_results, stress_time = test_stress_many_clients(10)
    all_results.append(('Stress (10)', stress_results, stress_time))
    time.sleep(2)
    
    # Test 4: Different URLs
    diff_results, diff_time = test_different_urls_concurrent()
    all_results.append(('Different URLs', diff_results, diff_time))
    
    # Resumen final
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}RESUMEN GENERAL{Colors.END}")
    print("─" * 70)
    
    for test_name, results, total_time in all_results:
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        percentage = (successful / total) * 100 if total > 0 else 0
        
        status = f"{Colors.GREEN}✓{Colors.END}" if percentage == 100 else f"{Colors.YELLOW}⚠{Colors.END}"
        print(f"  {status} {test_name:20s}: {successful}/{total} ({percentage:.0f}%) - {total_time:.2f}s")
    
    print(f"{Colors.BOLD}{'='*70}{Colors.END}")
    
    # Verificar si todos los tests pasaron
    all_passed = all(
        sum(1 for r in results if r['success']) == len(results)
        for _, results, _ in all_results
    )
    
    if all_passed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ SISTEMA APROBADO{Colors.END}")
        print(f"  El sistema maneja concurrencia correctamente")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ ALGUNOS TESTS FALLARON{Colors.END}")
        print(f"  Revisar logs de los servidores para más detalles")
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())