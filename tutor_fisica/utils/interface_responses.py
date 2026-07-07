from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


RESPUESTAS_PATH = Path(__file__).resolve().parents[2] / "data" / "respuestas_interfaz.json"
PATRONES_FISICA_PATH = Path(__file__).resolve().parents[2] / "data" / "patrones_fisica.json"


@dataclass(frozen=True)
class RespuestaInterfaz:
    encontrada: bool
    categoria: str = ""
    respuesta: str = ""


def normalizar_texto_interfaz(texto: str) -> str:
    texto = texto.lower().strip()

    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
        "¿": "",
        "?": "",
        "¡": "",
        "!": "",
        ",": " ",
        ".": " ",
        ":": " ",
        ";": " ",
    }

    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)

    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def cargar_respuestas_interfaz() -> dict:
    if not RESPUESTAS_PATH.exists():
        return {}

    with RESPUESTAS_PATH.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def cargar_patrones_fisica() -> list[str]:
    if not PATRONES_FISICA_PATH.exists():
        return []

    with PATRONES_FISICA_PATH.open("r", encoding="utf-8") as archivo:
        data = json.load(archivo)

    return data.get("palabras_fisica", [])


def contiene_tema_fisica(texto: str) -> bool:
    palabras_fisica = cargar_patrones_fisica()
    palabras_fisica = [normalizar_texto_interfaz(palabra) for palabra in palabras_fisica]

    return any(palabra in texto for palabra in palabras_fisica)


def coincide_patron(texto: str, patron: str, categoria: str) -> bool:
    patron = normalizar_texto_interfaz(patron)

    if not patron:
        return False

    if categoria in {"saludo", "agradecimiento"}:
        return texto == patron

    if categoria in {"identidad", "creador_sistema", "ayuda"}:
        return patron in texto

    if categoria == "fuera_dominio":
        return patron in texto

    return patron in texto


def buscar_respuesta_interfaz(pregunta: str) -> RespuestaInterfaz:
    texto = normalizar_texto_interfaz(pregunta)

    if not texto:
        return RespuestaInterfaz(
            encontrada=True,
            categoria="entrada_vacia",
            respuesta="Escribe un ejercicio o una pregunta de Física para poder ayudarte."
        )

    respuestas = cargar_respuestas_interfaz()

    # Primero se revisan saludos, identidad, creador, ayuda y agradecimientos.
    # No se revisa fuera_dominio todavía.
    for categoria, contenido in respuestas.items():
        if categoria == "fuera_dominio":
            continue

        patrones = contenido.get("patrones", [])
        respuesta = contenido.get("respuesta", "")

        for patron in patrones:
            if coincide_patron(texto, patron, categoria):
                return RespuestaInterfaz(
                    encontrada=True,
                    categoria=categoria,
                    respuesta=respuesta,
                )

    # Luego se revisa fuera de dominio.
    # Si la pregunta contiene tema de Física, no se bloquea aunque tenga palabras como "angular".
    if contiene_tema_fisica(texto):
        return RespuestaInterfaz(encontrada=False)

    contenido_fuera = respuestas.get("fuera_dominio", {})
    patrones_fuera = contenido_fuera.get("patrones", [])
    respuesta_fuera = contenido_fuera.get("respuesta", "")

    for patron in patrones_fuera:
        if coincide_patron(texto, patron, "fuera_dominio"):
            return RespuestaInterfaz(
                encontrada=True,
                categoria="fuera_dominio",
                respuesta=respuesta_fuera,
            )

    return RespuestaInterfaz(encontrada=False)
