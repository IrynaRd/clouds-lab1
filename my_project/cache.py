import os
import json
import redis
from decimal import Decimal


CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "60"))

REDIS_URL = os.getenv("REDIS_URL")

if CACHE_ENABLED and REDIS_URL:
    redis_client = redis.Redis.from_url(
        REDIS_URL,
        decode_responses = True,
        socket_connect_timeout = 2,
        socket_timeout = 2
    )
else:
    redis_client = None
    print("Caching disabled")

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def cache_get(key):
    if redis_client is None:
        return None
    try:
        data = redis_client.get(key)
        if data is not None:
            return json.loads(data)
    except (redis.RedisError, json.JSONDecodeError) as e:
        print(f"Error reading key '{key}' — {e}")
    return None


def cache_set(key, value, ttl=None):
    if redis_client is None:
        return
    if ttl is None:
        ttl = CACHE_TTL
    try:
        redis_client.setex(key, ttl, json.dumps(value, cls=DecimalEncoder))
    except redis.RedisError as e:
        print(f"Error writing key '{key}' — {e}")


def cache_delete(key):
    if redis_client is None:
        return
    try:
        redis_client.delete(key)
    except redis.RedisError as e:
        print(f"Error deleting key '{key}' — {e}")


def cache_invalidate_films():
    cache_delete("films:all")

