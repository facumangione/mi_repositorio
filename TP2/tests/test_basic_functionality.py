#!/usr/bin/env python3
import requests
import time
import json
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"{status} | {name}")
    if details:
        print(f"     {details}")

def test_server_a_health():
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        passed = response.status_code in [200, 503]
        data = response.json() if passed else {}
        details = f"Status: {response.status_code}, Server: {data.get('server', 'N/A')}"
        print_test("Servidor A - Health Check", passed, details)
        return passed
    except Exception as e:
        print_test("Servidor A - Health Check", False, str(e))
        return False

def test_server_a_info():
    try:
        response = requests.get('http://localhost:8000/info', timeout=5)
        passed = response.status_code == 200
        data = response.json() if passed else {}
        details = f"Server: {data.get('server', 'N/A')}, Version: {data.get('version', 'N/A')}"
        print_test("Servidor A - Info Endpoint", passed, details)
        return passed
    except Exception as e:
        print_test("Servidor A - Info Endpoint", False, str(e))
        return False

def test_scraping_basic():
    try:
        start = time.time()
        response = requests.get(
            'http://localhost:8000/scrape',
            params={'url': 'http://example.com'},
            timeout=30
        )
        elapsed = time.time() - start
        
        passed = response.status_code == 200
        data = response.json() if passed else {}
        
        details = f"Time: {elapsed:.2f}s, Status: {data.get('status', 'N/A')}"
        print_test("Scraping Básico", passed, details)
        
        if passed:
            print(f"     Title: {data.get('scraping_data', {}).get('title', 'N/A')}")
            print(f"     Links: {data.get('scraping_data', {}).get('links_count', 0)}")
        
        return passed
    except Exception as e:
        print_test("Scraping Básico", False, str(e))
        return False

def test_scraping_data_extraction():
    try:
        response = requests.get(
            'http://localhost:8000/scrape',
            params={'url': 'http://example.com'},
            timeout=30
        )
        
        if response.status_code != 200:
            print_test("Extracción de Datos", False, "Request failed")
            return False
        
        data = response.json()
        scraping = data.get('scraping_data', {})
        
        # Verificar campos requeridos
        required_fields = ['title', 'links', 'meta_tags', 'structure', 'images_count']
        missing = [f for f in required_fields if f not in scraping]
        
        passed = len(missing) == 0
        details = f"Campos presentes: {len(required_fields) - len(missing)}/{len(required_fields)}"
        if missing:
            details += f", Faltantes: {', '.join(missing)}"
        
        print_test("Extracción de Datos", passed, details)
        return passed
    except Exception as e:
        print_test("Extracción de Datos", False, str(e))
        return False

def test_processing_server_integration():
    try:
        response = requests.get(
            'http://localhost:8000/scrape',
            params={'url': 'http://example.com'},
            timeout=30
        )
        
        if response.status_code != 200:
            print_test("Integración Servidor B", False, "Request failed")
            return False
        
        data = response.json()
        processing = data.get('processing_data', {})
        
        # Verificar que hay datos de procesamiento
        has_performance = 'performance' in processing or 'performance_error' in processing
        has_screenshot = 'screenshot' in processing or 'screenshot_error' in processing
        
        passed = has_performance and has_screenshot
        details = f"Performance: {'✓' if has_performance else '✗'}, Screenshot: {'✓' if has_screenshot else '✗'}"
        
        print_test("Integración Servidor B", passed, details)
        return passed
    except Exception as e:
        print_test("Integración Servidor B", False, str(e))
        return False

def test_seo_analysis():
    try:
        response = requests.get(
            'http://localhost:8000/scrape',
            params={'url': 'http://example.com'},
            timeout=30
        )
        
        if response.status_code != 200:
            print_test("Análisis SEO", False, "Request failed")
            return False
        
        data = response.json()
        seo = data.get('seo_analysis', {})
        
        has_score = 'score' in seo
        has_grade = 'grade' in seo
        has_issues = 'issues' in seo
        
        passed = has_score and has_grade and has_issues
        details = f"Score: {seo.get('score', 'N/A')}/100, Grade: {seo.get('grade', 'N/A')}"
        
        print_test("Análisis SEO", passed, details)
        return passed
    except Exception as e:
        print_test("Análisis SEO", False, str(e))
        return False

def test_error_handling_invalid_url():
    try:
        response = requests.get(
            'http://localhost:8000/scrape',
            params={'url': 'not-a-valid-url'},
            timeout=10
        )
        
        passed = response.status_code == 400
        details = f"Status code: {response.status_code} (esperado 400)"
        
        print_test("Error Handling - URL Inválida", passed, details)
        return passed
    except Exception as e:
        print_test("Error Handling - URL Inválida", False, str(e))
        return False

def test_error_handling_missing_url():
    try:
        response = requests.get(
            'http://localhost:8000/scrape',
            timeout=10
        )
        
        passed = response.status_code == 400
        details = f"Status code: {response.status_code} (esperado 400)"
        
        print_test("Error Handling - URL Faltante", passed, details)
        return passed
    except Exception as e:
        print_test("Error Handling - URL Faltante", False, str(e))
        return False

def test_json_structure():
    try:
        response = requests.get(
            'http://localhost:8000/scrape',
            params={'url': 'http://example.com'},
            timeout=30
        )
        
        if response.status_code != 200:
            print_test("Estructura JSON", False, "Request failed")
            return False
        
        data = response.json()
        
        # Verificar estructura según enunciado
        required_top_level = ['url', 'timestamp', 'scraping_data', 'processing_data', 'status']
        missing = [f for f in required_top_level if f not in data]
        
        passed = len(missing) == 0
        details = f"Campos top-level: {len(required_top_level) - len(missing)}/{len(required_top_level)}"
        
        print_test("Estructura JSON", passed, details)
        return passed
    except Exception as e:
        print_test("Estructura JSON", False, str(e))
        return False

def test_performance_metrics():
    try:
        response = requests.get(
            'http://localhost:8000/scrape',
            params={'url': 'http://example.com'},
            timeout=30
        )
        
        if response.status_code != 200:
            print_test("Métricas de Performance", False, "Request failed")
            return False
        
        data = response.json()
        perf = data.get('processing_data', {}).get('performance', {})
        
        if not perf:
            print_test("Métricas de Performance", False, "No performance data")
            return False
        
        required_metrics = ['load_time_ms', 'total_size_kb', 'num_requests']
        present = [m for m in required_metrics if m in perf]
        
        passed = len(present) == len(required_metrics)
        details = f"Métricas: {', '.join([f'{m}={perf[m]}' for m in present])}"
        
        print_test("Métricas de Performance", passed, details)
        return passed
    except Exception as e:
        print_test("Métricas de Performance", False, str(e))
        return False

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}  TEST BÁSICO DE FUNCIONALIDAD - TP2{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    print(f"{Colors.YELLOW}Prerequisitos:{Colors.END}")
    print("  - Servidor A corriendo en localhost:8000")
    print("  - Servidor B corriendo en localhost:8001")
    print()
    
    tests = [
        test_server_a_health,
        test_server_a_info,
        test_scraping_basic,
        test_scraping_data_extraction,
        test_processing_server_integration,
        test_seo_analysis,
        test_error_handling_invalid_url,
        test_error_handling_missing_url,
        test_json_structure,
        test_performance_metrics,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        time.sleep(0.5)  # Pequeña pausa entre tests
    
    # Resumen
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}RESUMEN:{Colors.END}")
    print(f"  Tests pasados: {passed}/{total} ({percentage:.1f}%)")
    
    if percentage == 100:
        print(f"  {Colors.GREEN}{Colors.BOLD}¡TODOS LOS TESTS PASARON!{Colors.END}")
    elif percentage >= 80:
        print(f"  {Colors.YELLOW}{Colors.BOLD}Mayoría de tests pasados{Colors.END}")
    else:
        print(f"  {Colors.RED}{Colors.BOLD}Varios tests fallaron{Colors.END}")
    
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    
    return 0 if percentage == 100 else 1

if __name__ == '__main__':
    import sys
    sys.exit(main())