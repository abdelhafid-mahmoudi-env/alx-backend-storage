#!/usr/bin/env python3
"""Web caching and tracking module."""
import requests
import redis
from typing import Callable
from functools import wraps


def cache_with_expiry(expiry: int) -> Callable:
    """Decorator to cache the result."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(url: str) -> str:
            """Wrapper function to cache"""
            r = redis.Redis()
            r.incr(f"count:{url}")
            cached_content = r.get(f"cached:{url}")
            if cached_content:
                return cached_content.decode('utf-8')
            response = func(url)
            r.setex(f"cached:{url}", expiry, response)
            return response
        return wrapper
    return decorator


@cache_with_expiry(10)
def get_page(url: str) -> str:
    """Fetch the HTML content."""
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk"
    print(get_page(url))
