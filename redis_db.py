import logging
import os
import sys
import threading
from typing import Any

from redis import Redis as r
from config import HOST, PASSWORD, PORT

log = logging.getLogger("telethon")


class Redis(r):
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
        Loads all string-type keys from Redis into the in-memory cache.
        """
        cached_count = 0
        try:
            for key in self.scan_iter():
                # Check the type of the key before attempting to get its value
                if self.type(key).decode('utf-8') == 'string':
                    value = self.get(key)
                    self._cache[key] = value
                    cached_count += 1
            self.logger.info(f"Cached {cached_count} keys")
        except Exception as e:
            self.logger.error(f"Error during caching: {e}")

    def get_key(self, key: Any):
        if key in self._cache:
            return self._cache[key]
        
        data = self.get(key)
        if data is not None:
            self._cache[key] = data
        return data

    def del_key(self, key: Any):
        if key in self._cache:
            del self._cache[key]
        return self.delete(key)

    def set_key(self, key: Any = None, value: Any = None):
        if key is not None and value is not None:
            self._cache[key] = value
            return self.set(key, value)
        return False

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
