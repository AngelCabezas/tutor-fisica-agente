from __future__ import annotations

from tutor_fisica.utils.text_formatting import normalizar_texto


def detectar_tipo_diagrama(pregunta: str) -> str | None:
    texto = normalizar_texto(pregunta)

    if any(p in texto for p in ["dos masas cuelgan", "extremos de una cuerda", "maquina de atwood", "máquina de atwood"]):
        return "atwood"

    if any(p in texto for p in ["polea", "cuerda", "bloque colgante", "cuelga libremente", "colgante"]):
        return "polea"

    if any(p in texto for p in ["plano inclinado", "rampa", "inclinado", "inclinacion"]):
        return "plano_inclinado"

    if any(p in texto for p in ["proyectil", "tiro parabolico", "movimiento parabolico", "alcance horizontal", "altura maxima"]):
        return "tiro_parabolico"

    if any(p in texto for p in ["campo magnetico", "electron", "trayectoria circular", "radio de su trayectoria"]):
        return "campo_magnetico"

    if any(p in texto for p in ["flota", "flotando", "empuje", "arquimedes", "sumergido", "agua dulce", "agua salada", "mercurio"]):
        return "flotacion"

    if any(p in texto for p in ["presion hidrostatica", "profundidad", "recipiente", "batiscafo", "submarino"]):
        return "hidrostatica"

    if any(p in texto for p in ["grafica velocidad-tiempo", "velocidad-tiempo", "mrua", "acelera uniformemente"]):
        return "mrua"

    if any(p in texto for p in ["vector", "vectores", "resultante", "componentes", "angulos rectos", "perpendiculares"]):
        return "vectores"

    sin_friccion = any(
        frase in texto
        for frase in [
            "sin friccion",
            "sin rozamiento",
            "no hay friccion",
            "no presenta friccion",
            "superficie lisa",
        ]
    )

    hay_friccion = any(
        palabra in texto
        for palabra in [
            "coeficiente de friccion",
            "coeficiente de rozamiento",
            "μk",
            "mu_k",
            "friccion cinetica",
            "rozamiento cinetico",
            "superficie rugosa",
            "rugosa",
        ]
    )

    friccion_estatica_coeficiente = any(
        frase in texto
        for frase in [
            "coeficiente de friccion estatica",
            "coeficiente de rozamiento estatico",
            "friccion estatica maxima",
            "fuerza maxima de friccion estatica",
            "comienza a deslizarse",
        ]
    )

    if friccion_estatica_coeficiente:
        return "friccion_estatica_coeficiente"

    if hay_friccion and not sin_friccion:
        return "friccion"

    bloque_horizontal = "bloque" in texto and any(
        p in texto
        for p in ["mesa horizontal", "superficie horizontal", "fuerza constante", "fuerza aplicada"]
    )

    if bloque_horizontal and sin_friccion:
        return "bloque_simple"

    return None
