#!/usr/bin/env python3
"""
This module provides functionality to fetch HTML content from a URL,
while counting requests and caching responses using Redis.
"""

import requests
import redis
from typing import Callable, Any
import functools

# Initialize Redis instance
redis_instance = redis.Redis()


def count_requests(method: Callable) -> Callable:
    """
    Decorator to count how many times a URL is requested.
    
    Args:
        method (Callable): The method to be decorated.
    
    Returns:
        Callable: The decorated method.
    """
    @functools.wraps(method)
    def wrapper(url: str, *args: Any, **kwargs: Any) -> str:
        count_key = f"count:{url}"
        redis_instance.incr(count_key)
        return method(url, *args, **kwargs)
    return wrapper


def cache_page(expiration: int) -> Callable:
    """
    Decorator to cache the HTML content of a URL.
    
    Args:
        expiration (int): The cache expiration time in seconds.
    
    Returns:
        Callable: The decorated method.
    """
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
@cache_page(expiration=600)  # Set expiration to 10 minutes
def get_page(url: str) -> str:
    """
    Fetch the HTML content of a URL.
    
    Args:
        url (str): The URL to fetch.
    
    Returns:
        str: The HTML content of the URL.
    
    Raises:
        HTTPError: An error occurred accessing the URL.
    """
    response = requests.get(url)
    response.raise_for_status()  # Ensure we handle potential HTTP errors
    return response.text


if __name__ == "__main__":
    url = 'http://slowwly.robertomurray.co.uk'
    try:
        print(get_page(url))
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
