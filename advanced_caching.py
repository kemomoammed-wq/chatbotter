# advanced_caching.py: Advanced Caching System for Performance Optimization
import logging
import time
import hashlib
import pickle
import json
from typing import Any, Optional, Dict, Callable
from functools import wraps
from datetime import datetime, timedelta
import os
from pathlib import Path

# Caching backends
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from diskcache import Cache as DiskCache
    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False

logger = logging.getLogger(__name__)

class AdvancedCache:
    """Advanced multi-layer caching system"""
    
    def __init__(
        self,
        cache_type: str = 'multi',  # 'redis', 'disk', 'memory', 'multi'
        redis_url: str = 'redis://localhost:6379/0',
        disk_cache_dir: str = 'cache',
        default_ttl: int = 3600,  # 1 hour
        max_size_mb: int = 1000
    ):
        self.cache_type = cache_type
        self.default_ttl = default_ttl
        self.memory_cache = {}  # Level 1: Memory
        self.memory_cache_timestamps = {}
        
        # Redis (Level 2)
        self.redis_client = None
        if (cache_type == 'redis' or cache_type == 'multi') and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=False)
                self.redis_client.ping()
                logger.info("Redis cache initialized")
            except Exception as e:
                logger.warning(f"Redis not available: {e}")
                self.redis_client = None
        
        # Disk cache (Level 3)
        self.disk_cache = None
        if (cache_type == 'disk' or cache_type == 'multi') and DISKCACHE_AVAILABLE:
            try:
                cache_dir = Path(disk_cache_dir)
                cache_dir.mkdir(exist_ok=True)
                self.disk_cache = DiskCache(str(cache_dir), size_limit=max_size_mb * 1024 * 1024)
                logger.info("Disk cache initialized")
            except Exception as e:
                logger.warning(f"DiskCache not available: {e}")
        
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'memory_size': 0,
            'disk_size': 0
        }
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Get value from cache (multi-layer)"""
        try:
            # Level 1: Memory
            if key in self.memory_cache:
                if self._is_expired_memory(key):
                    del self.memory_cache[key]
                    del self.memory_cache_timestamps[key]
                else:
                    self.stats['hits'] += 1
                    return self.memory_cache[key]
            
            # Level 2: Redis
            if self.redis_client:
                try:
                    value = self.redis_client.get(key)
                    if value:
                        data = pickle.loads(value)
                        # Promote to memory cache
                        self.memory_cache[key] = data['value']
                        self.memory_cache_timestamps[key] = time.time() + data.get('ttl', self.default_ttl)
                        self.stats['hits'] += 1
                        return data['value']
                except Exception as e:
                    logger.debug(f"Redis get error: {e}")
            
            # Level 3: Disk
            if self.disk_cache:
                try:
                    value = self.disk_cache.get(key)
                    if value:
                        # Promote to memory and redis
                        self.set(key, value, ttl=value.get('ttl', self.default_ttl))
                        self.stats['hits'] += 1
                        return value.get('value')
                except Exception as e:
                    logger.debug(f"Disk cache get error: {e}")
            
            self.stats['misses'] += 1
            return default
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache (multi-layer)"""
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            # Level 1: Memory (always)
            self.memory_cache[key] = value
            self.memory_cache_timestamps[key] = time.time() + ttl
            
            # Level 2: Redis
            if self.redis_client:
                try:
                    data = {
                        'value': value,
                        'ttl': ttl,
                        'timestamp': time.time()
                    }
                    serialized = pickle.dumps(data)
                    self.redis_client.setex(key, ttl, serialized)
                except Exception as e:
                    logger.debug(f"Redis set error: {e}")
            
            # Level 3: Disk
            if self.disk_cache:
                try:
                    self.disk_cache.set(key, {'value': value, 'ttl': ttl}, expire=ttl)
                except Exception as e:
                    logger.debug(f"Disk cache set error: {e}")
            
            self.stats['sets'] += 1
            self._update_stats()
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from all cache layers"""
        try:
            # Memory
            if key in self.memory_cache:
                del self.memory_cache[key]
                if key in self.memory_cache_timestamps:
                    del self.memory_cache_timestamps[key]
            
            # Redis
            if self.redis_client:
                try:
                    self.redis_client.delete(key)
                except:
                    pass
            
            # Disk
            if self.disk_cache:
                try:
                    del self.disk_cache[key]
                except:
                    pass
            
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear(self, layer: Optional[str] = None) -> bool:
        """Clear cache (all layers or specific layer)"""
        try:
            if layer is None or layer == 'memory':
                self.memory_cache.clear()
                self.memory_cache_timestamps.clear()
            
            if layer is None or layer == 'redis':
                if self.redis_client:
                    try:
                        self.redis_client.flushdb()
                    except:
                        pass
            
            if layer is None or layer == 'disk':
                if self.disk_cache:
                    try:
                        self.disk_cache.clear()
                    except:
                        pass
            
            self._update_stats()
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def _is_expired_memory(self, key: str) -> bool:
        """Check if memory cache entry is expired"""
        if key not in self.memory_cache_timestamps:
            return True
        return time.time() > self.memory_cache_timestamps[key]
    
    def _update_stats(self):
        """Update cache statistics"""
        self.stats['memory_size'] = len(self.memory_cache)
        
        if self.disk_cache:
            try:
                self.stats['disk_size'] = len(self.disk_cache)
            except:
                pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            'hit_rate': hit_rate,
            'total_requests': total_requests,
            'cache_type': self.cache_type
        }

def cache_result(ttl: int = 3600, key_func: Optional[Callable] = None):
    """Decorator for caching function results"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_advanced_cache()
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_data = {
                    'func': func.__name__,
                    'args': str(args),
                    'kwargs': str(sorted(kwargs.items()))
                }
                key_str = json.dumps(key_data, sort_keys=True)
                cache_key = hashlib.md5(key_str.encode()).hexdigest()
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator

# Global cache instance
_advanced_cache = None

def get_advanced_cache() -> AdvancedCache:
    """Get global advanced cache instance"""
    global _advanced_cache
    if _advanced_cache is None:
        _advanced_cache = AdvancedCache()
    return _advanced_cache

