"""
Handlers HTTP para el servidor de scraping (Parte A).
Maneja requests de clientes y coordina con el servidor de procesamiento.
"""
import asyncio
import logging
from datetime import datetime
from aiohttp import web
from typing import Dict, Any

from scraper.async_http import AsyncHTTPClient
from scraper.html_parser import parse_html
from scraper.metadata_extractor import MetadataExtractor, analyze_seo
from api.processing_client import ProcessingClient

logger = logging.getLogger(__name__)


class ScrapingHandler:
    def __init__(self, app: web.Application):
        self.app = app
        self.processing_client = ProcessingClient(
            app['processing_host'],
            app['processing_port']
        )
    
    async def scrape(self, request: web.Request) -> web.Response:
        # Obtener parámetros
        url = request.query.get('url')
        if not url:
            return web.json_response(
                {
                    "status": "error",
                    "message": "URL parameter required",
                    "usage": "GET /scrape?url=https://example.com"
                },
                status=400
            )
        
        # Validar URL básica
        if not url.startswith(('http://', 'https://')):
            return web.json_response(
                {
                    "status": "error",
                    "message": "URL must start with http:// or https://"
                },
                status=400
            )
        
        logger.info(f"Scraping request received: {url}")
        start_time = datetime.utcnow()
        
        try:
            # ============ FASE 1: SCRAPING LOCAL (Asyncio) ============
            logger.info(f" Starting scraping: {url}")
            
            async with AsyncHTTPClient(timeout=30) as client:
                html, status_code, http_meta = await client.fetch(url)
            
            logger.info(f" Fetched {url}: {status_code}, {len(html)} bytes")
            
            # Parsing HTML
            scraping_data = parse_html(html, url)
            logger.info(f" Parsed HTML: {scraping_data['title']}")
            
            # Metadata extendida
            metadata = MetadataExtractor.extract_all(scraping_data, url, html)
            
            # Análisis SEO
            seo_analysis = analyze_seo(scraping_data)
            
            # ============ FASE 2: PROCESAMIENTO REMOTO (Servidor B) ============
            logger.info(f" Requesting processing from Server B: {url}")
            
            processing_data = await self.processing_client.request_processing(
                url,
                scraping_data
            )
            
            logger.info(f" Processing completed for {url}")
            
            # ============ FASE 3: CONSOLIDAR RESPUESTA ============
            end_time = datetime.utcnow()
            total_time = (end_time - start_time).total_seconds()
            
            response = {
                "url": url,
                "timestamp": start_time.isoformat() + "Z",
                "processing_time_seconds": round(total_time, 2),
                
                # Datos de scraping
                "scraping_data": {
                    "title": scraping_data['title'],
                    "links": scraping_data['links'][:50],  # Limitar para respuesta
                    "links_count": len(scraping_data['links']),
                    "meta_tags": scraping_data['meta_tags'],
                    "structure": scraping_data['structure'],
                    "images_count": scraping_data['images_count'],
                    "text_stats": scraping_data['text_stats'],
                    "social_links": scraping_data.get('social_links', {})
                },
                
                # Metadata extendida
                "metadata": {
                    "basic": metadata['basic'],
                    "seo": metadata['seo'],
                    "technical": metadata['technical'],
                    "content": metadata['content']
                },
                
                # Análisis SEO
                "seo_analysis": seo_analysis,
                
                # Datos de procesamiento (Servidor B)
                "processing_data": processing_data,
                
                # Estado
                "status": "success",
                "http_status": status_code
            }
            
            logger.info(f" Complete response ready for {url}")
            return web.json_response(response)
        
        except asyncio.TimeoutError:
            logger.error(f" Timeout scraping {url}")
            return web.json_response(
                {
                    "status": "error",
                    "message": "Timeout while fetching URL",
                    "url": url
                },
                status=504
            )
        
        except ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return web.json_response(
                {
                    "status": "error",
                    "message": f"Failed to connect: {str(e)}",
                    "url": url
                },
                status=502
            )
        
        except Exception as e:
            logger.error(f" Error scraping {url}: {e}", exc_info=True)
            return web.json_response(
                {
                    "status": "error",
                    "message": str(e),
                    "url": url
                },
                status=500
            )
    
    async def health(self, request: web.Request) -> web.Response:
        # Verificar servidor de procesamiento
        processing_available = await self.processing_client.ping()
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "server": "scraping",
            "processing_server": {
                "host": self.processing_client.host,
                "port": self.processing_client.port,
                "available": processing_available
            }
        }
        
        status_code = 200 if processing_available else 503
        
        return web.json_response(health_data, status=status_code)
    
    async def info(self, request: web.Request) -> web.Response:
        info_data = {
            "server": "TP2 Scraping Server",
            "version": "1.0.0",
            "endpoints": {
                "/scrape": {
                    "method": "GET",
                    "parameters": {
                        "url": "URL to scrape (required)"
                    },
                    "description": "Scrapes a webpage and returns structured data"
                },
                "/health": {
                    "method": "GET",
                    "description": "Health check endpoint"
                },
                "/info": {
                    "method": "GET",
                    "description": "Server information"
                }
            },
            "features": [
                "Asynchronous web scraping",
                "HTML parsing and structure analysis",
                "Meta tags extraction",
                "SEO analysis and scoring",
                "Screenshot generation (via processing server)",
                "Performance analysis",
                "Image processing and thumbnails"
            ],
            "processing_server": {
                "host": self.app['processing_host'],
                "port": self.app['processing_port']
            }
        }
        
        return web.json_response(info_data)


async def index_handler(request: web.Request) -> web.Response:
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TP2 Scraping Server</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            code {
                background: #f0f0f0;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            .endpoint {
                background: #e8f4f8;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                border-left: 4px solid #0066cc;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1> TP2 Web Scraping Server</h1>
            <p>Servidor de scraping distribuido con análisis asíncrono.</p>
            
            <h2> Endpoints Disponibles</h2>
            
            <div class="endpoint">
                <strong>GET /scrape?url=...</strong>
                <p>Realiza scraping completo de una URL</p>
                <code>curl "http://localhost:8000/scrape?url=https://example.com"</code>
            </div>
            
            <div class="endpoint">
                <strong>GET /health</strong>
                <p>Verifica estado del servidor</p>
                <code>curl http://localhost:8000/health</code>
            </div>
            
            <div class="endpoint">
                <strong>GET /info</strong>
                <p>Información del servidor</p>
                <code>curl http://localhost:8000/info</code>
            </div>
            
            <h2> Características</h2>
            <ul>
                <li>Scraping asíncrono con aiohttp</li>
                <li>Análisis de estructura HTML</li>
                <li>Extracción de meta tags</li>
                <li>Análisis SEO automatizado</li>
                <li>Captura de screenshots</li>
                <li>Análisis de rendimiento</li>
                <li>Procesamiento de imágenes</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    return web.Response(text=html, content_type='text/html')