import logging
import os
import sys
import threading
from typing import Any

from redis import Redis as r

# Assuming config.py has these variables
try:
    from config import HOST, PASSWORD, PORT
except ImportError:
    # Fallback for demonstration if config.py is not available
    HOST = "localhost"
    PORT = 6379
    PASSWORD = None

log = logging.getLogger("telethon")


class Redis(r):
    """
    A custom Redis client class with caching and error handling.
    """

    def __init__(
        self,
        host: str = None,
        port: int = None,
        password: str = None,
        logger=log,
        encoding: str = "utf-8",
        decode_responses=True,
        **kwargs,
    ):
        """
        Initializes the Redis client.
        """
        if ":" in host:
            data = host.split(":")
            host = data[0]
            port = int(data[1])
        if host.startswith("http"):
            logger.error("Your REDIS_URI should not start with http!")
            sys.exit(1)
        elif not host or not port:
            logger.error("Host or Port Number not found")
            sys.exit(1)

        kwargs["host"] = host
        if password and len(password) > 1:
            kwargs["password"] = password
        kwargs["port"] = port
        kwargs["encoding"] = encoding
        kwargs["decode_responses"] = decode_responses
        
        try:
            super().__init__(**kwargs)
        except Exception as e:
            logger.exception(f"Error while connecting to redis: {e}")
            sys.exit(1)
            
        self.logger = logger
        self._cache = {}
        threading.Thread(target=self.re_cache, daemon=True).start()

    def re_cache(self):
        """
        Loads all keys from Redis into the in-memory cache.
        """
        try:
            # Use scan_iter for efficiency with a large number of keys
            for key in self.scan_iter():
                # self.get() and self.set() with decode_responses=True will return/expect strings
                value = self.get(key)
                self._cache[key] = value
            self.logger.info("Cached {} keys".format(len(self._cache)))
        except Exception as e:
            self.logger.error(f"Error during caching: {e}")

    def get_key(self, key: Any):
        """
        Retrieves a key from the cache, falling back to Redis if not found.
        """
        if key in self._cache:
            return self._cache[key]
        
        data = self.get(key)
        if data is not None:
            self._cache[key] = data
        return data

    def del_key(self, key: Any):
        """
        Deletes a key from both the cache and Redis.
        """
        if key in self._cache:
            del self._cache[key]
        return self.delete(key)

    def set_key(self, key: Any = None, value: Any = None):
        """
        Sets a key-value pair in both the cache and Redis.
        """
        if key is not None and value is not None:
            self._cache[key] = value
            return self.set(key, value)
        return False

# Database instance
db = Redis(
    host=HOST,
    port=PORT,
    password=PASSWORD if PASSWORD and len(PASSWORD) > 1 else None,
    decode_responses=True,
)

log.info(f"Starting redis on {HOST}:{PORT}")
if not db.ping():
    log.error(f"Redis is not available on {HOST}:{PORT}")
    exit(1)
