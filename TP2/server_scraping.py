#!/usr/bin/env python3
import sys
import os
import argparse
import logging
from aiohttp import web
import socket

# Agregar directorio al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from api.handlers import ScrapingHandler, index_handler

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def create_app(args) -> web.Application:
    app = web.Application()
    
    # Configuración
    app['processing_host'] = args.processing_host
    app['processing_port'] = args.processing_port
    app['workers'] = args.workers
    
    # Crear handler
    scraping_handler = ScrapingHandler(app)
    
    # Configurar rutas
    app.router.add_get('/', index_handler)
    app.router.add_get('/scrape', scraping_handler.scrape)
    app.router.add_get('/health', scraping_handler.health)
    app.router.add_get('/info', scraping_handler.info)
    app.router.add_get('/stats', scraping_handler.stats)
    
    return app


def parse_args():
    parser = argparse.ArgumentParser(
        description='Servidor de Scraping Web Asíncrono',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s -i localhost -p 8000
  %(prog)s -i 0.0.0.0 -p 8000 --processing-host localhost --processing-port 8001
  %(prog)s -i :: -p 8000  # IPv6
        """
    )
    
    parser.add_argument(
        '-i', '--ip',
        required=True,
        help='Dirección de escucha (soporta IPv4/IPv6)'
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        required=True,
        help='Puerto de escucha'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=4,
        help='Número de workers (default: 4)'
    )
    
    parser.add_argument(
        '--processing-host',
        default='localhost',
        help='Host del servidor de procesamiento (default: localhost)'
    )
    
    parser.add_argument(
        '--processing-port',
        type=int,
        default=8001,
        help='Puerto del servidor de procesamiento (default: 8001)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Modo verbose (DEBUG logging)'
    )
    
    return parser.parse_args()


async def on_startup(app: web.Application):
    logger.info("🚀 Servidor de scraping iniciando...")
    logger.info(f"📡 Escuchando en: {app['host']}:{app['port']}")
    logger.info(f"🔧 Servidor de procesamiento: {app['processing_host']}:{app['processing_port']}")
    logger.info(f"⚙️  Workers: {app['workers']}")


async def on_cleanup(app: web.Application):
    logger.info("🛑 Cerrando servidor de scraping...")


def detect_ip_version(ip: str) -> str:
    """
    Detecta si una IP es IPv4 o IPv6.
    FIX: Agregada para manejar mejor las IPs.
    """
    # Casos especiales
    if ip in ['localhost', '127.0.0.1']:
        return 'ipv4'
    if ip in ['::', '::1']:
        return 'ipv6'
    if ip == '0.0.0.0':
        return 'ipv4'
    
    # Intentar parsear
    try:
        socket.inet_pton(socket.AF_INET, ip)
        return 'ipv4'
    except socket.error:
        pass
    
    try:
        socket.inet_pton(socket.AF_INET6, ip)
        return 'ipv6'
    except socket.error:
        pass
    
    # Default a IPv4
    return 'ipv4'


def is_ipv6_available():
    """
    Verifica si IPv6 está disponible en el sistema.
    """
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.close()
        return True
    except (socket.error, OSError):
        return False


def main():
    args = parse_args()
    
    # Configurar nivel de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # FIX: Detectar versión de IP
    ip_version = detect_ip_version(args.ip)
    
    # FIX: Si se solicita IPv6 pero no está disponible, avisar
    if ip_version == 'ipv6' and not is_ipv6_available():
        print(f"\n⚠️  ADVERTENCIA: IPv6 solicitado pero no está disponible en el sistema")
        print(f"   Intentando con IPv4 equivalente...")
        if args.ip in ['::', '::1']:
            args.ip = '0.0.0.0' if args.ip == '::' else '127.0.0.1'
            ip_version = 'ipv4'
        else:
            print(f"❌ No se puede convertir {args.ip} a IPv4")
            return 1
    
    # Imprimir banner
    print("=" * 70)
    print("🚀 SERVIDOR DE SCRAPING WEB - TP2")
    print("=" * 70)
    print(f"📡 Dirección: {args.ip}:{args.port}")
    print(f"🌐 Protocolo: HTTP ({ip_version.upper()})")
    print(f"⚙️  Workers: {args.workers}")
    print(f"🔧 Processing Server: {args.processing_host}:{args.processing_port}")
    if ip_version == 'ipv6':
        print(f"✅ IPv6 activo")
    print("=" * 70)
    print()
    
    try:
        # Crear aplicación
        import asyncio
        app = asyncio.run(create_app(args))
        
        # Guardar configuración para callbacks
        app['host'] = args.ip
        app['port'] = args.port
        
        # Registrar callbacks
        app.on_startup.append(on_startup)
        app.on_cleanup.append(on_cleanup)
        
        # Iniciar servidor
        web.run_app(
            app,
            host=args.ip,
            port=args.port,
            print=lambda x: None  # Suprimir output de aiohttp
        )
        
    except OSError as e:
        if e.errno == 98:  # Address already in use
            logger.error(f"❌ Error: Puerto {args.port} ya está en uso")
            logger.error("   Usa 'lsof -ti:PORT | xargs kill -9' para liberar el puerto")
        elif e.errno == 99:  # Cannot assign requested address
            logger.error(f"❌ Error: No se puede asignar la dirección {args.ip}")
            logger.error("   Verifica que la dirección sea válida en tu sistema")
            if ip_version == 'ipv6':
                logger.error("   IPv6 puede no estar disponible. Intenta con IPv4.")
        else:
            logger.error(f"❌ Error de socket: {e}")
        return 1
    
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrumpido por el usuario")
    
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}", exc_info=True)
        return 1
    
    finally:
        logger.info("✅ Servidor detenido")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())