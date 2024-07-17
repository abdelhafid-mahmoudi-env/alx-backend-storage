#!/usr/bin/env python3
"""
Exercise file for Redis basic operations.
"""
import redis
import uuid
from typing import Union, Callable

class Cache:
    """
    Cache class using Redis for basic operations.
    """
    def __init__(self) -> None:
        """
        Initialize Cache instance with Redis client.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store input data in Redis and return the generated key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Callable = None) -> Union[str, bytes, int]:
        """
        Retrieve data from Redis using the provided key and optionally
        convert it using the provided function.
        """
        value = self._redis.get(key)
        if value is None:
            return None
        if fn:
            return fn(value)
        return value

    def get_str(self, key: str) -> str:
        """
        Retrieve data from Redis and convert it to a string.
        """
        return self.get(key, fn=lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """
        Retrieve data from Redis and convert it to an integer.
        """
        return self.get(key, fn=int)

    def count_calls(method: Callable) -> Callable:
        """
        Decorator to count the number of times a method is called.
        """
        def wrapper(self, *args, **kwargs):
            count_key = f"calls:{method.__qualname__}"
            self._redis.incr(count_key)
            return method(self, *args, **kwargs)
        return wrapper

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store input data in Redis, using a generated key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def call_history(method: Callable) -> Callable:
        """
        Decorator to store the history of inputs and outputs for a method.
        """
        def wrapper(self, *args, **kwargs):
            inputs_key = f"{method.__qualname__}:inputs"
            outputs_key = f"{method.__qualname__}:outputs"
            self._redis.rpush(inputs_key, str(args))
            result = method(self, *args, **kwargs)
            self._redis.rpush(outputs_key, result)
            return result
        return wrapper

    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store input data in Redis and return the generated key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

def replay(method: Callable) -> None:
    """
    Function to display the history of calls of a particular function.
    """
    inputs_key = f"{method.__qualname__}:inputs"
    outputs_key = f"{method.__qualname__}:outputs"
    inputs = [eval(inp) for inp in self._redis.lrange(inputs_key, 0, -1)]
    outputs = self._redis.lrange(outputs_key, 0, -1)
    
    print(f"{method.__qualname__} was called {len(inputs)} times:")
    for inp, outp in zip(inputs, outputs):
        print(f"{method.__qualname__}(*{inp}) -> {outp.decode('utf-8')}")
