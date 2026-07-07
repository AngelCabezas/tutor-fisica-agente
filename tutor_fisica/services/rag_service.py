from __future__ import annotations

import json
import re

import chromadb
import streamlit as st
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from tutor_fisica.config import (
    COLLECTION_EJERCICIOS,
    COLLECTION_TEORIA,
    RAG_DB_PATH,
    RAG_REGISTRO_PATH,
    TEORIA_MAX_DISTANCIA_GENERAL,
    TEORIA_MAX_DISTANCIA_PREFERIDA,
)


@st.cache_resource(show_spinner=False)
def cargar_rag():
    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    client_chroma = chromadb.PersistentClient(path=str(RAG_DB_PATH))

    collection_ejercicios = client_chroma.get_collection(
        name=COLLECTION_EJERCICIOS,
        embedding_function=embedding_function,
    )

    collection_teoria = client_chroma.get_collection(
        name=COLLECTION_TEORIA,
        embedding_function=embedding_function,
    )

    if not RAG_REGISTRO_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el registro de ejercicios: {RAG_REGISTRO_PATH}"
        )

    with RAG_REGISTRO_PATH.open("r", encoding="utf-8") as f:
        registro_ejercicios = json.load(f)

    return collection_ejercicios, registro_ejercicios, collection_teoria


def es_pregunta_de_calculo_rag(pregunta: str) -> bool:
    texto = pregunta.lower()

    tiene_numeros = bool(re.search(r"\d", texto))

    palabras_calculo = [
        "calcula", "determina", "halla", "encuentra",
        "cuál es", "cuanto", "cuánto",
        "aceleración", "velocidad", "fuerza", "energía",
        "trabajo", "distancia", "altura", "tiempo",
        "cantidad de movimiento", "momento", "rapidez",
    ]

    return tiene_numeros or any(p in texto for p in palabras_calculo)


def es_opcion_multiple_rag(pregunta: str) -> bool:
    texto = pregunta.lower()

    return (
        "opción" in texto
        or "opciones" in texto
        or "a." in texto
        or "b." in texto
        or "c." in texto
        or "d." in texto
        or "e." in texto
    )


def construir_consulta_teoria(pregunta: str, resumen_ejercicios: list[str]):
    texto = pregunta.lower()
    resumen = " ".join(resumen_ejercicios).lower()

    sin_friccion = (
        "sin fricción" in texto
        or "sin friccion" in texto
        or "sin rozamiento" in texto
        or "no existe rozamiento" in texto
        or "no hay rozamiento" in texto
        or "no existe fricción" in texto
        or "no hay fricción" in texto
    )

    hay_friccion_real = (
        (
            "fricción" in texto
            or "friccion" in texto
            or "rozamiento" in texto
            or "coeficiente" in texto
        )
        and not sin_friccion
    )

    if (
        "rueda" in texto
        or "rotación" in texto
        or "rotacion" in texto
        or "rotacional" in texto
        or "torque" in texto
        or "momento de inercia" in texto
        or "velocidad angular" in texto
        or "aceleración angular" in texto
        or "aceleracion angular" in texto
        or "omega" in texto
        or "rad/s" in texto
        or "rad/s²" in texto
        or "rad/s^2" in texto
        or "angular" in texto
    ):
        return (
            "movimiento rotacional, velocidad angular, aceleración angular, "
            "cinemática rotacional, rueda que parte del reposo, movimiento angular",
            ["08_movimiento_rotacional"],
        )

    if (
        "proyectil" in texto
        or "proyectiles" in texto
        or "lanzamiento horizontal" in texto
        or "lanza horizontalmente" in texto
        or "se lanza horizontalmente" in texto
        or "velocidad horizontal" in texto
        or "tiro parabólico" in texto
        or "tiro parabolico" in texto
    ):
        return (
            "movimiento de proyectiles, lanzamiento horizontal, movimiento vertical independiente, "
            "movimiento horizontal uniforme, caída vertical con gravedad, trayectoria parabólica",
            ["10_movimiento_proyectiles"],
        )

    if (
        "cae" in texto
        or "caen" in texto
        or "caída" in texto
        or "caida" in texto
        or "se deja caer" in texto
        or "vacío" in texto
        or "vacio" in texto
        or "gravedad" in texto
        or "peso" in texto
    ):
        return (
            "caída libre, gravedad, aceleración gravitatoria, objeto que parte del reposo, "
            "movimiento vertical con aceleración constante, peso y masa",
            ["03_movimiento_lineal", "09_GRAVEDAD", "09_gravedad", "04_segunda_ley_newton"],
        )

    if sin_friccion:
        return (
            "Segunda Ley de Newton, fuerza neta, masa, aceleración, superficie sin fricción, "
            "ausencia de rozamiento, dinámica traslacional",
            ["04_segunda_ley_newton"],
        )

    if hay_friccion_real:
        return (
            "fuerza de fricción, rozamiento, fuerza normal, coeficiente de fricción, "
            "segunda ley de Newton, fuerza neta y aceleración",
            ["04_segunda_ley_newton"],
        )

    if (
        "cantidad de movimiento" in texto
        or "momento lineal" in texto
        or "impulso" in texto
        or "choque" in texto
        or "colisión" in texto
        or "colision" in texto
        or (
            "p = mv" in resumen
            and "angular" not in texto
            and "momento de inercia" not in texto
        )
    ):
        return (
            "cantidad de movimiento, momento lineal, masa, velocidad, impulso, "
            "conservación del momento lineal",
            ["06_cantidad_movimiento"],
        )

    if (
        "w = fd" in resumen
        or "trabajo" in texto
        or "ángulo" in texto
        or "angulo" in texto
        or "desplaza una caja" in texto
        or ("desplazamiento" in texto and "fuerza" in texto)
    ):
        return (
            "trabajo mecánico, fuerza, desplazamiento, ángulo entre fuerza y desplazamiento, "
            "energía transferida por una fuerza",
            ["07_energia"],
        )

    if (
        "energía cinética" in texto
        or "energia cinetica" in texto
        or "energía potencial" in texto
        or "energia potencial" in texto
        or "energía" in texto
        or "energia" in texto
        or "k = 1/2 mv^2" in resumen
        or "u = mgh" in resumen
    ):
        return (
            "energía cinética, energía potencial, masa, rapidez, energía asociada al movimiento, "
            "energía gravitatoria, conservación de la energía",
            ["07_energia"],
        )

    if (
        "equilibrio" in texto
        or "velocidad constante" in texto
        or "reposo" in texto
        or "inercia" in texto
        or "primera ley" in texto
        or "fuerza neta cero" in texto
    ):
        return (
            "Primera Ley de Newton, inercia, equilibrio, reposo, velocidad constante, fuerza neta cero",
            ["02_primera_ley_newton"],
        )

    if (
        "acción" in texto
        or "accion" in texto
        or "reacción" in texto
        or "reaccion" in texto
        or "tercera ley" in texto
        or "pares de fuerzas" in texto
        or "empujar una pared" in texto
        or "pared ejerce" in texto
    ):
        return (
            "Tercera Ley de Newton, acción y reacción, pares de fuerzas, interacción entre cuerpos",
            ["05_tercera_ley_newton"],
        )

    if (
        "f = ma" in resumen
        or "fuerza" in texto
        or "aceleración" in texto
        or "aceleracion" in texto
        or "masa" in texto
    ):
        return (
            "Segunda Ley de Newton, fuerza neta, masa, aceleración, "
            "relación entre fuerza y aceleración, dinámica traslacional",
            ["04_segunda_ley_newton"],
        )

    if (
        "velocidad" in texto
        or "distancia" in texto
        or "desplazamiento" in texto
        or "tiempo" in texto
        or "mru" in texto
        or "mruv" in texto
    ):
        return (
            "movimiento lineal, velocidad, aceleración, desplazamiento, tiempo, cinemática",
            ["03_movimiento_lineal"],
        )

    return pregunta, []


def capitulo_coincide(capitulo: str, capitulos_preferidos: list[str]) -> bool:
    if not capitulos_preferidos:
        return True

    capitulo = str(capitulo).lower()

    return any(preferido.lower() in capitulo for preferido in capitulos_preferidos)


def buscar_contexto_ejercicios_rag(
    pregunta: str,
    collection,
    registro: dict,
    n_resultados: int = 3,
):
    resultados = collection.query(
        query_texts=[pregunta],
        n_results=n_resultados,
    )

    contexto = []
    resumen = []

    ids = resultados.get("ids", [[]])[0]
    distances = resultados.get("distances", [[]])[0]

    for pos, ejercicio_id in enumerate(ids, start=1):
        distancia = distances[pos - 1]
        item = registro.get(ejercicio_id, {})

        tema = item.get("tema", "No especificado")
        dificultad = item.get("dificultad", "No especificada")
        formulas = item.get("formulas", "No detectadas")
        pregunta_recuperada = item.get("pregunta", "")
        respuesta_recuperada = item.get("respuesta", "")

        resumen.append(
            f"{pos}. {ejercicio_id} | distancia={distancia:.4f} | "
            f"tema={tema} | dificultad={dificultad} | fórmulas={formulas}"
        )

        bloque = f"""
Ejercicio similar {pos}
ID: {ejercicio_id}
Distancia semántica: {distancia:.4f}
Tema: {tema}
Dificultad: {dificultad}
Fórmulas detectadas: {formulas}

Enunciado similar:
{pregunta_recuperada}

Solución similar recortada:
{respuesta_recuperada[:500]}

Uso permitido:
Este ejercicio recuperado solo sirve como guía metodológica. No se deben copiar sus datos numéricos, redacción ni estructura de solución.
""".strip()

        contexto.append(bloque)

    separador = "\n\n" + "=" * 80 + "\n\n"

    return separador.join(contexto), resumen


def buscar_contexto_teoria_rag(
    pregunta: str,
    collection_teoria,
    n_resultados: int = 2,
    capitulos_preferidos: list[str] | None = None,
):
    capitulos_preferidos = capitulos_preferidos or []

    n_fetch = max(n_resultados * 6, n_resultados)

    resultados = collection_teoria.query(
        query_texts=[pregunta],
        n_results=n_fetch,
    )

    ids = resultados.get("ids", [[]])[0]
    documents = resultados.get("documents", [[]])[0]
    distances = resultados.get("distances", [[]])[0]
    metadatas = resultados.get("metadatas", [[]])[0]

    candidatos = []

    for pos, teoria_id in enumerate(ids):
        distancia = distances[pos]
        documento = documents[pos]
        metadata = metadatas[pos] if metadatas and metadatas[pos] else {}

        fuente = metadata.get("fuente", metadata.get("source", "No especificada"))
        capitulo = metadata.get("capitulo", metadata.get("chapter", "No especificado"))

        if capitulos_preferidos:
            if not capitulo_coincide(capitulo, capitulos_preferidos):
                continue

            if distancia > TEORIA_MAX_DISTANCIA_PREFERIDA:
                continue

        else:
            if distancia > TEORIA_MAX_DISTANCIA_GENERAL:
                continue

        candidatos.append({
            "id": teoria_id,
            "distancia": distancia,
            "documento": documento,
            "fuente": fuente,
            "capitulo": capitulo,
        })

        if len(candidatos) >= n_resultados:
            break

    contexto = []
    resumen = []

    for pos, item in enumerate(candidatos, start=1):
        resumen.append(
            f"{pos}. {item['id']} | distancia={item['distancia']:.4f} | "
            f"fuente={item['fuente']} | capítulo={item['capitulo']}"
        )

        bloque = f"""
Fragmento teórico {pos}
ID: {item["id"]}
Distancia semántica: {item["distancia"]:.4f}
Fuente: {item["fuente"]}
Capítulo: {item["capitulo"]}

Contenido teórico relevante:
{item["documento"][:800]}

Uso permitido:
Este fragmento solo sirve para reforzar la explicación conceptual. No debe introducir datos nuevos al problema.
""".strip()

        contexto.append(bloque)

    separador = "\n\n" + "-" * 80 + "\n\n"

    return separador.join(contexto), resumen


def construir_contexto_rag(
    pregunta: str,
    collection_ejercicios,
    registro_ejercicios: dict,
    collection_teoria,
):
    if es_pregunta_de_calculo_rag(pregunta) or es_opcion_multiple_rag(pregunta):
        n_ejercicios = 3
        n_teoria = 2
    else:
        n_ejercicios = 1
        n_teoria = 3

    contexto_ejercicios, resumen_ejercicios = buscar_contexto_ejercicios_rag(
        pregunta=pregunta,
        collection=collection_ejercicios,
        registro=registro_ejercicios,
        n_resultados=n_ejercicios,
    )

    consulta_teoria, capitulos_preferidos = construir_consulta_teoria(
        pregunta=pregunta,
        resumen_ejercicios=resumen_ejercicios,
    )

    contexto_teoria, resumen_teoria = buscar_contexto_teoria_rag(
        pregunta=consulta_teoria,
        collection_teoria=collection_teoria,
        n_resultados=n_teoria,
        capitulos_preferidos=capitulos_preferidos,
    )

    contexto_total = f"""
Contexto de ejercicios similares recuperados para apoyo metodológico:
{contexto_ejercicios}

Contexto teórico recuperado para apoyo conceptual:
{contexto_teoria}
""".strip()

    resumen = {
        "ejercicios": resumen_ejercicios,
        "consulta_teoria": consulta_teoria,
        "capitulos_preferidos": capitulos_preferidos,
        "teoria": resumen_teoria,
    }

    return contexto_total, resumen