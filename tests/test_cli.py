"""Проверки консольного интерфейса."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

MAIN = Path(__file__).resolve().parents[1] / "main.py"


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-X", "utf8", str(MAIN), *args],
            cwd=tempfile.gettempdir(), capture_output=True,
            text=True, encoding="utf-8", timeout=10,
        )

    def test_demo_outside_project(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("реальных вычислений: 1", result.stdout)
        self.assertIn("repeat(3)", result.stdout)
        self.assertIn("Вызов factorial", result.stderr)

    def test_commands(self):
        self.assertEqual(self.run_cli("factorial", "5").stdout.strip(), "120")
        self.assertEqual(self.run_cli("even", "-2", "1", "4").stdout.strip(),
                         "[-2, 4]")
        self.assertEqual(self.run_cli("even").stdout.strip(), "[]")

    def test_invalid_cli(self):
        for args in [("factorial", "-1"), ("factorial", "2.5"),
                     ("factorial",), ("even", "abc")]:
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)
