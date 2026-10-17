"""Декораторы логирования, мемоизации и повторного выполнения."""

import inspect
import logging
from functools import wraps

from lab4.functions import require_integer

logger = logging.getLogger(__name__)


def log_calls(function):
    """Среднее №7: записать вызов, результат или исключение в журнал."""
    @wraps(function)
    def wrapper(*args, **kwargs):
        logger.info("Вызов %s: args=%r, kwargs=%r",
                    function.__name__, args, kwargs)
        try:
            result = function(*args, **kwargs)
        except Exception:
            logger.exception("Ошибка в %s", function.__name__)
            raise
        logger.info("Результат %s: %r", function.__name__, result)
        return result
    return wrapper


def memoize(function):
    """Повышенное №2: собственный кэш результатов чистой функции.

    Эквивалентные позиционные и именованные аргументы имеют один ключ.
    Значения аргументов должны быть хешируемыми; ошибки не кэшируются.
    """
    signature = inspect.signature(function)
    cache = {}

    @wraps(function)
    def wrapper(*args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        parts = []
        for name, value in bound.arguments.items():
            parameter = signature.parameters[name]
            if parameter.kind == inspect.Parameter.VAR_KEYWORD:
                value = tuple(sorted(value.items()))
            parts.append((name, value))
        key = tuple(parts)
        try:
            hash(key)
        except TypeError as error:
            raise TypeError("Мемоизация требует хешируемых аргументов") from error
        if key not in cache:
            cache[key] = function(*args, **kwargs)
        return cache[key]

    wrapper.cache_clear = cache.clear
    wrapper.cache_size = lambda: len(cache)
    return wrapper


def repeat(times):
    """Повышенное №6: декоратор с параметром количества вызовов.

    Возвращает список всех результатов. При исключении прекращает повторы
    и передаёт ошибку вызывающему коду.
    """
    require_integer(times)
    if times < 1:
        raise ValueError("Количество повторов должно быть положительным")

    def decorate(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            return [function(*args, **kwargs) for _ in range(times)]
        return wrapper
    return decorate
