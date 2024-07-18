#!/usr/bin/env python3
"""Module for implementing"""
import redis
import requests
from typing import Callable
from functools import wraps


r = redis.Redis()


def cache_with_tracking(expiration: int):
    """Decorator to cache the result of a function."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(url: str) -> str:
            count_key = f"count:{url}"
            r.incr(count_key)
            cached_html = r.get(url)
            if cached_html:
                return cached_html.decode('utf-8')
            result = func(url)
            r.setex(url, expiration, result)
            return result
        return wrapper
    return decorator


@cache_with_tracking(expiration=10)
def get_page(url: str) -> str:
    """Obtain the HTML content of a particular."""
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.google.com"
    print(get_page(url))
