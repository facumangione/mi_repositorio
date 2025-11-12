#!/usr/bin/env python3
import sys
import argparse
import requests
import json
from datetime import datetime


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title: str):
    print(f"\n🔹 {title}")
    print("-" * 70)


def scrape_url(server_url: str, target_url: str):
    print_header(f"SCRAPING: {target_url}")
    
    # Hacer request
    print(f" Enviando request a: {server_url}/scrape")
    print(f" Target URL: {target_url}")
    
    start = datetime.now()
    
    try:
        response = requests.get(
            f"{server_url}/scrape",
            params={'url': target_url},
            timeout=60
        )
        
        elapsed = (datetime.now() - start).total_seconds()
        
        print(f" Response recibida en {elapsed:.2f}s")
        print(f" Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            display_results(data)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    except requests.Timeout:
        print("Timeout - La request tardó más de 60 segundos")
    
    except requests.ConnectionError:
        print(f" Error de conexión - ¿Está el servidor corriendo en {server_url}?")
    
    except Exception as e:
        print(f" Error: {e}")


def display_results(data: dict):
    
    # Información básica
    print_section("Información Básica")
    print(f"URL: {data.get('url')}")
    print(f"Timestamp: {data.get('timestamp')}")
    print(f"Tiempo de procesamiento: {data.get('processing_time_seconds')}s")
    print(f"Status: {data.get('status')}")
    
    # Datos de scraping
    scraping = data.get('scraping_data', {})
    print_section("Datos de Scraping")
    print(f"Título: {scraping.get('title', 'N/A')}")
    print(f"Links encontrados: {scraping.get('links_count', 0)}")
    print(f"Imágenes: {scraping.get('images_count', 0)}")
    
    # Estructura
    structure = scraping.get('structure', {})
    print(f"\nEstructura de Headers:")
    for header, count in structure.items():
        if count > 0:
            print(f"  {header.upper()}: {count}")
    
    # Stats de texto
    text_stats = scraping.get('text_stats', {})
    print(f"\nEstadísticas de Texto:")
    print(f"  Palabras: {text_stats.get('word_count', 0)}")
    print(f"  Párrafos: {text_stats.get('paragraph_count', 0)}")
    print(f"  Listas: {text_stats.get('list_count', 0)}")
    
    # Meta tags
    meta = scraping.get('meta_tags', {})
    if meta.get('description'):
        print(f"\nMeta Description:")
        print(f"  {meta['description'][:100]}...")
    
    # SEO Analysis
    seo = data.get('seo_analysis', {})
    if seo:
        print_section("Análisis SEO")
        print(f"Score: {seo.get('score', 0)}/100")
        print(f"Grade: {seo.get('grade', 'N/A')}")
        
        if seo.get('issues'):
            print(f"\n Issues encontrados:")
            for issue in seo['issues']:
                print(f"  - {issue}")
        
        if seo.get('recommendations'):
            print(f"\n Recomendaciones:")
            for rec in seo['recommendations'][:3]:  # Primeras 3
                print(f"  - {rec}")
    
    # Datos de procesamiento (Servidor B)
    processing = data.get('processing_data', {})
    if processing:
        print_section("Datos de Procesamiento (Servidor B)")
        
        # Performance
        perf = processing.get('performance')
        if perf:
            print(f"⚡ Performance:")
            print(f"  Tiempo de carga: {perf.get('load_time_ms', 0)}ms")
            print(f"  Tamaño total: {perf.get('total_size_kb', 0)} KB")
            print(f"  Requests: {perf.get('num_requests', 0)}")
        elif 'performance_error' in processing:
            print(f"⚡ Performance: Error - {processing['performance_error']}")
        
        # Screenshot
        if processing.get('screenshot'):
            screenshot_size = len(processing['screenshot'])
            print(f" Screenshot: {screenshot_size} chars (base64)")
            print(f"  ~{screenshot_size * 3 // 4 // 1024} KB")
        elif 'screenshot_error' in processing:
            print(f"Screenshot: Error - {processing['screenshot_error']}")
        
        # Thumbnails
        thumbnails = processing.get('thumbnails', [])
        if thumbnails:
            print(f"  Thumbnails: {len(thumbnails)} generados")
        elif 'images_error' in processing:
            print(f"  Thumbnails: Error - {processing['images_error']}")
    
    # Redes sociales
    social = scraping.get('social_links', {})
    if social:
        print_section("Enlaces Sociales")
        for platform, url in social.items():
            print(f"  {platform.title()}: {url}")
    
    # Metadata técnica
    metadata = data.get('metadata', {})
    if metadata.get('technical'):
        tech = metadata['technical']
        print_section("Información Técnica")
        print(f"HTML Size: {tech.get('html_size_kb', 0)} KB")
        print(f"HTTPS: {'' if tech.get('uses_https') else ''}")
        
        frameworks = tech.get('framework_hints', [])
        if frameworks:
            print(f"Frameworks detectados: {', '.join(frameworks)}")


def check_health(server_url: str):
    print_header("HEALTH CHECK")
    
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
        data = response.json()
        
        print(f"Status: {response.status_code}")
        print(f"Server: {data.get('server', 'unknown')}")
        print(f"Timestamp: {data.get('timestamp', 'N/A')}")
        
        proc_server = data.get('processing_server', {})
        print(f"\nProcessing Server:")
        print(f"  Host: {proc_server.get('host', 'N/A')}")
        print(f"  Port: {proc_server.get('port', 'N/A')}")
        print(f"  Available: {'' if proc_server.get('available') else ''}")
        
        return response.status_code == 200
    
    except Exception as e:
        print(f"Error: {e}")
        return False


def get_info(server_url: str):
    print_header("SERVER INFO")
    
    try:
        response = requests.get(f"{server_url}/info", timeout=5)
        data = response.json()
        
        print(f"Server: {data.get('server', 'N/A')}")
        print(f"Version: {data.get('version', 'N/A')}")
        
        print("\n🔹 Endpoints:")
        for endpoint, info in data.get('endpoints', {}).items():
            print(f"  {endpoint}")
            print(f"    Method: {info.get('method', 'N/A')}")
            print(f"    {info.get('description', 'N/A')}")
        
        print("\n🔹 Features:")
        for feature in data.get('features', []):
            print(f"  ✓ {feature}")
    
    except Exception as e:
        print(f" Error: {e}")


def save_results(data: dict, filename: str = 'scraping_results.json'):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n Resultados guardados en: {filename}")
    except Exception as e:
        print(f"\n Error guardando archivo: {e}")


def main():
    parser = argparse.ArgumentParser(description='Cliente del sistema de scraping')
    parser.add_argument(
        '--server',
        default='http://localhost:8000',
        help='URL del servidor (default: http://localhost:8000)'
    )
    parser.add_argument(
        '--url',
        help='URL a scrapear'
    )
    parser.add_argument(
        '--health',
        action='store_true',
        help='Solo verificar health del servidor'
    )
    parser.add_argument(
        '--info',
        action='store_true',
        help='Obtener información del servidor'
    )
    parser.add_argument(
        '--save',
        metavar='FILE',
        help='Guardar resultados en archivo JSON'
    )
    
    args = parser.parse_args()
    
    # Health check
    if args.health:
        check_health(args.server)
        return
    
    # Server info
    if args.info:
        get_info(args.server)
        return
    
    # Scraping
    if not args.url:
        print("Error: Se requiere --url para hacer scraping")
        print("Uso: python client.py --url https://example.com")
        print("     python client.py --health")
        print("     python client.py --info")
        return 1
    
    # Hacer scraping
    scrape_url(args.server, args.url)


if __name__ == '__main__':
    sys.exit(main() or 0)