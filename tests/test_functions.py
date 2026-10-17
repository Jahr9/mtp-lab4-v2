"""Эталонные значения и наблюдаемое поведение декораторов."""

import math
import unittest

from lab4.decorators import log_calls, memoize, repeat
from lab4.functions import even_numbers, factorial


class FunctionTests(unittest.TestCase):
    def test_even_numbers(self):
        values = [-3, -2, 0, 1, 2, 2, 5]
        self.assertEqual(even_numbers(values), [-2, 0, 2, 2])
        self.assertEqual(values, [-3, -2, 0, 1, 2, 2, 5])
        self.assertEqual(even_numbers(iter(range(5))), [0, 2, 4])
        self.assertEqual(even_numbers([]), [])

    def test_even_rejects_invalid_items(self):
        for item in (True, 2.5, "2", None):
            with self.subTest(item=item), self.assertRaises(TypeError):
                even_numbers([item])

    def test_factorial_against_reference(self):
        for n in range(101):
            with self.subTest(n=n):
                self.assertEqual(factorial(n), math.factorial(n))

    def test_invalid_factorial(self):
        with self.assertRaises(ValueError):
            factorial(-1)
        for value in (True, 2.5, "3", None):
            with self.subTest(value=value), self.assertRaises(TypeError):
                factorial(value)

    def test_log_success(self):
        decorated = log_calls(factorial)
        with self.assertLogs("lab4.decorators", level="INFO") as log:
            self.assertEqual(decorated(n=4), 24)
        self.assertIn("Вызов factorial", log.output[0])
        self.assertIn("24", log.output[1])
        self.assertEqual(decorated.__name__, factorial.__name__)
        self.assertEqual(decorated.__doc__, factorial.__doc__)

    def test_log_error_is_propagated(self):
        with self.assertLogs("lab4.decorators", level="INFO") as log:
            with self.assertRaises(ValueError):
                log_calls(factorial)(-1)
        self.assertIn("ERROR", log.output[-1])

    def test_memoize_equivalent_calls_and_clear(self):
        calls = []

        @memoize
        def add(a, b=2):
            calls.append((a, b))
            return a + b

        self.assertEqual(add(3), 5)
        self.assertEqual(add(a=3, b=2), 5)
        self.assertEqual(add(3, 2), 5)
        self.assertEqual(calls, [(3, 2)])
        self.assertEqual(add.cache_size(), 1)
        add.cache_clear()
        self.assertEqual(add.cache_size(), 0)
        add(3)
        self.assertEqual(len(calls), 2)
        self.assertEqual(add.__name__, "add")

    def test_memoize_variable_arguments(self):
        calls = []

        @memoize
        def collect(*args, **kwargs):
            calls.append(1)
            return sum(args) + sum(kwargs.values())

        self.assertEqual(collect(1, b=2, c=3), 6)
        self.assertEqual(collect(1, c=3, b=2), 6)
        self.assertEqual(len(calls), 1)

    def test_memoize_recursive_function(self):
        calls = []

        @memoize
        def fib(n):
            calls.append(n)
            return n if n < 2 else fib(n - 1) + fib(n - 2)

        self.assertEqual(fib(10), 55)
        self.assertEqual(len(calls), 11)
        fib(10)
        self.assertEqual(len(calls), 11)

    def test_memoize_errors_are_not_cached(self):
        calls = []

        @memoize
        def fail(n):
            calls.append(n)
            raise ValueError("test")

        for _ in range(2):
            with self.assertRaises(ValueError):
                fail(1)
        self.assertEqual(len(calls), 2)
        self.assertEqual(fail.cache_size(), 0)

    def test_memoize_unhashable_and_invalid_call(self):
        cached = memoize(lambda x: x)
        with self.assertRaises(TypeError):
            cached([])
        with self.assertRaises(TypeError):
            cached()

    def test_memoize_none(self):
        calls = []

        @memoize
        def nothing(n):
            calls.append(n)

        self.assertIsNone(nothing(1))
        self.assertIsNone(nothing(1))
        self.assertEqual(calls, [1])

    def test_repeat_calls_and_metadata(self):
        calls = []

        @repeat(times=3)
        def append(value):
            """Append and return current length."""
            calls.append(value)
            return len(calls)

        self.assertEqual(append(value="x"), [1, 2, 3])
        self.assertEqual(calls, ["x"] * 3)
        self.assertEqual(append.__name__, "append")
        self.assertEqual(append.__doc__, "Append and return current length.")

    def test_repeat_validation(self):
        for value in (0, -1):
            with self.assertRaises(ValueError):
                repeat(value)
        for value in (True, 1.5, "2"):
            with self.assertRaises(TypeError):
                repeat(value)
        self.assertEqual(repeat(1)(lambda: 5)(), [5])

    def test_repeat_stops_on_error(self):
        calls = []

        @repeat(3)
        def fail():
            calls.append(1)
            raise RuntimeError("test")

        with self.assertRaises(RuntimeError):
            fail()
        self.assertEqual(calls, [1])
