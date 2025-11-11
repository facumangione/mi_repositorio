import os
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError
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
        
        logger.info(f"Procesando tarea: {task_type} para {url}")
        
        try:
            # Seleccionar worker según tipo de tarea
            if task_type == 'screenshot_request':
                from processor.screenshot import generate_screenshot
                future = self.executor.submit(generate_screenshot, url, data)
                result = future.result(timeout=30)
                
            elif task_type == 'performance_request':
                from processor.performance import analyze_performance
                future = self.executor.submit(analyze_performance, url, data)
                result = future.result(timeout=30)
                
            elif task_type == 'images_request':
                from processor.image_processor import process_images
                image_urls = data.get('image_urls', [])
                max_images = data.get('max_images', 5)
                future = self.executor.submit(process_images, image_urls, max_images)
                result = future.result(timeout=30)
            
            elif task_type == 'batch_request':
                # Procesar múltiples tareas en paralelo
                result = self._process_batch(task)
                
            else:
                logger.warning(f"Tipo de tarea desconocido: {task_type}")
                return {
                    "success": False,
                    "error": f"Unknown task type: {task_type}"
                }
            
            logger.info(f"Tarea completada: {task_type}")
            return {
                "success": True,
                "result": result
            }
            
        except TimeoutError:
            logger.error(f"Timeout procesando {task_type} para {url}")
            return {
                "success": False,
                "error": f"Timeout after 30 seconds"
            }
            
        except Exception as e:
            logger.error(f"Error procesando {task_type}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_batch(self, task: Dict[str, Any]) -> Dict[str, Any]:
        subtasks = task.get('data', {}).get('tasks', [])
        results = {}
        
        # Enviar todas las subtareas al pool
        futures = {}
        for subtask in subtasks:
            task_id = subtask.get('id', str(len(futures)))
            future = self.executor.submit(self._execute_subtask, subtask)
            futures[task_id] = future
        
        # Recolectar resultados
        for task_id, future in futures.items():
            try:
                results[task_id] = future.result(timeout=30)
            except Exception as e:
                results[task_id] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def _execute_subtask(self, subtask: Dict[str, Any]) -> Dict[str, Any]:
        # Reutilizar la lógica de process_task pero sin recursión infinita
        task_type = subtask.get('type')
        
        if task_type == 'screenshot_request':
            from processor.screenshot import generate_screenshot
            url = subtask.get('url', '')
            data = subtask.get('data', {})
            return generate_screenshot(url, data)
        
        # Agregar más tipos según sea necesario
        return {"error": "Subtask type not implemented"}
    
    def shutdown(self, wait: bool = True):
        logger.info("Cerrando pool de procesos...")
        self.executor.shutdown(wait=wait)
        logger.info("Pool cerrado")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


# Función helper para testing
def test_worker_function(n: int) -> int:
    import time
    time.sleep(0.1)  # Simular trabajo
    return sum(i * i for i in range(n))