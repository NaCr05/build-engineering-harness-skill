from __future__ import annotations


def format_result(answer: str, error: Exception | None = None) -> str:
    if error is not None:
        return f"Agent failed: {error}"
    return answer
