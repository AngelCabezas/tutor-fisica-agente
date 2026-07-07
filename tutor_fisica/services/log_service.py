from __future__ import annotations

import json
from datetime import datetime

from tutor_fisica.config import LOG_DIR, LOG_FILE


def guardar_log(pregunta: str, respuesta: str, backend: str, modelo: str):
    registro = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "backend": backend,
        "modelo": modelo,
        "pregunta": pregunta,
        "respuesta": respuesta,
    }

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")
