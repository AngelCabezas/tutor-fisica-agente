import json
import re
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from openai import OpenAI


# ============================
# RUTAS Y CONFIGURACIÓN
# ============================

DB_PATH = "bd_semantica_fisica"

COLLECTION_EJERCICIOS = "ejercicios_fisica"
COLLECTION_TEORIA = "teoria_fisica"

REGISTRO_PATH = Path("registro_ejercicios_fisica.json")

LLM_BASE_URL = "http://127.0.0.1:8080/v1"
LLM_API_KEY = "local"
LLM_MODEL = "tutor-fisica-local"

SKILL_PATHS = [
    Path.home() / "tutor_fisica_agente" / "skills" / "tutor-fisica-epn" / "SKILL.md",
]

# Distancias máximas para aceptar teoría.
# Si hay capítulo preferido, permitimos una distancia un poco mayor.
TEORIA_MAX_DISTANCIA_PREFERIDA = 0.45
TEORIA_MAX_DISTANCIA_GENERAL = 0.32


# ============================
# CARGA DE SKILL
# ============================

def cargar_skill():
    for path in SKILL_PATHS:
        if path.exists():
            print(f"Skill cargada desde: {path}")
            return path.read_text(encoding="utf-8")

    raise FileNotFoundError(
        "No se encontró la skill de Física. Revisa la ruta de tu archivo SKILL.md."
    )


# ============================
# CARGA DE BASES SEMÁNTICAS
# ============================

def cargar_bases():
    print("Cargando modelo de embeddings...")

    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    print("Conectando a la base de datos ChromaDB...")
    client_chroma = chromadb.PersistentClient(path=DB_PATH)

    print("Cargando colección de ejercicios...")
    collection_ejercicios = client_chroma.get_collection(
        name=COLLECTION_EJERCICIOS,
        embedding_function=embedding_function
    )

    if not REGISTRO_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró {REGISTRO_PATH}. Primero ejecuta crear_bd_semantica.py"
        )

    with open(REGISTRO_PATH, "r", encoding="utf-8") as f:
        registro_ejercicios = json.load(f)

    print("Base de ejercicios cargada correctamente.")
    print("Cargando colección de teoría...")

    try:
        collection_teoria = client_chroma.get_collection(
            name=COLLECTION_TEORIA,
            embedding_function=embedding_function
        )
        print("Base teórica cargada correctamente.\n")

    except Exception as e:
        collection_teoria = None
        print("No se pudo cargar la base teórica.")
        print(f"Detalle: {e}")
        print("El tutor seguirá funcionando solo con ejercicios.\n")

    return collection_ejercicios, registro_ejercicios, collection_teoria


# ============================
# CLASIFICACIÓN SIMPLE DE PREGUNTAS
# ============================

def es_pregunta_de_calculo(pregunta):
    texto = pregunta.lower()

    tiene_numeros = bool(re.search(r"\d", texto))

    palabras_calculo = [
        "calcula",
        "determine",
        "determina",
        "halla",
        "encuentra",
        "cuál es",
        "cuanto",
        "cuánto",
        "aceleración",
        "velocidad",
        "fuerza",
        "energía",
        "trabajo",
        "distancia",
        "altura",
        "tiempo",
        "cantidad de movimiento",
        "momento",
        "rapidez",
    ]

    return tiene_numeros or any(palabra in texto for palabra in palabras_calculo)


def es_opcion_multiple(pregunta):
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


# ============================
# CONSULTA TEÓRICA ENRIQUECIDA
# ============================

def construir_consulta_teoria(pregunta, resumen_ejercicios):
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
        ("fricción" in texto or "friccion" in texto or "rozamiento" in texto or "coeficiente" in texto)
        and not sin_friccion
    )

    # 1. Caída libre, gravedad y vacío
    if (
        "cae" in texto
        or "caen" in texto
        or "caída" in texto
        or "caida" in texto
        or "vacío" in texto
        or "vacio" in texto
        or "gravedad" in texto
        or "peso" in texto
    ):
        return (
            "caída libre en el vacío, gravedad, peso, masa, inercia, "
            "aceleración gravitatoria, relación entre peso y masa, segunda ley de Newton",
            ["04_segunda_ley_newton", "09_GRAVEDAD", "09_gravedad"]
        )

    # 2. Problemas sin fricción: son de Segunda Ley de Newton, no de fricción
    if sin_friccion:
        return (
            "Segunda Ley de Newton, fuerza neta, masa, aceleración, superficie sin fricción, "
            "ausencia de rozamiento, dinámica traslacional",
            ["04_segunda_ley_newton"]
        )

    # 3. Fricción / rozamiento real
    if hay_friccion_real:
        return (
            "fuerza de fricción, rozamiento, fuerza normal, coeficiente de fricción, "
            "segunda ley de Newton, fuerza neta y aceleración",
            ["04_segunda_ley_newton"]
        )

    # 4. Trabajo mecánico
    if "w = fd" in resumen or "trabajo" in texto or "ángulo" in texto or "angulo" in texto:
        return (
            "trabajo mecánico, fuerza, desplazamiento, ángulo entre fuerza y desplazamiento, "
            "energía transferida por una fuerza",
            ["07_energia"]
        )

    # 5. Energía cinética / potencial / conservación
    if (
        "k = 1/2 mv^2" in resumen
        or "energía cinética" in texto
        or "energia cinetica" in texto
        or "energía potencial" in texto
        or "energia potencial" in texto
        or "energía" in texto
        or "energia" in texto
        or "rapidez" in texto
    ):
        return (
            "energía cinética, energía potencial, masa, rapidez, energía asociada al movimiento, "
            "energía gravitatoria, conservación de la energía",
            ["07_energia"]
        )

    # 6. Cantidad de movimiento / impulso
    if (
        "p = mv" in resumen
        or "cantidad de movimiento" in texto
        or "momento lineal" in texto
        or "impulso" in texto
        or "choque" in texto
        or "colisión" in texto
        or "colision" in texto
    ):
        return (
            "cantidad de movimiento, momento lineal, masa, velocidad, impulso, conservación del momento",
            ["06_cantidad_movimiento"]
        )

    # 7. Movimiento rotacional
    if (
        "rotación" in texto
        or "rotacion" in texto
        or "rotacional" in texto
        or "torque" in texto
        or "momento de inercia" in texto
        or "angular" in texto
    ):
        return (
            "movimiento rotacional, torque, momento de inercia, aceleración angular, dinámica rotacional",
            ["08_movimiento_rotacional"]
        )

    # 8. Movimiento de proyectiles
    if (
        "proyectil" in texto
        or "proyectiles" in texto
        or "lanzamiento" in texto
        or "tiro parabólico" in texto
        or "tiro parabolico" in texto
    ):
        return (
            "movimiento de proyectiles, movimiento horizontal y vertical, gravedad, trayectoria parabólica",
            ["10_movimiento_proyectiles"]
        )

    # 9. Primera Ley de Newton / equilibrio
    if (
        "equilibrio" in texto
        or "velocidad constante" in texto
        or "reposo" in texto
        or "inercia" in texto
        or "primera ley" in texto
    ):
        return (
            "Primera Ley de Newton, inercia, equilibrio, reposo, velocidad constante, fuerza neta cero",
            ["02_primera_ley_newton"]
        )

    # 10. Tercera Ley de Newton
    if (
        "acción" in texto
        or "accion" in texto
        or "reacción" in texto
        or "reaccion" in texto
        or "tercera ley" in texto
        or "pares de fuerzas" in texto
    ):
        return (
            "Tercera Ley de Newton, acción y reacción, pares de fuerzas, interacción entre cuerpos",
            ["05_tercera_ley_newton"]
        )

    # 11. Segunda Ley de Newton general
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
            ["04_segunda_ley_newton"]
        )

    # 12. Cinemática lineal
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
            ["03_movimiento_lineal"]
        )

    return pregunta, []


def capitulo_coincide(capitulo, capitulos_preferidos):
    if not capitulos_preferidos:
        return True

    capitulo = str(capitulo).lower()

    return any(preferido.lower() in capitulo for preferido in capitulos_preferidos)


# ============================
# BÚSQUEDA EN EJERCICIOS
# ============================

def buscar_contexto_ejercicios(pregunta, collection, registro, n_resultados=3):
    resultados = collection.query(
        query_texts=[pregunta],
        n_results=n_resultados
    )

    contexto = []
    resumen_recuperacion = []

    ids = resultados.get("ids", [[]])[0]
    distances = resultados.get("distances", [[]])[0]

    for pos, ejercicio_id in enumerate(ids, start=1):
        distancia = distances[pos - 1]
        item = registro[ejercicio_id]

        resumen_recuperacion.append(
            f"{pos}. {ejercicio_id} | distancia={distancia:.4f} | "
            f"tema={item['tema']} | dificultad={item['dificultad']} | "
            f"fórmulas={item['formulas']}"
        )

        bloque = f"""
Ejercicio similar {pos}
ID: {ejercicio_id}
Distancia semántica: {distancia:.4f}
Tema: {item["tema"]}
Dificultad: {item["dificultad"]}
Fórmulas detectadas: {item["formulas"]}

Enunciado similar:
{item["pregunta"]}

Solución similar recortada:
{item["respuesta"][:1000]}

Uso permitido:
Este ejercicio recuperado solo sirve como guía metodológica. No se deben copiar sus datos numéricos.
""".strip()

        contexto.append(bloque)

    separador = "\n\n" + "=" * 80 + "\n\n"
    contexto_final = separador.join(contexto)

    return contexto_final, resumen_recuperacion


# ============================
# BÚSQUEDA EN TEORÍA
# ============================

def buscar_contexto_teoria(
    pregunta,
    collection_teoria,
    n_resultados=2,
    capitulos_preferidos=None
):
    if collection_teoria is None:
        return "", []

    capitulos_preferidos = capitulos_preferidos or []

    # Pedimos más fragmentos de los necesarios para poder filtrar por capítulo.
    n_fetch = max(n_resultados * 6, n_resultados)

    resultados = collection_teoria.query(
        query_texts=[pregunta],
        n_results=n_fetch
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
    resumen_teoria = []

    for pos, item in enumerate(candidatos, start=1):
        resumen_teoria.append(
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
{item["documento"][:1200]}

Uso permitido:
Este fragmento solo sirve para reforzar la explicación conceptual. No debe introducir datos nuevos al problema.
""".strip()

        contexto.append(bloque)

    separador = "\n\n" + "-" * 80 + "\n\n"
    contexto_final = separador.join(contexto)

    return contexto_final, resumen_teoria


# ============================
# GENERACIÓN DE RESPUESTA
# ============================

def generar_respuesta(
    pregunta,
    collection_ejercicios,
    registro_ejercicios,
    collection_teoria,
    skill_pedagogica,
    client_llm
):
    if es_pregunta_de_calculo(pregunta) or es_opcion_multiple(pregunta):
        n_ejercicios = 3
        n_teoria = 2
    else:
        n_ejercicios = 1
        n_teoria = 3

    contexto_ejercicios, resumen_ejercicios = buscar_contexto_ejercicios(
        pregunta=pregunta,
        collection=collection_ejercicios,
        registro=registro_ejercicios,
        n_resultados=n_ejercicios
    )

    consulta_teoria, capitulos_preferidos = construir_consulta_teoria(
        pregunta=pregunta,
        resumen_ejercicios=resumen_ejercicios
    )

    contexto_teoria, resumen_teoria = buscar_contexto_teoria(
        pregunta=consulta_teoria,
        collection_teoria=collection_teoria,
        n_resultados=n_teoria,
        capitulos_preferidos=capitulos_preferidos
    )

    print("Ejercicios recuperados:")
    for item in resumen_ejercicios:
        print(item)

    print()

    print(f"Consulta teórica usada: {consulta_teoria}")
    if capitulos_preferidos:
        print(f"Capítulos preferidos: {', '.join(capitulos_preferidos)}")
    else:
        print("Capítulos preferidos: ninguno")

    print()

    if resumen_teoria:
        print("Fragmentos teóricos recuperados:")
        for item in resumen_teoria:
            print(item)
        print()
    else:
        print("No se recuperaron fragmentos teóricos suficientemente relacionados.\n")

    prompt_usuario = f"""
Pregunta del estudiante (ESTOS SON LOS ÚNICOS DATOS REALES):
{pregunta}

Contexto de ejercicios similares recuperados para apoyo metodológico:
{contexto_ejercicios}

Contexto teórico recuperado para apoyo conceptual:
{contexto_teoria}

INSTRUCCIONES DE CONTROL DE DATOS (MÁXIMA PRIORIDAD):
1. Resuelve ÚNICAMENTE el problema planteado en "Pregunta del estudiante".
2. Está TERMINANTEMENTE PROHIBIDO usar los números, masas, alturas, velocidades o datos del contexto de ejercicios como si fueran datos del problema actual.
3. Los ejercicios recuperados sirven solo para identificar el método de resolución y fórmulas relacionadas.
4. La teoría recuperada sirve solo para reforzar la explicación conceptual.
5. Si el problema del estudiante dice que la rapidez es 3 m/s, NO inventes caídas libres, alturas, tiempos ni datos que no estén en la pregunta.
6. Tu solución debe basarse única y exclusivamente en los datos numéricos proporcionados por el estudiante.
7. Si la teoría recuperada no es necesaria para resolver el ejercicio, úsala solo de forma breve.
8. Si algún fragmento recuperado no pertenece al tema del problema, ignóralo.
9. Respeta la skill pedagógica cargada en el mensaje de sistema.
""".strip()

    respuesta = client_llm.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": skill_pedagogica},
            {"role": "user", "content": prompt_usuario}
        ],
        temperature=0.05,
        max_tokens=3000
    )

    return respuesta.choices[0].message.content


# ============================
# PROGRAMA PRINCIPAL
# ============================

def main():
    skill_pedagogica = cargar_skill()

    collection_ejercicios, registro_ejercicios, collection_teoria = cargar_bases()

    client_llm = OpenAI(
        base_url=LLM_BASE_URL,
        api_key=LLM_API_KEY
    )

    print("Tutor RAG de Física con ejercicios + teoría")
    print("Escribe 'salir' para terminar.\n")

    while True:
        pregunta = input("Pregunta: ").strip()

        if pregunta.lower() in ["salir", "exit", "quit"]:
            break

        if not pregunta:
            continue

        print("\nBuscando ejercicios similares, teoría relevante y generando respuesta...\n")

        try:
            respuesta = generar_respuesta(
                pregunta=pregunta,
                collection_ejercicios=collection_ejercicios,
                registro_ejercicios=registro_ejercicios,
                collection_teoria=collection_teoria,
                skill_pedagogica=skill_pedagogica,
                client_llm=client_llm
            )

            print(respuesta)
            print("\n" + "=" * 100 + "\n")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()