#!/usr/bin/env python3
"""
Module to interact with Redis for cache management.
"""
import redis
import uuid
from typing import Callable, Union
from functools import wraps


class Cache:
    """
    Cache management class using Redis.
    """
    def __init__(self):
        """
        Initialize the Redis client and clean the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis using a random key.

        Args:
            data: Data to store (str, bytes, int, float)

        Returns:
            The key under which the data is stored.
        """
        random_key = str(uuid.uuid4())
        self._redis.set(random_key, data)
        return random_key

    def get(self, key: str, conversion_fn: Callable = None) -> Union[str, bytes, int, float]:
        """
        Retrieve a value from Redis and convert it if necessary.

        Args:
            key: The Redis key.
            conversion_fn: Optional conversion function.

        Returns:
            Converted value if conversion_fn is provided, otherwise raw value.
        """
        raw_value = self._redis.get(key)
        if conversion_fn is not None:
            return conversion_fn(raw_value)
        return raw_value

    def get_str(self, key: str) -> str:
        """Retrieve a string from Redis."""
        return self.get(key, lambda x: x.decode())

    def get_int(self, key: str) -> int:
        """Retrieve an integer from Redis."""
        return self.get(key, int)


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count and store the number of times a method is called.
    """
    method_key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.incr(method_key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator that stores the call history of the function.
    """
    inputs_key = f"{method.__qualname__}:inputs"
    outputs_key = f"{method.__qualname__}:outputs"

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.rpush(inputs_key, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(outputs_key, str(result))
        return result
    return wrapper


def replay(method: Callable):
    """
    Display the call history for a given method.
    """
    inputs_key = f"{method.__qualname__}:inputs"
    outputs_key = f"{method.__qualname__}:outputs"
    input_list = method.__self__._redis.lrange(inputs_key, 0, -1)
    output_list = method.__self__._redis.lrange(outputs_key, 0, -1)
    call_count = method.__self__._redis.get(method.__qualname__)

    print(f"{method.__qualname__} was called {call_count.decode('utf-8')} times:")
    for inp, outp in zip(input_list, output_list):
        print(f"{method.__qualname__}{inp.decode()} -> {outp.decode()}")


# Applying the decorators
Cache.store = count_calls(Cache.store)
Cache.store = call_history(Cache.store)
