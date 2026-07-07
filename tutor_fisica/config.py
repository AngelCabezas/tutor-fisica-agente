from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_DIR = Path.home() / "tutor_fisica_agente"

DEFAULT_SKILL_PATH = PROJECT_DIR / "skills" / "tutor-fisica-epn" / "SKILL.md"

RAG_DIR = PROJECT_DIR / "rag_fisica"
RAG_DB_PATH = RAG_DIR / "bd_semantica_fisica"
RAG_REGISTRO_PATH = RAG_DIR / "registro_ejercicios_fisica.json"

COLLECTION_EJERCICIOS = "ejercicios_fisica"
COLLECTION_TEORIA = "teoria_fisica"

TEORIA_MAX_DISTANCIA_PREFERIDA = 0.45
TEORIA_MAX_DISTANCIA_GENERAL = 0.32

LOG_DIR = PROJECT_DIR / "data"
LOG_FILE = LOG_DIR / "historial_interfaz_streamlit.jsonl"


@dataclass(frozen=True)
class AppSettings:
    backend: str
    endpoint: str
    model_name: str
    skill_path: Path
    temperature: float
    top_p: float
    max_tokens: int
    usar_rag: bool
    mostrar_rag: bool
