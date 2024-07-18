#!/usr/bin/env python3
"""exercise"""
import uuid
from typing import Union, Callable, Optional
from functools import wraps

import redis


def count_calls(method: Callable) -> Callable:
    """The decorator that takes a single method."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """increments the count for that key every"""
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """The stores the history of inputs and outputs."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """The saves the input and output of each."""
        input_list_key = method.__qualname__ + ":inputs"
        output_list_key = method.__qualname__ + ":outputs"
        self._redis.rpush(input_list_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_list_key, output)
        return output
    return wrapper


class Cache:
    """The cache class with redis"""
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(
            self,
            data: Union[str, bytes, int, float]
            ) -> str:
        """The store method"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
            self,
            key: str,
            fn: Optional[Callable] = None
            ) -> Union[str, bytes, int, float]:
        """ The get data from redis and transform. """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """ The transform a redis type variable."""
        return self.get(
            key,
            lambda d: d.decode('utf-8')
            )

    def get_int(self, key: str) -> int:
        """ The transform a redis type variable."""
        return self.get(key, int)


def replay(method: Callable):
    """ The display the history of calls."""
    instance = redis.Redis()
    method_name = method.__qualname__
    getmydata = instance.get(method_name)
    try:
        getmydata = getmydata.decode('utf-8')
    except Exception:
        getmydata = 0
    print(f'{method_name} was called {getmydata} times:')
    inputs = instance.lrange(method_name + ":inputs", 0, -1)
    outputs = instance.lrange(method_name + ":outputs", 0, -1)
    for input, output in zip(inputs, outputs):
        try:
            input = input.decode('utf-8')
        except Exception:
            input = ""
        try:
            output = output.decode('utf-8')
        except Exception:
            output = ""
        print(f'{method_name}(*{input}) -> {output}')
