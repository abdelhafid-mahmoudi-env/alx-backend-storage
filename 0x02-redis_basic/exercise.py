#!/usr/bin/env python3
"""Redis and Python exercise"""
import uuid
from typing import Union, Callable, Optional
from functools import wraps

import redis


def count_calls(method: Callable) -> Callable:
    """decorator that takes a single method."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """increments the count for that key every"""
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """stores the history of inputs and outputs."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """saves the input and output of each."""
        input_list_key = method.__qualname__ + ":inputs"
        output_list_key = method.__qualname__ + ":outputs"
        self._redis.rpush(input_list_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_list_key, output)
        return output
    return wrapper


class Cache:
    """Cache class with redis"""
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(
            self,
            data: Union[str, bytes, int, float]
            ) -> str:
        """Store method"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
            self,
            key: str,
            fn: Optional[Callable] = None
            ) -> Union[str, bytes, int, float]:
        """ Get data from redis and transform. """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """ Transform a redis type variable."""
        return self.get(
            key,
            lambda d: d.decode('utf-8')
            )

    def get_int(self, key: str) -> int:
        """ Transform a redis type variable."""
        return self.get(key, int)


def replay(method: Callable):
    """Display the history of calls."""
    r = redis.Redis()
    f_name = method.__qualname__
    n_calls = r.get(f_name)
    try:
        n_calls = n_calls.decode('utf-8')
    except Exception:
        n_calls = 0
    print(f'{f_name} was called {n_calls} times:')
    ins = r.lrange(f_name + ":inputs", 0, -1)
    outs = r.lrange(f_name + ":outputs", 0, -1)
    for i, o in zip(ins, outs):
        try:
            i = i.decode('utf-8')
        except Exception:
            i = ""
        try:
            o = o.decode('utf-8')
        except Exception:
            o = ""
        print(f'{f_name}(*{i}) -> {o}')
