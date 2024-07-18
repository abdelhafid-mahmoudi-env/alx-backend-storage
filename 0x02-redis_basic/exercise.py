#!/usr/bin/env python3
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_list_key = method.__qualname__ + ":inputs"
        output_list_key = method.__qualname__ + ":outputs"
        self._redis.rpush(input_list_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_list_key, output)
        return output
    return wrapper


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

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
        return self.get(key, int)


def replay(method: Callable):
    cache = method.__self__
    input_list_key = method.__qualname__ + ":inputs"
    output_list_key = method.__qualname__ + ":outputs"
    inputs = cache._redis.lrange(input_list_key, 0, -1)
    outputs = cache._redis.lrange(output_list_key, 0, -1)
    
    print(f"{method.__qualname__} was called {len(inputs)} times:")
    for i, o in zip(inputs, outputs):
        print(f"{method.__qualname__}(*{i.decode('utf-8')}) -> {o.decode('utf-8')}")
