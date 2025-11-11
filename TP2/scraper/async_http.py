import asyncio
import aiohttp
import logging
from typing import Optional, Tuple, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class AsyncHTTPClient:
    def __init__(self, timeout: int = 30, max_redirects: int = 10):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_redirects = max_redirects
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            connector=aiohttp.TCPConnector(limit=10)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            # Esperar a que se cierren las conexiones
            await asyncio.sleep(0.25)
    
    async def fetch(self, url: str, headers: Dict[str, str] = None) -> Tuple[str, int, Dict[str, Any]]:
        if not self.session:
            raise RuntimeError("Client must be used as context manager")
        
        # Validar URL
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        # Headers por defecto
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        if headers:
            default_headers.update(headers)
        
        logger.info(f"Fetching: {url}")
        
        try:
            async with self.session.get(
                url,
                headers=default_headers,
                allow_redirects=True,
                max_redirects=self.max_redirects
            ) as response:
                
                # Obtener contenido
                html = await response.text()
                status_code = response.status
                
                # Metadata
                metadata = {
                    'final_url': str(response.url),
                    'content_type': response.content_type,
                    'content_length': response.content_length,
                    'charset': response.charset or 'utf-8',
                    'redirected': url != str(response.url)
                }
                
                logger.info(f"Fetched {url}: {status_code}, {len(html)} bytes")
                
                return html, status_code, metadata
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {url}")
            raise TimeoutError(f"Request timeout after {self.timeout.total}s: {url}")
        
        except aiohttp.ClientError as e:
            logger.error(f"Client error fetching {url}: {e}")
            raise ConnectionError(f"Failed to fetch {url}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            raise
    
    async def fetch_multiple(self, urls: list) -> Dict[str, Tuple[str, int, Dict]]:
        if not self.session:
            raise RuntimeError("Client must be used as context manager")
        
        logger.info(f"Fetching {len(urls)} URLs in parallel")
        
        # Crear tasks para todas las URLs
        tasks = {url: asyncio.create_task(self.fetch(url)) for url in urls}
        
        # Esperar a que todas completen
        results = {}
        for url, task in tasks.items():
            try:
                results[url] = await task
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                results[url] = (None, 0, {'error': str(e)})
        
        return results
    
    async def head(self, url: str) -> Dict[str, Any]:
        if not self.session:
            raise RuntimeError("Client must be used as context manager")
        
        try:
            async with self.session.head(url, allow_redirects=True) as response:
                return {
                    'status': response.status,
                    'content_type': response.content_type,
                    'content_length': response.content_length,
                    'headers': dict(response.headers)
                }
        except Exception as e:
            logger.error(f"Error HEAD {url}: {e}")
            return {'error': str(e)}
    
    def _is_valid_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except Exception:
            return False


async def fetch_url(url: str, timeout: int = 30) -> Tuple[str, int]:
    async with AsyncHTTPClient(timeout=timeout) as client:
        html, status, _ = await client.fetch(url)
        return html, status


async def fetch_urls(urls: list, timeout: int = 30) -> Dict[str, Tuple[str, int]]:
    async with AsyncHTTPClient(timeout=timeout) as client:
        results = await client.fetch_multiple(urls)
        # Simplificar resultado
        return {url: (data[0], data[1]) for url, data in results.items() if data[0]}