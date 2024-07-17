#!/usr/bin/env python3
'''A module for interfacing with Redis NoSQL data storage. '''
from functools import wraps
from typing import Any, Callable, Union
import redis
import uuid


def count_calls(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        input_key = f'{method.__qualname__}:inputs'
        output_key = f'{method.__qualname__}:outputs'
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(input_key, str(args))
        result = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(output_key, result)
        return result
    return wrapper


def replay(method: Callable) -> None:
    if method is None or not hasattr(method, '__self__'):
        return
    redis_instance = getattr(method.__self__, '_redis', None)
    if not isinstance(redis_instance, redis.Redis):
        return
    method_name = method.__qualname__
    input_key = f'{method_name}:inputs'
    output_key = f'{method_name}:outputs'
    call_count = 0
    if redis_instance.exists(method_name) != 0:
        call_count = int(redis_instance.get(method_name))
    print(f'{method_name} was called {call_count} times:')
    inputs = redis_instance.lrange(input_key, 0, -1)
    outputs = redis_instance.lrange(output_key, 0, -1)
    for inp, out in zip(inputs, outputs):
        print(f'{method_name}(*{inp.decode("utf-8")}) -> {out}')


class Cache:

    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data:  Union[str, bytes, int, float]) -> str:
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
            self,
            key: str,
            fn: Callable = None,
            ) -> Union[str, bytes, int, float]:
        data = self._redis.get(key)
        return fn(data) if fn is not None else data

    def get_str(self, key: str) -> str:
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        return self.get(key, lambda x: int(x))
