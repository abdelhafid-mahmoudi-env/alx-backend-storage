#!/usr/bin/env python3
"""exercise"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator to count the number of calls to a method."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Increments the count for that method key every call."""
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store the history of inputs and outputs."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Saves the input and output of each call."""
        input_list_key = method.__qualname__ + ":inputs"
        output_list_key = method.__qualname__ + ":outputs"
        self._redis.rpush(input_list_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_list_key, output)
        return output
    return wrapper


class Cache:
    """Cache class using Redis."""
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis and return the key."""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
            self,
            key: str,
            fn: Optional[Callable] = None
            ) -> Union[str, bytes, int, float]:
        """Get data from Redis and optionally transform it."""
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """Get data as a string."""
        return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Get data as an integer."""
        return self.get(key, int)


def replay(method: Callable):
    """Display the history of calls to a method."""
    instance = method.__self__._redis
    method_name = method.__qualname__
    call_count = instance.get(method_name)
    if call_count:
        call_count = call_count.decode('utf-8')
    else:
        call_count = 0
    print(f"{method_name} was called {call_count} times:")
    inputs = instance.lrange(method_name + ":inputs", 0, -1)
    outputs = instance.lrange(method_name + ":outputs", 0, -1)
    for input_data, output_data in zip(inputs, outputs):
        try:
            input_data = input_data.decode('utf-8')
        except Exception:
            input_data = ""
        try:
            output_data = output_data.decode('utf-8')
        except Exception:
            output_data = ""
        print(f"{method_name}(*{input_data}) -> {output_data}")
