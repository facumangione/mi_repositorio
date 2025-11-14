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


def normalize_host(host: str) -> str:
    """Normaliza el host para que funcione con IPv4 e IPv6."""
    # Si es localhost, usar 0.0.0.0 que escucha en todas las interfaces
    if host in ['localhost', '127.0.0.1']:
        return '0.0.0.0'
    # Si es ::1 (loopback IPv6), usar :: (todas las interfaces IPv6)
    if host == '::1':
        return '::'
    return host


def main():
    args = parse_args()
    
    # Configurar nivel de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Normalizar host para soportar IPv4/IPv6
    normalized_host = normalize_host(args.ip)
    
    # Imprimir banner
    print("=" * 70)
    print("🌐 SERVIDOR DE SCRAPING WEB - TP2")
    print("=" * 70)
    print(f"📍 Dirección: {args.ip}:{args.port}")
    if normalized_host != args.ip:
        print(f"   (Normalizado a {normalized_host} para escuchar en todas las interfaces)")
    print(f"⚙️  Workers: {args.workers}")
    print(f"🔧 Processing Server: {args.processing_host}:{args.processing_port}")
    print(f"🌐 Protocolo: HTTP (IPv4/IPv6)")
    print("=" * 70)
    print()
    
    try:
        # Crear aplicación
        import asyncio
        app = asyncio.run(create_app(args))
        
        # Guardar configuración para callbacks
        app['host'] = normalized_host
        app['port'] = args.port
        
        # Registrar callbacks
        app.on_startup.append(on_startup)
        app.on_cleanup.append(on_cleanup)
        
        # Iniciar servidor
        web.run_app(
            app,
            host=normalized_host,
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