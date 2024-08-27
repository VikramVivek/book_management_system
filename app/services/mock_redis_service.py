import logging
import os
import time

import redis

# Set up logger
logger = logging.getLogger("app.mock_redis_service")

# Environment variable to decide whether to use mock or real Redis
USE_MOCK_REDIS = os.getenv("USE_MOCK_REDIS", "False").lower() == "true"


class MockRedisClientWithTTL:
    """
    A mock Redis client that simulates Redis operations with TTL (Time to Live).
    """

    def __init__(self):
        self.store = {}
        logger.debug("Initialized MockRedisClientWithTTL.")

    def setex(self, key, time, value):
        """
        Set a key with an expiration time.

        Args:
            key (str): The key to set.
            time (int): Time to live in seconds.
            value (str): The value to store.
        """
        expire_at = time.time() + time
        self.store[key] = (value, expire_at)
        logger.debug(f"Set key {key} with TTL of {time} seconds.")

    def get(self, key):
        """
        Get the value of a key, if it hasn't expired.

        Args:
            key (str): The key to retrieve.

        Returns:
            str: The value stored at the key, or None if the key has expired or
                 does not exist.
        """
        value, expire_at = self.store.get(key, (None, 0))
        if expire_at > time.time():
            logger.debug(f"Retrieved key {key} from mock Redis.")
            return value
        else:
            if key in self.store:
                del self.store[key]
                logger.debug(f"Key {key} expired and was removed.")
            return None


if USE_MOCK_REDIS:
    logger.info("Using MockRedisClientWithTTL as the Redis client.")
    redis_client = MockRedisClientWithTTL()
else:
    logger.info("Using real Redis client.")
    redis_client = redis.StrictRedis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379/0")
    )
