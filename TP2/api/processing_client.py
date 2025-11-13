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
        logger.info(f"Requesting processing for {url}")
        
        tasks = {
            'screenshot': self._request_screenshot(url),
            'performance': self._request_performance(url),
            'images': self._request_images(url, scraping_data.get('image_urls', []))
        }
        
        # Ejecutar todas en paralelo y recolectar resultados
        results = {}
        for task_name, task in tasks.items():
            try:
                results[task_name] = await task
            except Exception as e:
                logger.error(f"Error in {task_name}: {e}")
                results[task_name] = {
                    'error': str(e),
                    'success': False
                }
        
        # Consolidar resultados
        return self._consolidate_results(results)
    
    async def _request_screenshot(self, url: str) -> Dict[str, Any]:
        return await self._send_task('screenshot_request', url, {
            'timeout': 15,
            'width': 1920,
            'height': 1080
        })
    
    async def _request_performance(self, url: str) -> Dict[str, Any]:
        return await self._send_task('performance_request', url, {
            'timeout': 10
        })
    
    async def _request_images(self, url: str, image_urls: list) -> Dict[str, Any]:
        if not image_urls:
            return {'thumbnails': [], 'success': True}
        
        return await self._send_task('images_request', url, {
            'image_urls': image_urls[:5],  # Máximo 5 imágenes
            'max_images': 5
        })
    
    async def _send_task(self, task_type: str, url: str, data: Dict) -> Dict[str, Any]:
        try:
            # Conectar al servidor B
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout
            )
            
            try:
                # Crear y enviar request
                request = create_request(task_type, url, **data)
                await Protocol.send_message_async(writer, request)
                
                logger.debug(f"Sent {task_type} request for {url}")
                
                # Recibir respuesta
                response = await asyncio.wait_for(
                    Protocol.receive_message_async(reader),
                    timeout=self.timeout
                )
                
                logger.debug(f"Received {task_type} response: {response}")
                
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
            
            finally:
                writer.close()
                await writer.wait_closed()
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout on {task_type} for {url}")
            return {
                'success': False,
                'error': f'Timeout after {self.timeout}s'
            }
        
        except ConnectionRefusedError:
            logger.error(f"Connection refused to processing server")
            return {
                'success': False,
                'error': 'Processing server unavailable'
            }
        
        except Exception as e:
            logger.error(f"Error in {task_type}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _consolidate_results(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        consolidated = {}
        
        # Screenshot
        screenshot_result = results.get('screenshot', {})
        if screenshot_result.get('success'):
            consolidated['screenshot'] = screenshot_result.get('result')
        else:
            consolidated['screenshot'] = None
            if screenshot_result.get('error'):
                consolidated['screenshot_error'] = screenshot_result.get('error')
        
        # Performance
        performance_result = results.get('performance', {})
        if performance_result.get('success'):
            consolidated['performance'] = performance_result.get('result')
        else:
            consolidated['performance'] = None
            if performance_result.get('error'):
                consolidated['performance_error'] = performance_result.get('error')
        
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
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=5
            )
            
            try:
                # Enviar ping
                ping_msg = {'type': MessageType.PING}
                await Protocol.send_message_async(writer, ping_msg)
                
                # Recibir pong
                response = await asyncio.wait_for(
                    Protocol.receive_message_async(reader),
                    timeout=5
                )
                
                return response.get('success', False)
            
            finally:
                writer.close()
                await writer.wait_closed()
        
        except Exception as e:
            logger.warning(f"Processing server ping failed: {e}")
            return False