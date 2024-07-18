#!/usr/bin/env python3
"""
Redis basic operations with Python
"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


class Cache:
    """
    Cache class for interacting with Redis.
    """

    def __init__(self):
        """
        Initialize the Cache class.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a random key.
        
        Args:
            data: Data to store, can be str, bytes, int, or float.
        
        Returns:
            A randomly generated key as a string.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None):
        """
        Retrieve data from Redis and optionally convert it using fn.
        
        Args:
            key: The key to retrieve.
            fn: Optional callable to convert the data.
        
        Returns:
            The retrieved data, optionally converted.
        """
        data = self._redis.get(key)
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """
        Retrieve data as a string.
        
        Args:
            key: The key to retrieve.
        
        Returns:
            The retrieved data as a string.
        """
        return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """
        Retrieve data as an integer.
        
        Args:
            key: The key to retrieve.
        
        Returns:
            The retrieved data as an integer.
        """
        return self.get(key, int)


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of times a method is called.
    
    Args:
        method: The method to wrap.
    
    Returns:
        The wrapped method.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a method.
    
    Args:
        method: The method to wrap.
    
    Returns:
        The wrapped method.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.rpush(f"{method.__qualname__}:inputs", str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(f"{method.__qualname__}:outputs", str(result))
        return result
    return wrapper


def replay(method: Callable):
    """
    Display the history of calls of a particular function.
    
    Args:
        method: The method to replay.
    """
    cache = method.__self__
    inputs = cache._redis.lrange(f"{method.__qualname__}:inputs", 0, -1)
    outputs = cache._redis.lrange(f"{method.__qualname__}:outputs", 0, -1)

    print(f"{method.__qualname__} was called {len(inputs)} times:")
    for input, output in zip(inputs, outputs):
        print(f"{method.__qualname__}(*{input.decode('utf-8')}) -> {output.decode('utf-8')}")


if __name__ == "__main__":
    cache = Cache()

    s1 = cache.store("first")
    print(s1)
    s2 = cache.store("second")
    print(s2)
    s3 = cache.store("third")
    print(s3)

    inputs = cache._redis.lrange(f"{cache.store.__qualname__}:inputs", 0, -1)
    outputs = cache._redis.lrange(f"{cache.store.__qualname__}:outputs", 0, -1)

    print("inputs: {}".format(inputs))
    print("outputs: {}".format(outputs))

    replay(cache.store)
