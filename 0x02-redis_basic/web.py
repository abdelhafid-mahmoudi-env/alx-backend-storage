#!/usr/bin/env python3
"""
Web cache and URL tracker
"""
import redis
import requests
from typing import Callable


def count_calls(method: Callable) -> Callable:
    """Decorator to count the number of calls to a method"""
    def wrapper(self, *args, **kwargs):
        self._redis.incr(f"count:{args[0]}")
        return method(self, *args, **kwargs)
    return wrapper


class WebCache:
    """Web cache class for caching web pages"""

    def __init__(self):
        """Initialize the Redis client"""
        self._redis = redis.Redis()

    @count_calls
    def get_page(self, url: str) -> str:
        """Get the content of a URL and cache it with an expiration time"""
        cached_page = self._redis.get(url)
        if cached_page:
            return cached_page.decode('utf-8')
        response = requests.get(url)
        self._redis.setex(url, 10, response.text)
        return response.text


if __name__ == "__main__":
    cache = WebCache()
    url = "http://slowwly.robertomurray.co.uk"
    print(cache.get_page(url))
