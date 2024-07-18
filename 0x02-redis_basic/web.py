#!/usr/bin/env python3
import requests
import redis

r = redis.Redis()

def get_page(url: str) -> str:
    r.incr(f"count:{url}")
    cached_page = r.get(url)
    if cached_page:
        return cached_page.decode('utf-8')
    
    response = requests.get(url)
    r.setex(url, 10, response.text)
    return response.text
