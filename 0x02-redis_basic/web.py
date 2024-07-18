#!/usr/bin/env python3
"""This module provides a function to fetch."""
import requests
import redis
from typing import Callable
import functools


redis_instance = redis.Redis()


def count_requests(method: Callable) -> Callable:
    """Decorator to count how many times"""
    @functools.wraps(method)
    def wrapper(url: str) -> str:
        count_key = f"count:{url}"
        redis_instance.incr(count_key)
        return method(url)
    return wrapper


def cache_page(expiration: int) -> Callable:
    """Decorator to cache the HTML content"""
    def decorator(method: Callable) -> Callable:
        @functools.wraps(method)
        def wrapper(url: str) -> str:
            cache_key = f"cache:{url}"
            cached_content = redis_instance.get(cache_key)
            if cached_content:
                return cached_content.decode('utf-8')
            html_content = method(url)
            redis_instance.setex(cache_key, expiration, html_content)
            return html_content
        return wrapper
    return decorator


@count_requests
@cache_page(expiration=10)
def get_page(url: str) -> str:
    """Fetch the HTML content of a URL"""
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    url = 'http://slowwly.robertomurray.co.uk'
    print(get_page(url))
    print(get_page(url))
    print(f"URL {url} accessed {redis_instance.get(f'count:{url}').decode('utf-8')} times")
