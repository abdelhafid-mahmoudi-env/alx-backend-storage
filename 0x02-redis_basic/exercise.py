#!/usr/bin/env python3
"""
Exercise Module
"""
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

def replay(method: Callable) -> None:
    redis_instance = method.__self__._redis
    method_name = method.__qualname__
    input_key = f"{method_name}:inputs"
    output_key = f"{method_name}:outputs"

    inputs = redis_instance.lrange(input_key, 0, -1)
    outputs = redis_instance.lrange(output_key, 0, -1)
    print(f"{method_name} was called {len(inputs)} times:")
    for inp, outp in zip(inputs, outputs):
        inp = inp.decode('utf-8')
        outp = outp.decode('utf-8')
        print(f"{method_name}(*{inp}) -> {outp}")

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

    def get(self, key: str, fn: Optional[Callable] = None) -> Optional[Union[str, bytes, int, float]]:
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
