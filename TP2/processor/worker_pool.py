import os
import logging
from concurrent.futures import ProcessPoolExecutor, TimeoutError as FutureTimeoutError
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class WorkerPool:
    
    def __init__(self, num_processes: Optional[int] = None):
        self.num_processes = num_processes or os.cpu_count()
        self.executor = ProcessPoolExecutor(max_workers=self.num_processes)
        logger.info(f"Pool inicializado con {self.num_processes} procesos")
    
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get('type')
        url = task.get('url', '')
        data = task.get('data', {})
        
        logger.info(f"⚙️  Procesando tarea: {task_type} para {url}")
        
        # Timeout reducido según tipo de tarea
        timeout_map = {
            'screenshot_request': 15,
            'performance_request': 10,
            'images_request': 20
        }
        
        timeout = timeout_map.get(task_type, 15)
        
        try:
            if task_type == 'screenshot_request':
                from processor.screenshot import generate_screenshot
                logger.debug(f"  → Ejecutando screenshot en proceso")
                future = self.executor.submit(generate_screenshot, url, data)
                result = future.result(timeout=timeout)
                
            elif task_type == 'performance_request':
                from processor.performance import analyze_performance
                logger.debug(f"  → Ejecutando performance en proceso")
                future = self.executor.submit(analyze_performance, url, data)
                result = future.result(timeout=timeout)
                
            elif task_type == 'images_request':
                from processor.image_processor import process_images
                image_urls = data.get('image_urls', [])
                max_images = data.get('max_images', 5)
                logger.debug(f"  → Ejecutando images en proceso")
                future = self.executor.submit(process_images, image_urls, max_images)
                result = future.result(timeout=timeout)
            
            else:
                logger.warning(f"❌ Tipo de tarea desconocido: {task_type}")
                return {
                    "success": False,
                    "error": f"Unknown task type: {task_type}"
                }
            
            logger.info(f"✅ Tarea completada: {task_type}")
            return {
                "success": True,
                "result": result
            }
            
        except FutureTimeoutError:
            logger.error(f"⏱️  Timeout procesando {task_type} para {url} (>{timeout}s)")
            return {
                "success": False,
                "error": f"Timeout after {timeout} seconds"
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando {task_type}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def shutdown(self, wait: bool = True):
        logger.info("Cerrando pool de procesos...")
        self.executor.shutdown(wait=wait)
        logger.info("Pool cerrado")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
