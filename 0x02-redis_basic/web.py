#!/usr/bin/env python3
"""Web cache module"""
import redis
import requests


def get_page(url: str) -> str:
    r = redis.Redis()
    key = f"count:{url}"
    r.incr(key)
    cached_page = r.get(url)
    if cached_page:
        return cached_page.decode("utf-8")

    response = requests.get(url)
    r.setex(url, 10, response.text)
    return response.text
