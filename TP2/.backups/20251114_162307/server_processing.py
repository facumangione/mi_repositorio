#!/usr/bin/env python3
import sys
import os
import argparse
import socket
import logging
import signal
from concurrent.futures import ProcessPoolExecutor
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from common.protocol import Protocol, MessageType, create_response
from processor.worker_pool import WorkerPool

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def handle_client_connection(client_socket_fd, client_addr, worker_pool_size):
    """Maneja conexión de cliente en proceso separado."""
    client_socket = None
    try:
        # Recrear socket desde FD
        client_socket = socket.fromfd(client_socket_fd, socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(30)
        
        logger.info(f"🔧 Proceso {os.getpid()} manejando cliente {client_addr}")
        
        # Recibir mensaje
        message = Protocol.receive_message_sync(client_socket)
        msg_type = message.get('type', 'unknown')
        url = message.get('url', '')
        
        logger.info(f"📩 Proceso {os.getpid()}: Tarea {msg_type} para {url}")
        
        # Procesar mensaje
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
            # Procesar con worker pool
            with WorkerPool(worker_pool_size) as pool:
                result = pool.process_task(message)
                
                if result.get('success'):
                    result_data = result.get('result')
                    if isinstance(result_data, dict):
                        result_data['handled_by_process'] = os.getpid()
                    response = create_response(True, result=result_data)
                else:
                    response = create_response(False, error=result.get('error'))
        
        # Enviar respuesta
        Protocol.send_message_sync(client_socket, response)
        logger.info(f"✅ Proceso {os.getpid()}: Respuesta enviada")
        
        return "OK"
        
    except socket.timeout:
        logger.error(f"⏱️ Timeout en proceso {os.getpid()}")
        try:
            if client_socket:
                error_response = create_response(False, error="Request timeout")
                Protocol.send_message_sync(client_socket, error_response)
        except:
            pass
        return "TIMEOUT"
        
    except Exception as e:
        logger.error(f"❌ Error en proceso {os.getpid()}: {e}", exc_info=True)
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
                client_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                client_socket.close()
            except:
                pass
        logger.info(f"🔌 Proceso {os.getpid()}: Conexión cerrada")


class MultiprocessingServer:
    """Servidor que usa ProcessPoolExecutor."""
    
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
        """Inicia el servidor."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(1.0)
        
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
            
            connection_count = 0
            
            while self.running:
                try:
                    client_socket, client_addr = self.socket.accept()
                    connection_count += 1
                    logger.info(f"📨 Nueva conexión #{connection_count} de: {client_addr}")
                    
                    # Duplicar FD antes de cerrar en proceso padre
                    client_fd = client_socket.fileno()
                    client_fd_dup = os.dup(client_fd)
                    
                    # Enviar al pool
                    future = self.executor.submit(
                        handle_client_connection,
                        client_fd_dup,
                        client_addr,
                        max(1, self.num_workers // 2)
                    )
                    
                    # Cerrar en proceso padre
                    client_socket.close()
                    
                    # Verificar resultado (sin bloquear mucho)
                    try:
                        result = future.result(timeout=0.1)
                        if result == "OK":
                            logger.info(f"✅ Conexión #{connection_count} completada exitosamente")
                        else:
                            logger.warning(f"⚠️ Conexión #{connection_count} completada con {result}")
                    except:
                        # El proceso sigue trabajando
                        pass
                        
                except socket.timeout:
                    continue
                except KeyboardInterrupt:
                    logger.info("\n⚠️ Señal de interrupción recibida")
                    break
                except Exception as e:
                    if self.running:
                        logger.error(f"❌ Error aceptando conexión: {e}")
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Cierra el servidor."""
        logger.info("🛑 Cerrando servidor...")
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        if self.executor:
            logger.info("Cerrando pool de procesos...")
            self.executor.shutdown(wait=True, cancel_futures=False)
        
        logger.info("✅ Servidor cerrado")


def parse_args():
    parser = argparse.ArgumentParser(
        description='Servidor de Procesamiento con Multiprocessing REAL'
    )
    
    parser.add_argument('-i', '--ip', required=True, help='Dirección de escucha')
    parser.add_argument('-p', '--port', type=int, required=True, help='Puerto')
    parser.add_argument('-n', '--processes', type=int, default=None, help='Número de procesos')
    parser.add_argument('-v', '--verbose', action='store_true', help='Modo verbose')
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("=" * 70)
    print("🚀 SERVIDOR DE PROCESAMIENTO - TP2 (MULTIPROCESSING)")
    print("=" * 70)
    print(f"📍 Dirección: {args.ip}:{args.port}")
    print(f"⚙️  Procesos: {args.processes or os.cpu_count()}")
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
