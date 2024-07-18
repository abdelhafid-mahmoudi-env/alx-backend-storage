#!/usr/bin/env python3
"""
Module pour interagir avec Redis pour la gestion de cache.
"""
import redis
import uuid
from typing import Callable, Union
from functools import wraps


class Cache:
    """
    Classe de gestion de cache utilisant Redis.
    """
    def __init__(self):
        """
        Initialisation du client Redis et nettoyage de la base de données.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Stocke les données dans Redis en utilisant une clé aléatoire.

        Args:
            data: Donnée à stocker (str, bytes, int, float)

        Returns:
            La clé sous laquelle les données sont stockées.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
            self, key: str, fn: Callable = None
            ) -> Union[str, bytes, int, float]:
        """
        Récupère une valeur de Redis et la convertit si nécessaire.

        Args:
            key: La clé Redis.
            fn: Fonction optionnelle de conversion.

        Returns:
            Valeur convertie si fn est fournie, sinon valeur brute.
        """
        value = self._redis.get(key)
        if fn is not None:
            return fn(value)
        return value

    def get_str(self, key: str) -> str:
        """Récupère une chaîne de Redis."""
        return self.get(key, lambda x: x.decode())

    def get_int(self, key: str) -> int:
        """Récupère un entier de Redis."""
        return self.get(key, int)


def count_calls(method: Callable) -> Callable:
    """
    Décorateur compte+stocke nombre fois qu'une méthode est appelée.
    """
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Décorateur qui stocke l'historique des appels de la fonction.
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
    Affiche l'historique des appels pour une méthode donnée.
    """
    inputs_key = f"{method.__qualname__}:inputs"
    outputs_key = f"{method.__qualname__}:outputs"
    inputs = method.__self__._redis.lrange(inputs_key, 0, -1)
    outputs = method.__self__._redis.lrange(outputs_key, 0, -1)
    method_call_count = method.__self__._redis.get(method.__qualname__)

    print(f"{method.__qualname__} was called" +
          f"{method_call_count.decode('utf-8')} times:")
    for input, output in zip(inputs, outputs):
        print(f"{method.__qualname__}{input.decode()} -> {output.decode()}")


# Application des décorateurs
Cache.store = count_calls(Cache.store)
Cache.store = call_history(Cache.store)
