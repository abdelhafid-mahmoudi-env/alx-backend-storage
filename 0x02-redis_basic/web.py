#!/usr/bin/env python3
""" Web cache module """
import redis
import requests
from typing import Callable


def get_page(url: str) -> str:
    _redis = redis.Redis()
    count_key = f"count:{url}"
    _redis.incr(count_key)
    
    cached_data = _redis.get(url)
    if cached_data:
        return cached_data.decode('utf-8')
    
    response = requests.get(url)
    _redis.setex(url, 10, response.text)
    return response.text


if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk"
    print(get_page(url))
    print(get_page(url))
