#!/usr/bin/env python3
"""
A module for request caching and tracking.
"""
import redis
import requests
from functools import wraps
from typing import Callable


redis_client = redis.Redis()


def cache_response(method: Callable) -> Callable:
    """
    Decorator to cache the response
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        """
        Wrapper function to handle caching and request tracking.
        """
        if not isinstance(url, str):
            raise TypeError("URL must be a string")
        
        redis_client.incr(f"count:{url}")
        
        cached_result = redis_client.get(f"result:{url}")
        if cached_result:
            return cached_result.decode("utf-8")
        
        result = method(url)
        
        if not isinstance(result, str):
            raise ValueError("The result must be a string")
        
        redis_client.setex(f"result:{url}", 10, result)
        return result
    return wrapper


@cache_response
def get_page(url: str) -> str:
    """
    Fetches the content of a URL
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching the URL {url}: {e}")
