from __future__ import annotations

from pathlib import Path


def load_context(notes_dir: Path) -> str:
    return "\n\n".join(path.read_text(encoding="utf-8") for path in notes_dir.rglob("*.md"))
