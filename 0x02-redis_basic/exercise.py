#!/usr/bin/env python3
'''A module for interacting with the Redis NoSQL database.
'''
from functools import wraps
from typing import Any, Callable, Union
import redis
import uuid


def count_calls(method: Callable) -> Callable:
    '''Decorator to count the number of calls to a method in the Cache class.
    '''
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        '''Increments the call count of the method and then calls it.
        '''
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    '''Decorator to record the call history of a method in the Cache class.
    '''
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        '''Records the inputs and output of the method call.
        '''
        input_key = f'{method.__qualname__}:inputs'
        output_key = f'{method.__qualname__}:outputs'
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(input_key, str(args))
        result = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(output_key, result)
        return result
    return invoker


def replay(fn: Callable) -> None:
    '''Displays the call history of a method in the Cache class.
    '''
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_instance = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_instance, redis.Redis):
        return
    method_name = fn.__qualname__
    input_key = f'{method_name}:inputs'
    output_key = f'{method_name}:outputs'
    call_count = 0
    if redis_instance.exists(method_name) != 0:
        call_count = int(redis_instance.get(method_name))
    print(f'{method_name} was called {call_count} times:')
    method_inputs = redis_instance.lrange(input_key, 0, -1)
    method_outputs = redis_instance.lrange(output_key, 0, -1)
    for method_input, method_output in zip(method_inputs, method_outputs):
        print(f'{method_name}(*{method_input.decode("utf-8")}) -> {method_output}')


class Cache:
    '''Represents a caching object using Redis.
    '''

    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''Stores data in Redis and returns the generated key.
        '''
        data_key = str(uuid.uuid4())
        self._redis.set(data_key, data)
        return data_key

    def get(
            self,
            key: str,
            fn: Callable = None,
            ) -> Union[str, bytes, int, float]:
        '''Retrieves data from Redis by key and applies an optional transformation function.
        '''
        data = self._redis.get(key)
        return fn(data) if fn is not None else data

    def get_str(self, key: str) -> str:
        '''Retrieves a string value from Redis by key.
        '''
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        '''Retrieves an integer value from Redis by key.
        '''
        return self.get(key, lambda x: int(x))
