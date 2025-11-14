import asyncio
import logging
from typing import Dict, Any, Optional
from common.protocol import Protocol, MessageType, create_request

logger = logging.getLogger(__name__)


class ProcessingClient:

    def __init__(self, host: str, port: int, timeout: int = 30):
        self.host = host
        self.port = port
        self.timeout = timeout
        logger.info(f"Processing client configured: {host}:{port}")
    
    async def request_processing(self, url: str, scraping_data: Dict) -> Dict[str, Any]:
        """Solicita procesamiento completo al servidor B."""
        logger.info(f"Requesting processing for {url}")
        
        # Ejecutar todas las tareas en paralelo
        tasks = {
            'screenshot': self._request_screenshot(url),
            'performance': self._request_performance(url),
            'images': self._request_images(url, scraping_data.get('image_urls', []))
        }
        
        # Recolectar resultados con timeout individual por tarea
        results = {}
        for task_name, task in tasks.items():
            try:
                results[task_name] = await asyncio.wait_for(task, timeout=self.timeout)
            except asyncio.TimeoutError:
                logger.error(f"Timeout en {task_name} para {url}")
                results[task_name] = {
                    'error': f'Timeout after {self.timeout}s',
                    'success': False
                }
            except Exception as e:
                logger.error(f"Error en {task_name}: {e}")
                results[task_name] = {
                    'error': str(e),
                    'success': False
                }
        
        # Consolidar resultados
        return self._consolidate_results(results)
    
    async def _request_screenshot(self, url: str) -> Dict[str, Any]:
        """Solicita screenshot del URL."""
        return await self._send_task('screenshot_request', url, {
            'timeout': 15,
            'width': 1920,
            'height': 1080
        })
    
    async def _request_performance(self, url: str) -> Dict[str, Any]:
        """Solicita análisis de performance."""
        return await self._send_task('performance_request', url, {
            'timeout': 10
        })
    
    async def _request_images(self, url: str, image_urls: list) -> Dict[str, Any]:
        """Solicita procesamiento de imágenes."""
        if not image_urls:
            return {'thumbnails': [], 'success': True}
        
        return await self._send_task('images_request', url, {
            'image_urls': image_urls[:5],  # Máximo 5 imágenes
            'max_images': 5
        })
    
    async def _send_task(self, task_type: str, url: str, data: Dict) -> Dict[str, Any]:
        """Envía una tarea al servidor de procesamiento y espera respuesta."""
        reader = None
        writer = None
        
        try:
            # Conectar al servidor B con timeout
            logger.debug(f"Conectando a {self.host}:{self.port} para {task_type}")
            
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(self.host, self.port),
                    timeout=5  # Timeout de conexión
                )
            except asyncio.TimeoutError:
                logger.error(f"Timeout conectando a {self.host}:{self.port}")
                return {
                    'success': False,
                    'error': f'Connection timeout to processing server'
                }
            except ConnectionRefusedError:
                logger.error(f"Conexión rechazada por {self.host}:{self.port}")
                return {
                    'success': False,
                    'error': 'Processing server unavailable (connection refused)'
                }
            
            logger.debug(f"Conectado, enviando {task_type} para {url}")
            
            # Crear y enviar request
            request = create_request(task_type, url, **data)
            await Protocol.send_message_async(writer, request)
            
            logger.debug(f"Request enviado, esperando respuesta...")
            
            # Recibir respuesta con timeout
            try:
                response = await asyncio.wait_for(
                    Protocol.receive_message_async(reader),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"Timeout esperando respuesta de {task_type}")
                return {
                    'success': False,
                    'error': f'Response timeout after {self.timeout}s'
                }
            
            logger.debug(f"Respuesta recibida para {task_type}")
            
            # Procesar respuesta
            if response.get('success'):
                return {
                    'success': True,
                    'result': response.get('result', {})
                }
            else:
                return {
                    'success': False,
                    'error': response.get('error', 'Unknown error')
                }
        
        except ConnectionResetError:
            logger.error(f"Conexión cerrada por el servidor durante {task_type}")
            return {
                'success': False,
                'error': 'Connection reset by server'
            }
        
        except Exception as e:
            logger.error(f"Error inesperado en {task_type}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
        
        finally:
            # Cerrar conexión
            if writer:
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception as e:
                    logger.debug(f"Error cerrando conexión: {e}")
    
    def _consolidate_results(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """Consolida resultados de todas las tareas."""
        consolidated = {}
        
        # Screenshot
        screenshot_result = results.get('screenshot', {})
        if screenshot_result.get('success'):
            consolidated['screenshot'] = screenshot_result.get('result')
        else:
            consolidated['screenshot'] = None
            if screenshot_result.get('error'):
                consolidated['screenshot_error'] = screenshot_result.get('error')
        
        # Performance - CRÍTICO: Asegurar que siempre esté presente
        performance_result = results.get('performance', {})
        if performance_result.get('success'):
            result = performance_result.get('result', {})
            # Asegurar que el resultado tenga la estructura correcta
            if isinstance(result, dict) and 'load_time_ms' in result:
                consolidated['performance'] = result
            else:
                logger.warning(f"Performance result malformado: {result}")
                consolidated['performance'] = None
                consolidated['performance_error'] = 'Invalid performance data structure'
        else:
            consolidated['performance'] = None
            error_msg = performance_result.get('error', 'Performance analysis failed')
            consolidated['performance_error'] = error_msg
            logger.warning(f"Performance failed: {error_msg}")
        
        # Images
        images_result = results.get('images', {})
        if images_result.get('success'):
            consolidated['thumbnails'] = images_result.get('result', [])
        else:
            consolidated['thumbnails'] = []
            if images_result.get('error'):
                consolidated['images_error'] = images_result.get('error')
        
        return consolidated
    
    async def ping(self) -> bool:
        """Verifica conectividad con el servidor de procesamiento."""
        reader = None
        writer = None
        
        try:
            logger.debug(f"Pinging {self.host}:{self.port}")
            
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=5
            )
            
            # Enviar ping
            ping_msg = {'type': MessageType.PING}
            await Protocol.send_message_async(writer, ping_msg)
            
            # Recibir pong
            response = await asyncio.wait_for(
                Protocol.receive_message_async(reader),
                timeout=5
            )
            
            is_available = response.get('success', False)
            logger.debug(f"Ping result: {'success' if is_available else 'failed'}")
            return is_available
        
        except ConnectionRefusedError:
            logger.warning(f"Processing server not available at {self.host}:{self.port} (connection refused)")
            return False
        
        except asyncio.TimeoutError:
            logger.warning(f"Processing server ping timeout")
            return False
        
        except Exception as e:
            logger.warning(f"Processing server ping failed: {e}")
            return False
        
        finally:
            if writer:
                try:
                    writer.close()
                    await writer.wait_closed()
                except:
                    pass