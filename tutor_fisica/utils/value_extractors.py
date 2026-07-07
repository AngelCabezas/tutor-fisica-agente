from __future__ import annotations

import re


def extraer_valores_en_newton(pregunta: str) -> list[float]:
    valores = re.findall(r"(\d+(?:[.,]\d+)?)\s*N", pregunta, flags=re.IGNORECASE)
    return [float(v.replace(",", ".")) for v in valores]


def extraer_angulo_grados(pregunta: str, valor_default: float = 30.0) -> float:
    patron = r"(\d+(?:[.,]\d+)?)\s*(?:°|grados|grado)"
    match = re.search(patron, pregunta, flags=re.IGNORECASE)

    if match:
        return float(match.group(1).replace(",", "."))

    return valor_default


def extraer_rapidez(pregunta: str, valor_default: float = 20.0) -> float:
    patrones = [
        r"rapidez\s+inicial\s+de\s+(\d+(?:[.,]\d+)?)\s*m/s",
        r"velocidad\s+inicial\s+de\s+(\d+(?:[.,]\d+)?)\s*m/s",
        r"v0\s*=?\s*(\d+(?:[.,]\d+)?)\s*m/s",
        r"(\d+(?:[.,]\d+)?)\s*m/s",
    ]

    for patron in patrones:
        match = re.search(patron, pregunta, flags=re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", "."))

    return valor_default


def extraer_masa(pregunta: str, nombre: str, valor_default: float) -> float:
    texto = pregunta

    # Limpieza básica para leer formatos LaTeX como m_1 = 3 \text{kg}
    texto = texto.replace("\\text{kg}", "kg")
    texto = texto.replace("\\mathrm{kg}", "kg")
    texto = texto.replace("{", "")
    texto = texto.replace("}", "")
    texto = texto.replace("\\", "")

    variantes = [nombre]

    if nombre == "m1":
        variantes.extend(["m_1", "m 1", "masa 1", "bloque 1"])
    elif nombre == "m2":
        variantes.extend(["m_2", "m 2", "masa 2", "bloque 2"])

    for variante in variantes:
        patron = rf"{re.escape(variante)}\s*=?\s*(\d+(?:[.,]\d+)?)\s*kg"
        match = re.search(patron, texto, flags=re.IGNORECASE)

        if match:
            return float(match.group(1).replace(",", "."))

    return valor_default


def extraer_primer_numero_con_unidad(pregunta: str, unidad: str, valor_default: float) -> float:
    patron = rf"(\d+(?:[.,]\d+)?)\s*{unidad}"
    match = re.search(patron, pregunta, flags=re.IGNORECASE)

    if match:
        return float(match.group(1).replace(",", "."))

    return valor_default


def extraer_fuerza_aplicada(pregunta: str, valor_default: float = 50.0) -> float:
    patrones = [
        r"fuerza\s+(?:horizontal\s+)?(?:constante\s+)?de\s+(\d+(?:[.,]\d+)?)\s*N",
        r"se\s+aplica\s+una\s+fuerza\s+de\s+(\d+(?:[.,]\d+)?)\s*N",
        r"fuerza\s+aplicada\s*=?\s*(\d+(?:[.,]\d+)?)\s*N",
        r"F\s*=?\s*(\d+(?:[.,]\d+)?)\s*N",
    ]

    for patron in patrones:
        match = re.search(patron, pregunta, flags=re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", "."))

    valores_n = extraer_valores_en_newton(pregunta)
    if valores_n:
        return valores_n[0]

    return valor_default


def extraer_coeficiente_friccion(pregunta: str, valor_default: float = 0.30) -> float:
    patrones = [
        r"(?:μk|μ_k|mu_k)\s*=?\s*(\d+(?:[.,]\d+)?)",
        r"coeficiente\s+de\s+fricci[oó]n\s+cin[eé]tica\s+(?:es|=|de)?\s*(\d+(?:[.,]\d+)?)",
        r"coeficiente\s+de\s+rozamiento\s+cin[eé]tico\s+(?:es|=|de)?\s*(\d+(?:[.,]\d+)?)",
        r"coeficiente\s+de\s+fricci[oó]n\s+(?:es|=|de)?\s*(\d+(?:[.,]\d+)?)",
        r"coeficiente\s+de\s+rozamiento\s+(?:es|=|de)?\s*(\d+(?:[.,]\d+)?)",
    ]

    for patron in patrones:
        match = re.search(patron, pregunta, flags=re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", "."))

    return valor_default


def extraer_gravedad(pregunta: str, valor_default: float = 9.8) -> float:
    patrones = [
        r"g\s*=\s*(\d+(?:[.,]\d+)?)\s*m/s",
        r"gravedad\s+(?:es|=|de)?\s*(\d+(?:[.,]\d+)?)\s*m/s",
        r"usa\s+g\s*=\s*(\d+(?:[.,]\d+)?)",
    ]

    for patron in patrones:
        match = re.search(patron, pregunta, flags=re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", "."))

    return valor_default


def extraer_peso_newton(pregunta: str, valor_default: float = 30.0) -> float:
    patrones = [
        r"peso\s+de\s+(\d+(?:[.,]\d+)?)\s*N",
        r"peso\s+.*?(\d+(?:[.,]\d+)?)\s*N",
        r"W\s*=?\s*(\d+(?:[.,]\d+)?)\s*N",
    ]

    for patron in patrones:
        match = re.search(patron, pregunta, flags=re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", "."))

    valores = extraer_valores_en_newton(pregunta)
    if valores:
        return valores[0]

    return valor_default


def extraer_friccion_estatica_maxima(pregunta: str, valor_default: float = 15.0) -> float:
    patrones = [
        r"fricci[oó]n\s+est[aá]tica\s+m[aá]xima\s+.*?(\d+(?:[.,]\d+)?)\s*N",
        r"fuerza\s+m[aá]xima\s+de\s+fricci[oó]n\s+est[aá]tica\s+.*?(\d+(?:[.,]\d+)?)\s*N",
        r"f_s\s*,?\s*m[aá]x\s*=?\s*(\d+(?:[.,]\d+)?)\s*N",
        r"fs\s*,?\s*max\s*=?\s*(\d+(?:[.,]\d+)?)\s*N",
    ]

    for patron in patrones:
        match = re.search(patron, pregunta, flags=re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", "."))

    valores = extraer_valores_en_newton(pregunta)

    if len(valores) >= 2:
        return valores[1]

    return valor_default