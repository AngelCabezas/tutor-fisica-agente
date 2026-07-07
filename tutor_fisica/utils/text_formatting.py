from __future__ import annotations

import re


def limpiar_latex_malformado(texto: str) -> str:
    texto = texto.strip()

    # Elimina líneas que tengan solo un signo $
    texto = re.sub(r"(?m)^\s*\$\s*$", "", texto)

    # Protege los bloques $$...$$ temporalmente
    texto_temp = texto.replace("$$", "__DOBLE_DOLLAR__")

    # Si queda un número impar de $ simples, los elimina
    if texto_temp.count("$") % 2 != 0:
        texto_temp = re.sub(r"(?<!\$)\$(?!\$)", "", texto_temp)

    # Restaura los $$ originales
    texto = texto_temp.replace("__DOBLE_DOLLAR__", "$$")

    # Si por alguna razón queda un número impar de $$, los elimina
    if texto.count("$$") % 2 != 0:
        texto = texto.replace("$$", "")

    # Limpia espacios y saltos excesivos
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()


def corregir_formato_salida(texto: str) -> str:
    texto = texto.strip()

    match = re.search(r"1\.\s*Principio\s+f[ií]sico", texto, flags=re.IGNORECASE)
    if match:
        texto = texto[match.start():].strip()

    texto = re.sub(r"\\textbf\{([^{}]+)\}", r"**\1**", texto)

    texto = re.sub(r"\\begin\{itemize\}", "\n", texto)
    texto = re.sub(r"\\end\{itemize\}", "\n", texto)
    texto = re.sub(r"\\begin\{enumerate\}", "\n", texto)
    texto = re.sub(r"\\end\{enumerate\}", "\n", texto)
    texto = re.sub(r"\\item\s*", "\n* ", texto)

    texto = re.sub(
        r"<GRAFICO_PYTHON>\s*.*?\s*</GRAFICO_PYTHON>",
        "",
        texto,
        flags=re.DOTALL | re.IGNORECASE,
    )

    texto = texto.replace("P0P0", "P0")
    texto = texto.replace("ρρ", "ρ")
    texto = texto.replace("gg", "g")
    texto = texto.replace("hh", "h")

    texto = re.sub(r"(\d+(?:\.\d+)?),\\text\{", r"\1\\,\\text{", texto)

    texto = texto.replace("dirección de F4", "dirección de la fuerza aplicada")
    texto = texto.replace("direccion de F4", "dirección de la fuerza aplicada")

    texto = texto.replace(" ", " ")
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    texto = limpiar_latex_malformado(texto)

    return texto.strip()



def es_respuesta_conceptual_forzada(texto: str) -> bool:
    texto_norm = normalizar_texto(texto)

    indicadores = [
        "no se requiere ecuacion",
        "no se requiere sustitucion",
        "no se requiere desarrollo matematico",
        "no se requiere calculo",
        "no se requieren datos numericos",
        "no se requieren datos",
        "no requiere ecuacion",
        "no requiere sustitucion",
        "no requiere desarrollo matematico",
    ]

    cantidad = sum(1 for indicador in indicadores if indicador in texto_norm)

    tiene_formato_resolucion = bool(
        re.search(r"1\.\s*Principio\s+f[ií]sico", texto, flags=re.IGNORECASE)
    )

    return tiene_formato_resolucion and cantidad >= 2


def extraer_secciones_respuesta(texto: str) -> dict[str, str]:
    titulos = {
        "1": "Principio físico",
        "2": "Datos del problema",
        "3": "Incógnitas",
        "4": "Ecuaciones",
        "5": "Sustitución con unidades",
        "6": "Desarrollo matemático",
        "7": "Respuestas finales",
        "8": "Interpretación física breve",
    }

    patron = re.compile(
        r"(?m)^\s*(?:#+\s*)?([1-8])\.\s*"
        r"(Principio\s+f[ií]sico|Datos\s+del\s+problema|Inc[oó]gnitas|"
        r"Ecuaciones|Sustituci[oó]n\s+con\s+unidades|Desarrollo\s+matem[aá]tico|"
        r"Respuestas\s+finales|Interpretaci[oó]n\s+f[ií]sica\s+breve)\s*$",
        flags=re.IGNORECASE,
    )

    coincidencias = list(patron.finditer(texto))
    secciones = {}

    for idx, match in enumerate(coincidencias):
        numero = match.group(1)
        inicio = match.end()
        fin = coincidencias[idx + 1].start() if idx + 1 < len(coincidencias) else len(texto)

        contenido = texto[inicio:fin].strip()
        secciones[numero] = contenido

    return secciones


def limpiar_lineas_no_requeridas(texto: str) -> str:
    lineas_limpias = []

    patrones_excluir = [
        "no se requiere",
        "no requiere",
        "no se necesitan datos",
        "no se proporcionan datos",
    ]

    for linea in texto.splitlines():
        linea_norm = normalizar_texto(linea)

        if any(patron in linea_norm for patron in patrones_excluir):
            continue

        lineas_limpias.append(linea)

    limpio = "\n".join(lineas_limpias)
    limpio = re.sub(r"\n{3,}", "\n\n", limpio)

    return limpio.strip()


def limpiar_respuesta_conceptual_forzada(texto: str) -> str:
    if not es_respuesta_conceptual_forzada(texto):
        return texto

    secciones = extraer_secciones_respuesta(texto)

    principio = limpiar_lineas_no_requeridas(secciones.get("1", ""))
    respuesta = limpiar_lineas_no_requeridas(secciones.get("7", ""))
    interpretacion = limpiar_lineas_no_requeridas(secciones.get("8", ""))

    explicacion_partes = []

    if principio:
        explicacion_partes.append(principio)

    if interpretacion:
        explicacion_partes.append(interpretacion)

    partes = []

    if explicacion_partes:
        explicacion = "\n\n".join(explicacion_partes).strip()
        partes.append(f"### Explicación conceptual\n\n{explicacion}")

    if respuesta:
        partes.append(f"### Respuesta\n\n{respuesta}")

    if not partes:
        return texto

    return "\n\n".join(partes).strip()


def formatear_respuesta_markdown(texto: str) -> str:
    texto = texto.strip()
    texto = limpiar_respuesta_conceptual_forzada(texto)

    secciones = [
        ("1", "Principio físico"),
        ("2", "Datos del problema"),
        ("3", "Incógnitas"),
        ("4", "Ecuaciones"),
        ("5", "Sustitución con unidades"),
        ("6", "Desarrollo matemático"),
        ("7", "Respuestas finales"),
        ("8", "Interpretación física breve"),
    ]

    for numero, titulo in secciones:
        patron = rf"(?:^|\s)(?:#+\s*)?{numero}\.\s*{titulo}\s*"
        reemplazo = f"\n\n### {numero}. {titulo}\n\n"
        texto = re.sub(patron, reemplazo, texto, flags=re.IGNORECASE)

    texto = re.sub(r"\s+\*\s+", "\n\n* ", texto)

    texto = texto.replace(" La ecuación", "\n\nLa ecuación")
    texto = texto.replace(" Sustituimos", "\n\nSustituimos")
    texto = texto.replace(" Despejamos", "\n\nDespejamos")
    texto = texto.replace(" Recordando que", "\n\nRecordando que")
    texto = texto.replace(" Por tanto", "\n\nPor tanto")
    texto = texto.replace(" Entonces", "\n\nEntonces")

    texto = re.sub(r"(?<!\n)\$\$", "\n\n$$", texto)
    texto = re.sub(r"\$\$(?!\n)", "$$\n\n", texto)

    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()


def normalizar_texto(texto: str) -> str:
    return texto.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")