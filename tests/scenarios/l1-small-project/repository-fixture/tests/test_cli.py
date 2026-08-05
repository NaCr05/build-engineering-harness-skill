from __future__ import annotations

import unittest

from cli import greet


class GreetTests(unittest.TestCase):
    def test_greets_a_name(self) -> None:
        self.assertEqual("Hello, Ada!", greet("Ada"))


if __name__ == "__main__":
    unittest.main()
