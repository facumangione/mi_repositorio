import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def analyze_performance(url: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Análisis de rendimiento SIMPLIFICADO y RÁPIDO.
    Hace un request HTTP básico con timeout agresivo.
    """
    options = options or {}
    timeout = 5  # TIMEOUT MUY CORTO: 5 segundos máximo
    
    logger.info(f"⚡ Performance analysis (fast mode): {url}")
    
    try:
        import requests
        
        start_time = time.time()
        
        # Request con timeout muy corto
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={'User-Agent': 'Mozilla/5.0'},
            stream=False  # No streaming
        )
        
        load_time = (time.time() - start_time) * 1000  # ms
        
        # Datos básicos
        status_code = response.status_code
        page_size = len(response.content)
        redirect_count = len(response.history)
        
        # Análisis MÍNIMO de recursos (sin parsear HTML completo)
        content_type = response.headers.get('Content-Type', 'unknown')
        server = response.headers.get('Server', 'unknown')
        
        # Estimación simple de recursos
        resources = {
            "scripts": 0,
            "stylesheets": 0,
            "images": 0,
            "videos": 0,
            "iframes": 0
        }
        
        # Solo contar si es HTML
        if 'html' in content_type.lower():
            # Conteo rápido sin parsing completo
            html_lower = response.text.lower() if len(response.content) < 500000 else ""
            resources["scripts"] = html_lower.count('<script')
            resources["stylesheets"] = html_lower.count('<link') + html_lower.count('rel="stylesheet"')
            resources["images"] = html_lower.count('<img')
        
        num_requests = 1 + sum(resources.values())
        
        result = {
            "load_time_ms": round(load_time, 2),
            "total_size_kb": round(page_size / 1024, 2),
            "page_size_kb": round(page_size / 1024, 2),
            "num_requests": num_requests,
            "status_code": status_code,
            "redirect_count": redirect_count,
            "resources": resources,
            "content_type": content_type,
            "server": server,
            "analysis_mode": "fast"
        }
        
        logger.info(f"✅ Performance OK: {load_time:.2f}ms, {page_size} bytes")
        return result
        
    except requests.Timeout:
        logger.warning(f"⏱️  Timeout ({timeout}s) - Usando valores estimados")
        # FALLBACK: devolver datos estimados en lugar de error
        return {
            "load_time_ms": timeout * 1000,
            "total_size_kb": 0,
            "page_size_kb": 0,
            "num_requests": 1,
            "status_code": 0,
            "redirect_count": 0,
            "resources": {
                "scripts": 0,
                "stylesheets": 0,
                "images": 0,
                "videos": 0,
                "iframes": 0
            },
            "content_type": "unknown",
            "server": "unknown",
            "analysis_mode": "timeout_fallback",
            "note": f"Request timeout after {timeout}s"
        }
    
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        # FALLBACK: devolver datos básicos en lugar de fallar
        return {
            "load_time_ms": 0,
            "total_size_kb": 0,
            "page_size_kb": 0,
            "num_requests": 0,
            "status_code": 0,
            "redirect_count": 0,
            "resources": {
                "scripts": 0,
                "stylesheets": 0,
                "images": 0,
                "videos": 0,
                "iframes": 0
            },
            "content_type": "unknown",
            "server": "unknown",
            "analysis_mode": "error_fallback",
            "error": str(e)
        }
