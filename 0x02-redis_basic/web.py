#!/usr/bin/env python3
"""This module provides a function to fetch."""
import requests
import redis
import functools
from typing import Callable, Any


redis_instance = redis.Redis()


def count_requests(method: Callable) -> Callable:
    """Decorator to count how many times"""
    @functools.wraps(method)
    def wrapper(url: str, *args: Any, **kwargs: Any) -> str:
        count_key = f"count:{url}"
        redis_instance.incr(count_key)
        return method(url, *args, **kwargs)
    return wrapper


def cache_page(expiration: int) -> Callable:
    """Decorator to cache the HTML content"""
    def decorator(method: Callable) -> Callable:
        @functools.wraps(method)
        def wrapper(url: str, *args: Any, **kwargs: Any) -> str:
            cache_key = f"cache:{url}"
            cached_content = redis_instance.get(cache_key)
            if cached_content:
                return cached_content.decode('utf-8')
            html_content = method(url, *args, **kwargs)
            redis_instance.setex(cache_key, expiration, html_content)
            return html_content
        return wrapper
    return decorator


@count_requests
@cache_page(expiration=10)
def get_page(url: str) -> str:
    """Fetch the HTML content of a URL"""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


if __name__ == "__main__":
    url = 'http://slowwly.robertomurray.co.uk'
    try:
        print(get_page(url))
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
