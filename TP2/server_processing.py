#!/usr/bin/env python3
"""
Servidor de Procesamiento - Parte B
Usa socketserver y multiprocessing para tareas CPU-bound.

Soporta IPv4 e IPv6 (dual-stack).
Usa ProcessPoolExecutor para procesamiento paralelo.
"""
import sys
import os
import argparse
import socketserver
import socket
import logging
import signal

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


class ProcessingRequestHandler(socketserver.BaseRequestHandler):
    """
    Handler para requests de procesamiento.
    Cada request se maneja en un thread separado (ThreadingTCPServer).
    """
    
    def handle(self):
        """Maneja una conexión de cliente."""
        client_addr = self.client_address
        logger.info(f"📨 Cliente conectado: {client_addr}")
        
        try:
            # Recibir mensaje usando el protocolo
            message = Protocol.receive_message_sync(self.request)
            
            msg_type = message.get('type', 'unknown')
            url = message.get('url', '')
            
            logger.info(f"📩 Tarea recibida: {msg_type} para {url}")
            
            # Procesar según tipo de mensaje
            if msg_type == MessageType.PING:
                # Responder a ping
                response = create_response(True, result={"message": "PONG from processor"})
                
            elif msg_type == MessageType.SHUTDOWN:
                # Comando de shutdown
                logger.warning(f"⚠️  Comando SHUTDOWN recibido de {client_addr}")
                response = create_response(True, result={"message": "Shutting down"})
                Protocol.send_message_sync(self.request, response)
                
                # Señalar shutdown al servidor
                os.kill(os.getpid(), signal.SIGTERM)
                return
            
            else:
                # Procesar con el worker pool
                result = self.server.worker_pool.process_task(message)
                
                if result.get('success'):
                    response = create_response(True, result=result.get('result'))
                else:
                    response = create_response(False, error=result.get('error'))
            
            # Enviar respuesta
            Protocol.send_message_sync(self.request, response)
            logger.info(f"✅ Respuesta enviada a {client_addr}")
            
        except ConnectionError as e:
            logger.error(f"❌ Error de conexión con {client_addr}: {e}")
        
        except Exception as e:
            logger.error(f"❌ Error procesando request de {client_addr}: {e}", exc_info=True)
            
            # Intentar enviar respuesta de error
            try:
                error_response = create_response(False, error=str(e))
                Protocol.send_message_sync(self.request, error_response)
            except:
                pass
        
        finally:
            logger.info(f"👋 Conexión cerrada: {client_addr}")


class DualStackTCPServer(socketserver.ThreadingTCPServer):
    """
    Servidor TCP que soporta IPv4 e IPv6 (dual-stack).
    Usa ThreadingMixIn para manejar múltiples clientes concurrentemente.
    """
    
    # Permitir reutilizar dirección inmediatamente
    allow_reuse_address = True
    
    def __init__(self, server_address, RequestHandlerClass, num_processes=None):
        """
        Inicializa el servidor.
        
        Args:
            server_address: Tupla (host, port)
            RequestHandlerClass: Clase handler para requests
            num_processes: Número de procesos en el pool
        """
        # Inicializar worker_pool como None primero (para evitar AttributeError en server_close)
        self.worker_pool = None
        
        # Detectar si es IPv6
        host, port = server_address
        is_ipv6 = ':' in host or host == ''
        
        if is_ipv6:
            self.address_family = socket.AF_INET6
        else:
            self.address_family = socket.AF_INET
        
        # Inicializar servidor
        super().__init__(server_address, RequestHandlerClass)
        
        # Configurar dual-stack si es IPv6
        if is_ipv6:
            try:
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
                logger.info("✅ Dual-stack habilitado (IPv4 + IPv6)")
            except (AttributeError, OSError) as e:
                logger.warning(f"⚠️  No se pudo habilitar dual-stack: {e}")
        
        # Crear worker pool
        self.worker_pool = WorkerPool(num_processes)
        logger.info(f"✅ Worker pool creado con {self.worker_pool.num_processes} procesos")
    
    def server_close(self):
        """Cierra el servidor y limpia recursos."""
        logger.info("🛑 Cerrando servidor...")
        if self.worker_pool is not None:
            self.worker_pool.shutdown()
        super().server_close()
        logger.info("✅ Servidor cerrado")


def parse_args():
    """Parsea argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Servidor de Procesamiento Distribuido',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s -i localhost -p 8001
  %(prog)s -i 0.0.0.0 -p 8001 -n 8
  %(prog)s -i :: -p 8001          # IPv6, escucha en todas las interfaces
        """
    )
    
    parser.add_argument(
        '-i', '--ip',
        required=True,
        help='Dirección de escucha (IPv4 o IPv6)'
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


def setup_signal_handlers(server):
    """Configura manejadores de señales para shutdown graceful."""
    import sys
    
    def signal_handler(signum, frame):
        print(f"\n⚠️  Señal {signum} recibida. Cerrando servidor...")
        logger.info(f"Señal {signum} recibida. Iniciando shutdown...")
        try:
            server.shutdown()
        except Exception as e:
            logger.error(f"Error durante shutdown: {e}")
            sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Función principal."""
    args = parse_args()
    
    # Configurar nivel de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Imprimir banner
    print("=" * 70)
    print("🔧 SERVIDOR DE PROCESAMIENTO - TP2")
    print("=" * 70)
    print(f"📍 Dirección: {args.ip}:{args.port}")
    print(f"⚙️  Procesos: {args.processes or 'CPU count'}")
    print(f"🔌 Protocolo: TCP (IPv4/IPv6)")
    print("=" * 70)
    print()
    
    try:
        # Crear y configurar servidor
        server = DualStackTCPServer(
            (args.ip, args.port),
            ProcessingRequestHandler,
            num_processes=args.processes
        )
        
        # Configurar signal handlers
        setup_signal_handlers(server)
        
        # Obtener información real del socket
        actual_addr = server.socket.getsockname()
        logger.info(f"✅ Servidor escuchando en: {actual_addr}")
        logger.info("Presiona Ctrl+C para detener\n")
        
        # Servir forever
        server.serve_forever()
        
    except OSError as e:
        if e.errno == 98:  # Address already in use
            logger.error(f"❌ Error: Puerto {args.port} ya está en uso")
            logger.error("   Usa 'lsof -ti:PORT | xargs kill -9' para liberar el puerto")
        elif e.errno == 99:  # Cannot assign requested address
            logger.error(f"❌ Error: No se puede asignar la dirección {args.ip}")
            logger.error("   Verifica que la dirección sea válida en tu sistema")
        else:
            logger.error(f"❌ Error de socket: {e}")
        return 1
    
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrumpido por el usuario")
    
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}", exc_info=True)
        return 1
    
    finally:
        if 'server' in locals():
            server.server_close()
        logger.info("👋 Servidor detenido")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())