
import time
from typing import Any, Dict, Optional
import hashlib


class SimpleCache:
    
    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, tuple] = {}  # key -> (value, timestamp)
        self.ttl = ttl_seconds
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()
    
    def get(self, url: str) -> Optional[Any]:
        key = self._generate_key(url)
        
        if key not in self._cache:
            self.misses += 1
            return None
        
        value, timestamp = self._cache[key]
        
        # Verificar si expiró
        if time.time() - timestamp > self.ttl:
            del self._cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return value
    
    def set(self, url: str, value: Any):
        key = self._generate_key(url)
        self._cache[key] = (value, time.time())
    
    def clear(self):
        self._cache.clear()
        self.hits = 0
        self.misses = 0
    
    def remove(self, url: str) -> bool:
        key = self._generate_key(url)
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clean_expired(self):
        now = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if now - timestamp > self.ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "size": len(self._cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "ttl_seconds": self.ttl
        }


# Instancia global del caché
_global_cache = SimpleCache(ttl_seconds=3600)


def get_cache() -> SimpleCache:
    return _global_cache