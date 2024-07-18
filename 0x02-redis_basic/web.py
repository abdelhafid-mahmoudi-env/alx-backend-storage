#!/usr/bin/env python3
"""This module provides a function"""
import requests
import redis
from typing import Callable


redis_instance = redis.Redis()


def get_page(url: str) -> str:
    cache_key = f"count:{url}"
    html_content = redis_instance.get(cache_key)
    if html_content:
        return html_content.decode('utf-8')
    response = requests.get(url)
    html_content = response.text
    redis_instance.setex(cache_key, 10, html_content)
    redis_instance.incr(cache_key)
    return html_content
