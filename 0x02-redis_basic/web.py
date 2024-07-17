#!/usr/bin/env python3
'''Implementing an expiring web cache and tracker'''
import redis
import requests
from datetime import timedelta


def get_page(url: str) -> str:
    '''Define get_page'''
    if url is None or len(url.strip()) == 0:
        return ''
    redis_store = redis.Redis()
    r_key = 'result:{}'.format(url)
    req_uest = 'count:{}'.format(url)
    result = redis_store.get(r_key)
    if result is not None:
        redis_store.incr(req_uest)
        return result.decode('utf-8')
    result = requests.get(url).content.decode('utf-8')
    redis_store.setex(r_key, timedelta(seconds=10), result)
    return result
