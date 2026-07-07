from __future__ import annotations

from pathlib import Path


def cargar_skill(skill_path: Path) -> str:
    if not skill_path.exists():
        raise FileNotFoundError(f"No se encontró la skill en: {skill_path}")
    return skill_path.read_text(encoding="utf-8")
