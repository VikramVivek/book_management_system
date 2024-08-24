import os
import time

import redis

# Environment variable to decide whether to use mock or real Redis
USE_MOCK_REDIS = os.getenv("USE_MOCK_REDIS", "False").lower() == "true"


class MockRedisClientWithTTL:
    def __init__(self):
        self.store = {}

    def setex(self, key, time, value):
        expire_at = time.time() + time
        self.store[key] = (value, expire_at)

    def get(self, key):
        value, expire_at = self.store.get(key, (None, 0))
        if expire_at > time.time():
            return value
        else:
            del self.store[key]
            return None


if USE_MOCK_REDIS:
    RedisClient = MockRedisClientWithTTL
else:
    RedisClient = redis.StrictRedis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379/0")
    )

redis_client = RedisClient()
