import json
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from openai import OpenAI

DB_PATH = "bd_semantica_fisica"
REGISTRO_PATH = Path("registro_ejercicios_fisica.json")

LLM_BASE_URL = "http://127.0.0.1:8080/v1"
LLM_API_KEY = "local"
LLM_MODEL = "tutor-fisica-local"

SKILL_PATHS = [
    Path.home() / "tutor_fisica_agente" / "skills" / "tutor-fisica-epn" / "SKILL.md",
]


def cargar_skill():
    for path in SKILL_PATHS:
        if path.exists():
            print(f"Skill cargada desde: {path}")
            return path.read_text(encoding="utf-8")

    raise FileNotFoundError(
        "No se encontró la skill de Física. Revisa la ruta de tu archivo SKILL.md."
    )


def cargar_bd():
    print("Cargando base semántica...")

    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    client_chroma = chromadb.PersistentClient(path=DB_PATH)

    collection = client_chroma.get_collection(
        name="ejercicios_fisica",
        embedding_function=embedding_function
    )

    if not REGISTRO_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró {REGISTRO_PATH}. Primero ejecuta crear_bd_semantica.py"
        )

    with open(REGISTRO_PATH, "r", encoding="utf-8") as f:
        registro = json.load(f)

    print("Base semántica cargada correctamente.\n")
    return collection, registro


def buscar_contexto(pregunta, collection, registro, n_resultados=3):
    resultados = collection.query(
        query_texts=[pregunta],
        n_results=n_resultados
    )

    contexto = []
    resumen_recuperacion = []

    for pos, ejercicio_id in enumerate(resultados["ids"][0], start=1):
        distancia = resultados["distances"][0][pos - 1]
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

Solución similar:
{item["respuesta"][:1800]}
""".strip()

        contexto.append(bloque)

    separador = "\n\n" + "=" * 80 + "\n\n"
    contexto_final = separador.join(contexto)

    return contexto_final, resumen_recuperacion


def generar_respuesta(pregunta, collection, registro, skill_pedagogica, client_llm):
    contexto, resumen_recuperacion = buscar_contexto(
        pregunta=pregunta,
        collection=collection,
        registro=registro,
        n_resultados=3
    )

    print("Ejercicios recuperados:")
    for item in resumen_recuperacion:
        print(item)
    print()

    prompt_usuario = f"""
Pregunta del estudiante (ESTOS SON LOS ÚNICOS DATOS REALES):
{pregunta}

Contexto de ejemplos similares recuperados para apoyo conceptual:
{contexto}

INSTRUCCIONES DE CONTROL DE DATOS (MÁXIMA PRIORIDAD):
1. Resuelve ÚNICAMENTE el problema planteado en "Pregunta del estudiante".
2. Está TERMINANTEMENTE PROHIBIDO usar los números, masas, alturas, velocidades o datos del "Contexto de ejemplos". Esos ejemplos son solo una guía de referencia conceptual.
3. Si el problema del estudiante dice que la rapidez es 3 m/s, NO inventes caídas libres, alturas de 5 m ni uses datos de los ejemplos.
4. Tu solución debe basarse única y exclusivamente en los datos numéricos proporcionados por el estudiante.
""".strip()

    respuesta = client_llm.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": skill_pedagogica},
            {"role": "user", "content": prompt_usuario}
        ],
        temperature=0.15,
        max_tokens=2500
    )

    return respuesta.choices[0].message.content


def main():
    skill_pedagogica = cargar_skill()
    collection, registro = cargar_bd()

    client_llm = OpenAI(
        base_url=LLM_BASE_URL,
        api_key=LLM_API_KEY
    )

    print("Tutor RAG de Física")
    print("Escribe 'salir' para terminar.\n")

    while True:
        pregunta = input("Pregunta: ").strip()

        if pregunta.lower() in ["salir", "exit", "quit"]:
            break

        if not pregunta:
            continue

        print("\nBuscando ejercicios similares y generando respuesta...\n")

        try:
            respuesta = generar_respuesta(
                pregunta=pregunta,
                collection=collection,
                registro=registro,
                skill_pedagogica=skill_pedagogica,
                client_llm=client_llm
            )

            print(respuesta)
            print("\n" + "=" * 100 + "\n")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()