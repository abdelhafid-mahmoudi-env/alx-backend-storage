#!/usr/bin/env/ python3
"""
This module implements the get_page function.
"""

import redis
import requests
from functools import wraps
from typing import Callable

# connect redis
r = redis.Redis(decode_responses=True)


def count_acess_request(method: Callable) -> Callable:
    """
    Decorator function which counts number of requests made to a url and caches
    response
    """

    @wraps(method)
    def wrapper(url):
        """wrapper function"""
        r.incr(f"count:{url}")
        cached_data = r.get(f"cached:{url}")

        if cached_data:
            return cached_data.decode('utf-8')
        #otherwise
        result = method(url)

        r.setex(f"cached:{url}", 10, result)

        return result

    return wrapper


def get_page(url: str) -> str:
    """
    This function fetches HTML content of a particular url and returns it.
    """
    response = requests.get(url)
    return response.text
