#!/usr/bin/env python3
"""
This module provides a WebCache class to fetch and cache web pages.
"""
import requests
import redis
from typing import Callable
import functools


class WebCache:
    """WebCache class for caching web pages and tracking access counts"""

    def __init__(self):
        """Initialize the Redis client"""
        self._redis = redis.Redis()

    def count_requests(self, method: Callable) -> Callable:
        """Decorator to count how many times a URL is requested"""
        @functools.wraps(method)
        def wrapper(url: str) -> str:
            count_key = f"count:{url}"
            self._redis.incr(count_key)
            return method(url)
        return wrapper

    def cache_page(self, expiration: int) -> Callable:
        """Decorator to cache the HTML content of a URL for a specified duration"""
        def decorator(method: Callable) -> Callable:
            @functools.wraps(method)
            def wrapper(url: str) -> str:
                cache_key = f"cache:{url}"
                cached_content = self._redis.get(cache_key)
                if cached_content:
                    return cached_content.decode('utf-8')
                html_content = method(url)
                self._redis.setex(cache_key, expiration, html_content)
                return html_content
            return wrapper
        return decorator

    @count_requests
    @cache_page(expiration=10)
    def get_page(self, url: str) -> str:
        """Fetch the HTML content of a URL"""
        response = requests.get(url)
        return response.text


if __name__ == "__main__":
    web_cache = WebCache()
    url = 'http://slowwly.robertomurray.co.uk'
    print(web_cache.get_page(url))
