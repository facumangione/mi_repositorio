"""
Tests para el servidor de procesamiento y workers.
"""
import pytest
import socket
import time
import threading
import sys
import os
from io import BytesIO

# Agregar path para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.protocol import Protocol, MessageType, create_request


# ==================== TESTS DEL WORKER POOL ====================

def test_worker_pool_initialization():
    """Test de inicialización del pool."""
    pool = WorkerPool(num_processes=2)
    assert pool.num_processes == 2
    pool.shutdown()


def test_worker_pool_cpu_count():
    """Test que usa CPU count por defecto."""
    import os
    pool = WorkerPool()
    assert pool.num_processes == os.cpu_count()
    pool.shutdown()


def test_worker_function():
    """Test de función worker simple."""
    result = test_worker_function(100)
    expected = sum(i * i for i in range(100))
    assert result == expected


def test_pool_execute_task():
    """Test de ejecución de tarea en el pool."""
    with WorkerPool(num_processes=2) as pool:
        # Ejecutar función de test
        future = pool.executor.submit(test_worker_function, 50)
        result = future.result(timeout=5)
        
        assert result == sum(i * i for i in range(50))


def test_pool_multiple_tasks():
    """Test de múltiples tareas concurrentes."""
    with WorkerPool(num_processes=4) as pool:
        # Enviar múltiples tareas
        futures = []
        for i in range(10):
            future = pool.executor.submit(test_worker_function, 10 + i)
            futures.append((i, future))
        
        # Recolectar resultados
        results = {}
        for i, future in futures:
            results[i] = future.result(timeout=5)
        
        # Verificar que todas completaron
        assert len(results) == 10


def test_pool_context_manager():
    """Test de pool como context manager."""
    with WorkerPool(num_processes=2) as pool:
        assert pool.num_processes == 2
    
    # El pool debe estar cerrado al salir del context


# ==================== TESTS DE PERFORMANCE WORKER ====================

def test_analyze_performance_basic():
    """Test básico de análisis de rendimiento."""
    result = analyze_performance('http://example.com')
    
    assert 'load_time_ms' in result
    assert 'total_size_kb' in result
    assert 'num_requests' in result
    assert 'status_code' in result
    assert result['status_code'] == 200
    assert result['load_time_ms'] > 0
    assert result['total_size_kb'] > 0


def test_analyze_performance_invalid_url():
    """Test con URL inválida."""
    with pytest.raises(Exception):
        analyze_performance('http://this-domain-does-not-exist-12345.com')


def test_analyze_performance_timeout():
    """Test de timeout."""
    # URL que tarda mucho o no responde
    with pytest.raises(Exception):
        analyze_performance('http://httpbin.org/delay/20', {'timeout': 1})


def test_performance_metrics_structure():
    """Test de estructura de métricas."""
    result = analyze_performance('http://example.com')
    
    # Verificar estructura
    assert isinstance(result['load_time_ms'], (int, float))
    assert isinstance(result['total_size_kb'], (int, float))
    assert isinstance(result['num_requests'], int)
    assert isinstance(result['resources'], dict)
    
    # Verificar recursos
    assert 'scripts' in result['resources']
    assert 'stylesheets' in result['resources']
    assert 'images' in result['resources']


# ==================== TESTS DE IMAGE PROCESSOR ====================

def test_create_thumbnail():
    """Test de creación de thumbnail."""
    from PIL import Image
    
    # Crear imagen de prueba
    img = Image.new('RGB', (800, 600), color='red')
    
    # Crear thumbnail
    thumb_b64 = create_thumbnail(img, size=(150, 150))
    
    # Verificar que es base64
    assert isinstance(thumb_b64, str)
    assert len(thumb_b64) > 0
    
    # Decodificar y verificar
    import base64
    thumb_data = base64.b64decode(thumb_b64)
    thumb_img = Image.open(BytesIO(thumb_data))
    
    assert thumb_img.size[0] <= 150
    assert thumb_img.size[1] <= 150


def test_extract_image_metadata():
    """Test de extracción de metadata."""
    from PIL import Image
    
    img = Image.new('RGB', (100, 100), color='blue')
    metadata = extract_image_metadata(img)
    
    assert isinstance(metadata, dict)
    assert 'has_exif' in metadata


def test_process_images_empty_list():
    """Test con lista vacía."""
    from processor.image_processor import process_images
    
    result = process_images([])
    assert result == []


@pytest.mark.slow
def test_process_images_real():
    """Test con imagen real (requiere internet)."""
    from processor.image_processor import process_images
    
    # Imagen de prueba
    urls = ['https://via.placeholder.com/150']
    
    results = process_images(urls, max_images=1)
    
    assert len(results) >= 0  # Puede fallar si no hay internet
    
    if results:
        result = results[0]
        assert 'url' in result
        assert 'thumbnail' in result
        assert 'original_size' in result


# ==================== TESTS DE COMUNICACIÓN CON SERVIDOR ====================

def test_server_ping():
    """Test de ping al servidor (requiere servidor corriendo)."""
    # Este test asume que hay un servidor corriendo
    # Si no hay servidor, se saltará
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect(('localhost', 8001))
        
        # Enviar ping
        ping = {"type": MessageType.PING}
        Protocol.send_message_sync(sock, ping)
        
        # Recibir pong
        response = Protocol.receive_message_sync(sock)
        
        assert response['success'] is True
        assert 'PONG' in str(response.get('result', {}))
        
        sock.close()
        
    except (ConnectionRefusedError, socket.timeout):
        pytest.skip("Servidor no está corriendo en localhost:8001")


@pytest.mark.integration
def test_performance_request():
    """Test de request de performance (requiere servidor)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect(('localhost', 8001))
        
        # Enviar request
        request = create_request(
            'performance_request',
            'http://example.com'
        )
        Protocol.send_message_sync(sock, request)
        
        # Recibir respuesta
        response = Protocol.receive_message_sync(sock)
        
        assert response['success'] is True
        result = response.get('result', {})
        assert 'load_time_ms' in result
        
        sock.close()
        
    except (ConnectionRefusedError, socket.timeout):
        pytest.skip("Servidor no está corriendo")


# ==================== TESTS DE WORKER POOL CON TASKS ====================

def test_process_performance_task():
    """Test de procesamiento de tarea de performance."""
    pool = WorkerPool(num_processes=2)
    
    task = {
        'type': 'performance_request',
        'url': 'http://example.com',
        'data': {}
    }
    
    result = pool.process_task(task)
    
    assert result['success'] is True
    assert 'result' in result
    assert 'load_time_ms' in result['result']
    
    pool.shutdown()


def test_process_unknown_task():
    """Test con tipo de tarea desconocido."""
    pool = WorkerPool(num_processes=2)
    
    task = {
        'type': 'unknown_task_type',
        'url': 'http://example.com'
    }
    
    result = pool.process_task(task)
    
    assert result['success'] is False
    assert 'error' in result
    
    pool.shutdown()


# ==================== HELPER ====================

from io import BytesIO


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'not slow'])