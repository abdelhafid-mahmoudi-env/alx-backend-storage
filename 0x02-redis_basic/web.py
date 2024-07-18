#!/usr/bin/env python3
"""Web caching and tracking"""
import requests
import redis
from typing import Callable
from functools import wraps


r = redis.Redis()


def cache_with_expiry(expiry: int):
    """Decorator to cache the result."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(url: str) -> str:
            """Wrapper function to cache with expiry."""
            # Track access count
            r.incr(f"count:{url}")

            # Try to get cached content
            cached_content = r.get(f"cached:{url}")
            if cached_content:
                return cached_content.decode('utf-8')

            # Fetch new content if not cached
            response = func(url)
            r.setex(f"cached:{url}", expiry, response)
            return response
        return wrapper
    return decorator


@cache_with_expiry(10)
def get_page(url: str) -> str:
    """Fetch the HTML content of a URL and cache it."""
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk"
    print(get_page(url))
    print(get_page(url))
    print(get_page(url))
