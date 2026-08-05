from __future__ import annotations

import json
from pathlib import Path


def append_memory(path: Path, user_text: str, assistant_text: str) -> None:
    items = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    items.append({"user": user_text, "assistant": assistant_text})
    path.write_text(json.dumps(items), encoding="utf-8")
