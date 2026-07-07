from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any


SYSTEM_PROMPT = (
    "Eres un tutor experto en física. "
    "Resuelves problemas paso a paso, proporcionando soluciones detalladas "
    "y explicaciones claras."
)


PATRON_EJERCICIO = re.compile(
    r"\\subsection\*\{Enunciado ?\}(.*?)"
    r"\\subsection\*\{Soluci[oó]n\}(.*?)"
    r"(?=\\newpage|\\subsection\*\{Enunciado ?\}|\\end\{document\}|$)",
    flags=re.DOTALL | re.IGNORECASE,
)


def limpiar_latex(texto: str) -> str:
    """
    Limpia comandos decorativos de LaTeX y conserva el contenido textual y
    matemático necesario para construir ejemplos de entrenamiento.

    Args:
        texto: Fragmento de texto en formato LaTeX.

    Returns:
        Texto limpio y normalizado.
    """

    # Eliminar bloques TikZ completos.
    texto = re.sub(
        r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
        "",
        texto,
        flags=re.DOTALL,
    )

    # Convertir bloques lstlisting a formato markdown.
    texto = re.sub(
        r"\\begin\{lstlisting\}(.*?)\\end\{lstlisting\}",
        r"```python\n\1\n```",
        texto,
        flags=re.DOTALL,
    )

    # Eliminar entornos visuales, conservando el contenido interno.
    texto = re.sub(r"\\begin\{center\}", "", texto)
    texto = re.sub(r"\\end\{center\}", "", texto)
    texto = re.sub(r"\\begin\{tcolorbox\}(?:\[[^\]]*\])?", "", texto)
    texto = re.sub(r"\\end\{tcolorbox\}", "", texto)

    # Eliminar comandos de estructura que no aportan al entrenamiento.
    texto = re.sub(r"\\subsubsection\*\{[^}]*\}", "", texto)
    texto = re.sub(r"\\subsection\*\{[^}]*\}", "", texto)

    # Eliminar comandos visuales innecesarios.
    texto = texto.replace(r"\centering", "")
    texto = texto.replace(r"\newpage", "")

    # Convertir unidades \si{...} a una notación matemática más general.
    texto = re.sub(r"\\si\{([^}]*)\}", r"\\mathrm{\1}", texto)

    # Normalizar espacios y saltos de línea.
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n[ \t]+", "\n", texto)
    texto = re.sub(r"\n\s*\n\s*\n+", "\n\n", texto)

    return texto.strip()


def crear_registro(
    enunciado: str,
    solucion: str,
    system_prompt: str = SYSTEM_PROMPT,
) -> dict[str, list[dict[str, str]]]:
    """
    Crea un registro en formato conversacional compatible con fine-tuning
    de modelos instructivos.

    Args:
        enunciado: Enunciado del problema.
        solucion: Solución explicada del problema.
        system_prompt: Instrucción del sistema para el modelo.

    Returns:
        Registro con mensajes de tipo system, user y assistant.
    """

    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": enunciado},
            {"role": "assistant", "content": solucion},
        ]
    }


def extraer_registros(
    contenido_latex: str,
    system_prompt: str = SYSTEM_PROMPT,
) -> list[dict[str, Any]]:
    """
    Extrae pares Enunciado/Solución desde un documento LaTeX.

    Args:
        contenido_latex: Contenido completo del archivo .tex.
        system_prompt: Instrucción del sistema para cada registro.

    Returns:
        Lista de registros en formato JSONL conversacional.
    """

    registros = []

    for enunciado, solucion in PATRON_EJERCICIO.findall(contenido_latex):
        enunciado_limpio = limpiar_latex(enunciado)
        solucion_limpia = limpiar_latex(solucion)

        if not enunciado_limpio or not solucion_limpia:
            continue

        registro = crear_registro(
            enunciado=enunciado_limpio,
            solucion=solucion_limpia,
            system_prompt=system_prompt,
        )

        registros.append(registro)

    return registros


def procesar_archivo(
    archivo_entrada: Path,
    archivo_salida: Path,
    system_prompt: str = SYSTEM_PROMPT,
) -> int:
    """
    Procesa un archivo LaTeX y genera un archivo JSONL.

    Args:
        archivo_entrada: Ruta del archivo .tex.
        archivo_salida: Ruta del archivo .jsonl generado.
        system_prompt: Instrucción del sistema para cada registro.

    Returns:
        Número de registros generados.
    """

    contenido = archivo_entrada.read_text(encoding="utf-8")
    registros = extraer_registros(contenido, system_prompt)

    with archivo_salida.open("w", encoding="utf-8") as salida:
        for registro in registros:
            linea_json = json.dumps(registro, ensure_ascii=False)
            salida.write(linea_json + "\n")

    return len(registros)


def procesar_carpeta(
    carpeta_entrada: Path,
    archivo_salida: Path,
    system_prompt: str = SYSTEM_PROMPT,
) -> tuple[int, int]:
    """
    Procesa todos los archivos .tex encontrados en una carpeta y sus subcarpetas.

    Args:
        carpeta_entrada: Carpeta donde se buscarán los archivos .tex.
        archivo_salida: Archivo JSONL final.
        system_prompt: Instrucción del sistema para cada registro.

    Returns:
        Una tupla con:
        - número de archivos procesados correctamente;
        - número total de registros generados.
    """

    if not carpeta_entrada.exists():
        raise FileNotFoundError(f"La carpeta no existe: {carpeta_entrada}")

    archivos_tex = sorted(carpeta_entrada.rglob("*.tex"))

    archivos_procesados = 0
    total_registros = 0

    with archivo_salida.open("w", encoding="utf-8") as salida:
        for archivo_tex in archivos_tex:
            try:
                contenido = archivo_tex.read_text(encoding="utf-8")
                registros = extraer_registros(contenido, system_prompt)

                for registro in registros:
                    linea_json = json.dumps(registro, ensure_ascii=False)
                    salida.write(linea_json + "\n")

                archivos_procesados += 1
                total_registros += len(registros)

                logging.info(
                    "[OK] %s: %d ejercicios procesados",
                    archivo_tex,
                    len(registros),
                )

            except Exception as error:
                logging.error(
                    "[ERROR] No se pudo procesar %s: %s",
                    archivo_tex,
                    error,
                )

    return archivos_procesados, total_registros


def configurar_argumentos() -> argparse.Namespace:
    """
    Define los argumentos de ejecución del script.

    Returns:
        Argumentos ingresados por consola.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Convierte ejercicios en formato LaTeX a un dataset JSONL "
            "con estructura conversacional para fine-tuning."
        )
    )

    parser.add_argument(
        "--entrada",
        type=Path,
        default=Path("."),
        help="Archivo .tex o carpeta que contiene archivos .tex.",
    )

    parser.add_argument(
        "--salida",
        type=Path,
        default=Path("dataset_fisica_total.jsonl"),
        help="Ruta del archivo JSONL de salida.",
    )

    return parser.parse_args()


def main() -> None:
    """
    Punto de entrada principal del script.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    args = configurar_argumentos()

    if args.entrada.is_file():
        total = procesar_archivo(args.entrada, args.salida)

        logging.info("Archivo procesado: %s", args.entrada)
        logging.info("Total de ejercicios procesados: %d", total)
        logging.info("Dataset generado: %s", args.salida)

    else:
        archivos_procesados, total_registros = procesar_carpeta(
            carpeta_entrada=args.entrada,
            archivo_salida=args.salida,
        )

        logging.info("Archivos procesados: %d", archivos_procesados)
        logging.info("Total de ejercicios procesados: %d", total_registros)
        logging.info("Dataset generado: %s", args.salida)


if __name__ == "__main__":
    main()