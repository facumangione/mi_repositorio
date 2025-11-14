import time
from urllib.parse import urlparse
from typing import Dict
from collections import deque


class RateLimiter:    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._requests: Dict[str, deque] = {}  # domain -> timestamps
    
    def _get_domain(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc or url
    
    def can_request(self, url: str) -> bool:
        domain = self._get_domain(url)
        now = time.time()
        
        # Inicializar si no existe
        if domain not in self._requests:
            self._requests[domain] = deque()
        
        # Limpiar requests viejos
        requests = self._requests[domain]
        while requests and requests[0] < now - self.window:
            requests.popleft()
        
        # Verificar límite
        return len(requests) < self.max_requests
    
    def record_request(self, url: str):
        domain = self._get_domain(url)
        now = time.time()
        
        if domain not in self._requests:
            self._requests[domain] = deque()
        
        self._requests[domain].append(now)
    
    def wait_time(self, url: str) -> float:
        if self.can_request(url):
            return 0.0
        
        domain = self._get_domain(url)
        requests = self._requests[domain]
        
        if not requests:
            return 0.0
        
        # Tiempo hasta que expire el request más viejo
        oldest = requests[0]
        now = time.time()
        wait = self.window - (now - oldest)
        
        return max(0.0, wait)
    
    def reset(self, url: str = None):
        if url is None:
            self._requests.clear()
        else:
            domain = self._get_domain(url)
            if domain in self._requests:
                self._requests[domain].clear()
    
    def stats(self) -> Dict[str, any]:
        return {
            "domains": len(self._requests),
            "max_requests": self.max_requests,
            "window_seconds": self.window,
            "requests_by_domain": {
                domain: len(requests)
                for domain, requests in self._requests.items()
            }
        }


# Instancia global del rate limiter
_global_limiter = RateLimiter(max_requests=10, window_seconds=60)


def get_rate_limiter() -> RateLimiter:
    return _global_limiter