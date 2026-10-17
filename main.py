"""Запуск пяти заданий лабораторной №4."""

import argparse
import logging

from lab4.decorators import log_calls, memoize, repeat
from lab4.functions import even_numbers, factorial


def demo():
    print(f"Чётные числа: {even_numbers(range(-3, 7))}")
    print(f"5! = {factorial(5)}; 0! = {factorial(0)}")
    logged_factorial = log_calls(factorial)
    print(f"Факториал с логированием: {logged_factorial(4)}")
    evaluations = 0

    @memoize
    def square(number):
        nonlocal evaluations
        evaluations += 1
        return number ** 2

    print(f"Мемоизация: {square(7)}, {square(number=7)}; "
          f"реальных вычислений: {evaluations}")

    @repeat(times=3)
    def greet(name):
        return f"Привет, {name}!"

    print(f"Декоратор repeat(3): {greet('Илья')}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command")
    fact = commands.add_parser("factorial", help="Факториал через reduce")
    fact.add_argument("n", type=int)
    even = commands.add_parser("even", help="Фильтрация чётных чисел")
    even.add_argument("numbers", nargs="*", type=int)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        if args.command == "factorial":
            print(factorial(args.n))
        elif args.command == "even":
            print(even_numbers(args.numbers))
        else:
            demo()
    except (ValueError, TypeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
