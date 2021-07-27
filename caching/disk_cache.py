import logging
import pickle
import os

logger = logging.getLogger(__name__)


class DiskCache:
    """Cache item to disk, expire after recored expire time."""
    __slots__ = ["cache", "name", "expire_seconds"]

    def __init__(self, name, expire_seconds=300):
        """Name the cache, set expire_seconds."""
        self.cache = {}
        self.name = name
        self.expire_seconds = expire_seconds

    def __enter__(self):
        self.cache = self.open_cache()
        return self

    def __exit__(self, *_):
        self.close_cache()

    def __setitem__(self, key, item):
        now = time.time()
        expire_time = now + self.expire_seconds
        self.cache[key] = {
            "time": time.time(),
            "expire_time": expire_time,
            key: item
        }

    def __getitem__(self, key):
        cache_item = self.cache.get(key, None)
        now_time = time.time()
        if cache_item:
            if cache_item["expire_time"] < now_time:
                del self.cache[key]
                return None
            else:
                return cache_item[key]

    def get(self, key, default=None):
        item = self.__getitem__(key)
        return item if item else default

    def open_cache(self):
        cache_file_path = f"{os.getcwd()}/{self.name}.pickle"
        try:
            with open(cache_file_path, 'rb') as f:
                cache = pickle.load(f)
                logger.debug("%i items in cache", len(cache))
        except (EOFError, FileNotFoundError) as err:
            logger.warning("Cannot open cache %s", err)
            cache = self.cache

        return cache

    def close_cache(self):
        try:
            logger.debug("%i items in cache", len(self.cache))
            with open(f"{os.getcwd()}/{self.name}.pickle", 'wb') as f:
                pickle.dump(self.cache, f, protocol=pickle.HIGHEST_PROTOCOL)
        except FileNotFoundError as err:
            logger.warning("Cannot write cache %s", err)
