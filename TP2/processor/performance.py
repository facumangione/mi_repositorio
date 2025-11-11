import time
import logging
from typing import Dict, Any
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


def analyze_performance(url: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    import requests
    from bs4 import BeautifulSoup
    
    options = options or {}
    timeout = options.get('timeout', 10)
    
    logger.info(f"Analizando rendimiento de {url}")
    
    try:
        # Medir tiempo de carga
        start_time = time.time()
        
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
        )
        
        load_time = (time.time() - start_time) * 1000  # Convertir a ms
        
        # Información básica
        status_code = response.status_code
        page_size = len(response.content)
        redirect_count = len(response.history)
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        scripts = soup.find_all('script', src=True)
        styles = soup.find_all('link', rel='stylesheet')
        images = soup.find_all('img', src=True)
        videos = soup.find_all('video')
        iframes = soup.find_all('iframe')
        
        num_requests = 1  # La página principal
        num_requests += len(scripts)
        num_requests += len(styles)
        num_requests += len(images)
        num_requests += len(videos)
        num_requests += len(iframes)
        
        total_size = page_size
        
        resource_sizes = _estimate_resource_sizes(url, scripts[:5], styles[:5], images[:5])
        total_size += sum(resource_sizes.values())
        
        result = {
            "load_time_ms": round(load_time, 2),
            "total_size_kb": round(total_size / 1024, 2),
            "page_size_kb": round(page_size / 1024, 2),
            "num_requests": num_requests,
            "status_code": status_code,
            "redirect_count": redirect_count,
            "resources": {
                "scripts": len(scripts),
                "stylesheets": len(styles),
                "images": len(images),
                "videos": len(videos),
                "iframes": len(iframes)
            },
            "content_type": response.headers.get('Content-Type', 'unknown'),
            "server": response.headers.get('Server', 'unknown')
        }
        
        logger.info(f"Análisis completado: {load_time:.2f}ms, {num_requests} requests")
        return result
        
    except requests.Timeout:
        logger.error(f"Timeout analizando {url}")
        raise TimeoutError(f"Request timeout after {timeout} seconds")
    
    except requests.RequestException as e:
        logger.error(f"Error de request: {e}")
        raise ConnectionError(f"Failed to fetch URL: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error analizando rendimiento: {e}")
        raise


def _estimate_resource_sizes(base_url: str, scripts, styles, images) -> Dict[str, int]:
    import requests
    
    sizes = {
        'scripts': 0,
        'styles': 0,
        'images': 0
    }
    
    def get_resource_size(url: str) -> int:
        try:
            abs_url = urljoin(base_url, url)
            response = requests.head(abs_url, timeout=2, allow_redirects=True)
            size = response.headers.get('Content-Length', 0)
            return int(size) if size else 0
        except:
            return 0
    
    for script in scripts:
        src = script.get('src', '')
        if src and not src.startswith('data:'):
            sizes['scripts'] += get_resource_size(src)
    
    for style in styles:
        href = style.get('href', '')
        if href and not href.startswith('data:'):
            sizes['styles'] += get_resource_size(href)
    
    for img in images:
        src = img.get('src', '')
        if src and not src.startswith('data:'):
            sizes['images'] += get_resource_size(src)
    
    return sizes


def measure_time_to_first_byte(url: str, timeout: int = 10) -> float:
    import requests
    
    start = time.time()
    
    try:
        with requests.get(url, timeout=timeout, stream=True) as response:
            # Leer el primer byte
            next(response.iter_content(chunk_size=1))
            ttfb = (time.time() - start) * 1000
            return round(ttfb, 2)
    except Exception as e:
        logger.error(f"Error midiendo TTFB: {e}")
        return -1.0


def analyze_lighthouse_metrics(url: str) -> Dict[str, Any]:
    perf = analyze_performance(url)
    ttfb = measure_time_to_first_byte(url)
    
    load_score = max(0, 100 - (perf['load_time_ms'] / 50))  # 5s = 0 points
    size_score = max(0, 100 - (perf['total_size_kb'] / 50))  # 5MB = 0 points
    
    return {
        "performance_score": round((load_score + size_score) / 2),
        "ttfb_ms": ttfb,
        "fcp_estimate_ms": perf['load_time_ms'] * 0.6,  # Estimación
        "metrics": perf
    }