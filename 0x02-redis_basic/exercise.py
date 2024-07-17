#!/usr/bin/env python3
"""Exercise Module"""
import redis
import uuid
import functools
from typing import Union, Callable, Optional


def count_calls(method: Callable) -> Callable:
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(output))
        return output
    return wrapper


def replay(fn: Callable) -> None:
    if fn is None or not hasattr(fn, '__self__'):
        return
    rstore = getattr(fn.__self__, '_redis', None)
    if not isinstance(rstore, redis.Redis):
        return
    input_name = fn.__qualname__
    in_key = '{}:inputs'.format(input_name)
    out_key = '{}:outputs'.format(input_name)
    callcounter = 0
    if rstore.exists(input_name) != 0:
        callcounter = int(rstore.get(input_name))
    print('{} was called {} times:'.format(input_name, callcounter))
    input = rstore.lrange(in_key, 0, -1)
    output = rstore.lrange(out_key, 0, -1)
    for fxn_input, fxn_output in zip(input, output):
        print('{}(*{}) -> {}'.format(
            input_name,
            fxn_input.decode("utf-8"),
            fxn_output,
        ))


class Cache:
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
            self,
            key: str,
            fn: Optional[Callable] = None
            ) -> Optional[Union[str, bytes, int, float]]:
        data = self._redis.get(key)
        if data is not None and fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        data = self.get(key, lambda d: d.decode('utf-8'))
        return data

    def get_int(self, key: str) -> int:
        data = self.get(key, int)
        return data
