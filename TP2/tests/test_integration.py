import pytest
import requests
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

SCRAPING_SERVER = 'http://localhost:8000'
PROCESSING_SERVER_HOST = 'localhost'
PROCESSING_SERVER_PORT = 8001



@pytest.mark.integration
def test_server_a_health():
    response = requests.get(f'{SCRAPING_SERVER}/health', timeout=5)
    assert response.status_code in [200, 503]  # 503 si B no está disponible
    
    data = response.json()
    assert 'status' in data
    assert 'processing_server' in data


@pytest.mark.integration
def test_server_a_info():
    response = requests.get(f'{SCRAPING_SERVER}/info', timeout=5)
    assert response.status_code == 200
    
    data = response.json()
    assert 'server' in data
    assert 'endpoints' in data
    assert 'features' in data


@pytest.mark.integration
def test_server_a_index():
    response = requests.get(SCRAPING_SERVER, timeout=5)
    assert response.status_code == 200
    assert 'text/html' in response.headers.get('Content-Type', '')



@pytest.mark.integration
def test_scrape_simple_url():
    response = requests.get(
        f'{SCRAPING_SERVER}/scrape',
        params={'url': 'http://example.com'},
        timeout=60
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estructura básica
    assert data['status'] == 'success'
    assert data['url'] == 'http://example.com'
    assert 'timestamp' in data
    assert 'scraping_data' in data
    assert 'processing_data' in data


@pytest.mark.integration
def test_scrape_missing_url():
    response = requests.get(f'{SCRAPING_SERVER}/scrape', timeout=5)
    
    assert response.status_code == 400
    data = response.json()
    assert data['status'] == 'error'


@pytest.mark.integration
def test_scrape_invalid_url():
    response = requests.get(
        f'{SCRAPING_SERVER}/scrape',
        params={'url': 'not-a-valid-url'},
        timeout=10
    )
    
    assert response.status_code == 400


@pytest.mark.integration
def test_scraping_data_structure():
    response = requests.get(
        f'{SCRAPING_SERVER}/scrape',
        params={'url': 'http://example.com'},
        timeout=60
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Scraping data
    scraping = data['scraping_data']
    assert 'title' in scraping
    assert 'links' in scraping
    assert 'meta_tags' in scraping
    assert 'structure' in scraping
    assert 'images_count' in scraping
    
    # Metadata
    metadata = data['metadata']
    assert 'basic' in metadata
    assert 'seo' in metadata
    assert 'technical' in metadata
    
    # SEO analysis
    seo = data['seo_analysis']
    assert 'score' in seo
    assert 'grade' in seo
    assert 0 <= seo['score'] <= 100


@pytest.mark.integration
def test_processing_data_present():
    response = requests.get(
        f'{SCRAPING_SERVER}/scrape',
        params={'url': 'http://example.com'},
        timeout=60
    )
    
    assert response.status_code == 200
    data = response.json()
    
    processing = data['processing_data']
    
    # Debe tener al menos uno de estos campos
    has_screenshot = 'screenshot' in processing or 'screenshot_error' in processing
    has_performance = 'performance' in processing or 'performance_error' in processing
    has_thumbnails = 'thumbnails' in processing or 'images_error' in processing
    
    assert has_screenshot or has_performance or has_thumbnails


@pytest.mark.integration
@pytest.mark.slow
def test_full_scraping_workflow():
    
    url = 'http://example.com'
    
    # 1. Cliente hace request a Servidor A
    response = requests.get(
        f'{SCRAPING_SERVER}/scrape',
        params={'url': url},
        timeout=60
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # 2. Verificar que Servidor A hizo su trabajo (scraping)
    assert data['scraping_data']['title'] is not None
    assert len(data['scraping_data']['links']) >= 0
    
    # 3. Verificar que Servidor B procesó las tareas
    processing = data['processing_data']
    
    # Performance debe estar presente (aunque sea con error)
    assert 'performance' in processing or 'performance_error' in processing
    
    # 4. Verificar consolidación
    assert 'status' in data
    assert data['status'] == 'success'


@pytest.mark.integration
def test_transparency():
    response = requests.get(
        f'{SCRAPING_SERVER}/scrape',
        params={'url': 'http://example.com'},
        timeout=60
    )
    
    # Pero recibe datos de ambos servidores
    data = response.json()
    
    # Datos de Servidor A
    assert 'scraping_data' in data
    
    # Datos de Servidor B (transparentemente integrados)
    assert 'processing_data' in data
    
    # Todo en una sola respuesta
    assert response.status_code == 200



@pytest.mark.integration
@pytest.mark.slow
def test_concurrent_requests():
    import concurrent.futures
    
    urls = [
        'http://example.com',
        'http://example.org',
    ]
    
    def scrape_url(url):
        response = requests.get(
            f'{SCRAPING_SERVER}/scrape',
            params={'url': url},
            timeout=60
        )
        return response.status_code == 200
    
    # Ejecutar en paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(scrape_url, urls))
    
    # Todas deberían completar exitosamente
    assert all(results)


@pytest.mark.integration
def test_response_time():
    import time
    
    start = time.time()
    response = requests.get(
        f'{SCRAPING_SERVER}/scrape',
        params={'url': 'http://example.com'},
        timeout=60
    )
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 60  # Debe completar en menos de 60 segundos
    
    # El processing_time_seconds en la respuesta debe ser similar
    data = response.json()
    assert 'processing_time_seconds' in data



@pytest.mark.integration
def test_invalid_url_error():
    response = requests.get(
        f'{SCRAPING_SERVER}/scrape',
        params={'url': 'http://this-domain-does-not-exist-12345.com'},
        timeout=30
    )
    
    # Puede ser 502 (bad gateway) o 500 (internal error)
    assert response.status_code in [500, 502]
    data = response.json()
    assert data['status'] == 'error'


@pytest.mark.integration
def test_server_b_unavailable():
    health = requests.get(f'{SCRAPING_SERVER}/health', timeout=5)
    health_data = health.json()
    
    if health_data.get('processing_server', {}).get('available'):
        pytest.skip("Servidor B está disponible, no se puede probar este caso")
    
    # El scraping debería funcionar pero sin datos de procesamiento
    response = requests.get(
        f'{SCRAPING_SERVER}/scrape',
        params={'url': 'http://example.com'},
        timeout=60
    )
    
    data = response.json()
    
    assert 'scraping_data' in data
    
    # Processing data tendrá errores
    processing = data.get('processing_data', {})
    has_errors = (
        'screenshot_error' in processing or
        'performance_error' in processing or
        'images_error' in processing
    )
    assert has_errors



def is_server_running(url: str) -> bool:
    try:
        response = requests.get(url, timeout=2)
        return response.status_code < 500
    except:
        return False



@pytest.fixture(scope='module', autouse=True)
def check_servers():
    if not is_server_running(SCRAPING_SERVER):
        pytest.skip(f"Servidor A no está corriendo en {SCRAPING_SERVER}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'integration'])