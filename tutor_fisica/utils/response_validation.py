from __future__ import annotations

import re


def respuesta_mala(texto: str, pregunta: str) -> bool:
    texto_lower = texto.lower()
    pregunta_lower = pregunta.lower()

    senales_malas = [
        "```",
        "python",
        "matplotlib",
        "import ",
        "plt.",
        "fig, ax",
        "<grafico_python>",
        "</grafico_python>",
        "estudiante:",
        "tutor:",
        "\\subsection",
        "\\subsubsection",
        "\\begin{lstlisting}",
        "\\end{lstlisting}",
        "\\begin{itemize}",
        "\\end{itemize}",
        "\\item",
        "\\textbf",
        "\\begin{enumerate}",
        "\\end{enumerate}",
        "specified by the user",
        "final_conclusion",
    ]

    primera_linea = texto.strip().splitlines()[0].lower() if texto.strip() else ""

    if not re.match(r"^1\.\s*principio f[ií]sico", primera_linea):
        return True

    if any(s in texto_lower for s in senales_malas):
        return True

    if "f4" not in pregunta_lower and "dirección de f4" in texto_lower:
        return True

    if "9.8" in pregunta_lower and re.search(r"g\s*=\s*10", texto_lower):
        return True

    if "0.20" in pregunta_lower:
        if "μ = 0.3" in texto_lower or "\\mu = 0.3" in texto_lower or "0.30" in texto_lower:
            return True

    return False
