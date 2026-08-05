from __future__ import annotations

import unittest

from agent.runner import format_result


class RunnerTests(unittest.TestCase):
    def test_returns_text(self) -> None:
        self.assertIsInstance(format_result("answer"), str)


if __name__ == "__main__":
    unittest.main()
