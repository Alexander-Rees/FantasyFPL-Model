"""Redis caching utilities for Flask endpoints"""
import redis
import json
import hashlib
import os
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Redis connection
redis_client = None

def get_redis_client():
    global redis_client
    if redis_client is None:
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        redis_password = os.getenv('REDIS_PASSWORD', None)
        try:
            redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True
            )
            redis_client.ping()  # Test connection
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            redis_client = None
    return redis_client

def cache_result(key_prefix, ttl=300):
    """Decorator to cache function results in Redis"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_key_data = json.dumps({"args": str(args), "kwargs": str(kwargs)}, sort_keys=True)
            cache_key_hash = hashlib.md5(cache_key_data.encode()).hexdigest()
            cache_key = f"{key_prefix}:{cache_key_hash}"
            
            client = get_redis_client()
            if client:
                try:
                    cached = client.get(cache_key)
                    if cached:
                        logger.info(f"Cache HIT: {cache_key}")
                        return json.loads(cached)
                    logger.info(f"Cache MISS: {cache_key}")
                except Exception as e:
                    logger.warning(f"Cache read error: {e}")
            
            # Call function
            result = func(*args, **kwargs)
            
            # Store in cache
            if client:
                try:
                    client.setex(cache_key, ttl, json.dumps(result))
                except Exception as e:
                    logger.warning(f"Cache write error: {e}")
            
            return result
        return wrapper
    return decorator

