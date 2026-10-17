"""Фильтрация и факториал в функциональном стиле."""

from functools import reduce
from operator import mul


def require_integer(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("Ожидается целое число")
    return value


def even_numbers(values):
    """Среднее №2: вернуть чётные числа, не изменяя исходные данные."""
    return list(filter(lambda n: require_integer(n) % 2 == 0, values))


def factorial(n):
    """Среднее №4: факториал через reduce; 0! = 1."""
    require_integer(n)
    if n < 0:
        raise ValueError("Факториал определён для n >= 0")
    return reduce(mul, range(1, n + 1), 1)
