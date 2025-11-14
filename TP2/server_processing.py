#!/usr/bin/env python3
import sys
import os
import argparse
import socket
import logging
import signal
from concurrent.futures import ProcessPoolExecutor
import time

# Agregar directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from common.protocol import Protocol, MessageType, create_response
from processor.worker_pool import WorkerPool

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def handle_client_connection(client_socket_fd, client_addr, worker_pool_size):
    """
    Esta función se ejecuta en un PROCESO SEPARADO.
    Recibe el file descriptor del socket y recrea el socket en el proceso hijo.
    """
    client_socket = None
    
    try:
        # Recrear socket desde el file descriptor
        client_socket = socket.fromfd(client_socket_fd, socket.AF_INET, socket.SOCK_STREAM)
        
        logger.info(f"🔧 Proceso {os.getpid()} manejando cliente {client_addr}")
        
        # Recibir mensaje
        try:
            message = Protocol.receive_message_sync(client_socket)
        except Exception as e:
            logger.error(f"Error recibiendo mensaje: {e}")
            error_response = create_response(False, error=f"Protocol error: {str(e)}")
            try:
                Protocol.send_message_sync(client_socket, error_response)
            except:
                pass
            return "ERROR"
        
        msg_type = message.get('type', 'unknown')
        url = message.get('url', '')
        
        logger.info(f"📩 Proceso {os.getpid()}: Tarea {msg_type} para {url}")
        
        # Procesar según tipo
        if msg_type == MessageType.PING:
            response = create_response(True, result={
                "message": "PONG from processor",
                "process_id": os.getpid(),
                "using_multiprocessing": True
            })
            
        elif msg_type == MessageType.SHUTDOWN:
            logger.warning(f"⚠️ Comando SHUTDOWN desde {client_addr}")
            response = create_response(True, result={"message": "Shutting down"})
            Protocol.send_message_sync(client_socket, response)
            return "SHUTDOWN"
            
        else:
            # Crear un worker pool temporal para esta tarea
            try:
                with WorkerPool(worker_pool_size) as pool:
                    result = pool.process_task(message)
                    
                    if result.get('success'):
                        result_data = result.get('result')
                        # Añadir info del proceso
                        if isinstance(result_data, dict):
                            result_data['handled_by_process'] = os.getpid()
                        response = create_response(True, result=result_data)
                    else:
                        error_msg = result.get('error', 'Processing failed')
                        logger.error(f"Processing failed: {error_msg}")
                        response = create_response(False, error=error_msg)
            except Exception as e:
                logger.error(f"Error en worker pool: {e}", exc_info=True)
                response = create_response(False, error=f"Worker pool error: {str(e)}")
        
        # Enviar respuesta
        try:
            Protocol.send_message_sync(client_socket, response)
            logger.info(f"✅ Proceso {os.getpid()}: Respuesta enviada a {client_addr}")
        except Exception as e:
            logger.error(f"Error enviando respuesta: {e}")
            return "ERROR"
        
        return "OK"
        
    except Exception as e:
        logger.error(f"❌ Proceso {os.getpid()}: Error fatal: {e}", exc_info=True)
        try:
            if client_socket:
                error_response = create_response(False, error=str(e))
                Protocol.send_message_sync(client_socket, error_response)
        except:
            pass
        return "ERROR"
    
    finally:
        if client_socket:
            try:
                client_socket.close()
            except Exception as e:
                logger.debug(f"Error cerrando socket: {e}")
        logger.info(f"🔌 Proceso {os.getpid()}: Conexión cerrada con {client_addr}")


class MultiprocessingServer:
    """
    Servidor que usa ProcessPoolExecutor para manejar conexiones.
    Cada conexión es procesada en un proceso separado del pool.
    """
    
    def __init__(self, host, port, num_workers=None):
        self.host = host
        self.port = port
        self.num_workers = num_workers or os.cpu_count()
        self.running = False
        self.socket = None
        self.executor = ProcessPoolExecutor(max_workers=self.num_workers)
        
        logger.info(f"✅ Servidor Multiprocessing creado")
        logger.info(f"   Workers: {self.num_workers}")
        logger.info(f"   Dirección: {host}:{port}")
    
    def start(self):
        """Inicia el servidor y comienza a escuchar conexiones"""
        # Crear socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(1.0)  # Timeout para poder interrumpir con Ctrl+C
        
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(10)
            self.running = True
            
            actual_addr = self.socket.getsockname()
            logger.info(f"✅ Servidor escuchando en: {actual_addr}")
            print(f"✅ Servidor iniciado correctamente")
            print(f"📡 Escuchando en: {actual_addr}")
            print(f"⚙️  Pool de {self.num_workers} procesos activo")
            print(f"⏹️  Presiona Ctrl+C para detener\n")
            
            # Loop principal - acepta conexiones
            connection_count = 0
            while self.running:
                try:
                    # Aceptar conexión
                    client_socket, client_addr = self.socket.accept()
                    connection_count += 1
                    logger.info(f"📨 Nueva conexión #{connection_count} de: {client_addr}")
                    
                    # Obtener file descriptor ANTES de cerrar el socket en el proceso padre
                    client_fd = client_socket.fileno()
                    
                    # Enviar al pool de procesos
                    # IMPORTANTE: Pasar el FD, no el socket directamente
                    future = self.executor.submit(
                        handle_client_connection,
                        client_fd,
                        client_addr,
                        max(1, self.num_workers // 2)  # Workers para tareas internas
                    )
                    
                    # Cerrar el socket en el proceso padre
                    # (el proceso hijo lo recreará desde el FD)
                    client_socket.close()
                    
                    # Opcional: agregar callback para logging
                    future.add_done_callback(
                        lambda f: self._log_future_result(f, connection_count)
                    )
                    
                except socket.timeout:
                    # Timeout normal, continuar
                    continue
                    
                except KeyboardInterrupt:
                    logger.info("\n⚠️ Señal de interrupción recibida")
                    break
                    
                except Exception as e:
                    if self.running:
                        logger.error(f"❌ Error aceptando conexión: {e}", exc_info=True)
        
        finally:
            self.shutdown()
    
    def _log_future_result(self, future, conn_num):
        """Callback para logging de resultados"""
        try:
            result = future.result(timeout=0.1)
            if result == "SHUTDOWN":
                logger.info("⚠️ Señal de shutdown recibida desde worker")
                self.running = False
            elif result == "OK":
                logger.debug(f"✅ Conexión #{conn_num} completada exitosamente")
            elif result == "ERROR":
                logger.warning(f"⚠️ Conexión #{conn_num} completada con errores")
        except Exception as e:
            logger.debug(f"Error obteniendo resultado de future: {e}")
    
    def shutdown(self):
        """Cierra el servidor y el pool de workers"""
        logger.info("🛑 Cerrando servidor...")
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.debug(f"Error cerrando socket principal: {e}")
        
        if self.executor:
            logger.info("Cerrando pool de procesos...")
            try:
                self.executor.shutdown(wait=True, cancel_futures=False)
            except Exception as e:
                logger.error(f"Error cerrando executor: {e}")
        
        logger.info("✅ Servidor cerrado")


def parse_args():
    parser = argparse.ArgumentParser(
        description='Servidor de Procesamiento Distribuido con Multiprocessing REAL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s -i localhost -p 8001
  %(prog)s -i 0.0.0.0 -p 8001 -n 8
  %(prog)s -i 127.0.0.1 -p 8001 -n 4

Características:
  ✅ Usa MULTIPROCESSING REAL (ProcessPoolExecutor)
  ✅ Pool de procesos configurable
  ✅ Cada conexión procesada en proceso separado
  ✅ Manejo robusto de sockets entre procesos
        """
    )
    
    parser.add_argument(
        '-i', '--ip',
        required=True,
        help='Dirección de escucha (IPv4)'
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        required=True,
        help='Puerto de escucha'
    )
    
    parser.add_argument(
        '-n', '--processes',
        type=int,
        default=None,
        help='Número de procesos en el pool (default: CPU count)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Modo verbose (DEBUG logging)'
    )
    
    return parser.parse_args()


def check_port_available(host, port):
    """Verifica si el puerto está disponible"""
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(1)
        result = test_socket.connect_ex((host, port))
        test_socket.close()
        return result != 0
    except:
        return True


def find_free_port(start_port, max_attempts=10):
    """Busca un puerto libre"""
    for port in range(start_port, start_port + max_attempts):
        if check_port_available('localhost', port):
            return port
    return None


def main():
    args = parse_args()
    
    # Configurar logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Verificar puerto
    original_port = args.port
    if not check_port_available(args.ip, args.port):
        logger.warning(f"⚠️ Puerto {args.port} está ocupado")
        free_port = find_free_port(args.port + 1)
        
        if free_port:
            print(f"\n{'='*70}")
            print(f"⚠️  PUERTO {args.port} OCUPADO")
            print(f"{'='*70}")
            print(f"\nOpciones:")
            print(f"  1. Liberar: lsof -ti:{args.port} | xargs kill -9")
            print(f"  2. Usar puerto {free_port}")
            print(f"\n¿Usar puerto {free_port}? (s/n): ", end='')
            
            try:
                choice = input().strip().lower()
                if choice == 's':
                    args.port = free_port
                else:
                    return 1
            except KeyboardInterrupt:
                print("\n❌ Cancelado")
                return 1
        else:
            logger.error(f"❌ No hay puertos libres")
            return 1
    
    # Banner
    print("=" * 70)
    print("🚀 SERVIDOR DE PROCESAMIENTO - TP2 (MULTIPROCESSING REAL)")
    print("=" * 70)
    print(f"📍 Dirección: {args.ip}:{args.port}")
    if args.port != original_port:
        print(f"   (Puerto original {original_port} ocupado)")
    print(f"⚙️  Procesos: {args.processes or os.cpu_count()}")
    print(f"🔧 Arquitectura: ProcessPoolExecutor")
    print(f"🌐 Protocolo: TCP/IPv4")
    print("=" * 70)
    print()
    
    server = None
    try:
        server = MultiprocessingServer(args.ip, args.port, args.processes)
        
        def signal_handler(signum, frame):
            print(f"\n⚠️ Señal {signum} recibida")
            if server:
                server.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        server.start()
        
    except OSError as e:
        if e.errno == 98:
            logger.error(f"❌ Puerto {args.port} ocupado")
            print(f"\nSolución: lsof -ti:{args.port} | xargs kill -9")
        else:
            logger.error(f"❌ Error: {e}")
        return 1
    
    except KeyboardInterrupt:
        logger.info("\n⚠️ Interrumpido")
    
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1
    
    finally:
        if server:
            server.shutdown()
        logger.info("✅ Servidor detenido")
    
    return 0


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    sys.exit(main())