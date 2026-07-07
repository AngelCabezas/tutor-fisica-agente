import json
import re
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


DATASET_PATH = Path("dataset_fisica_total.jsonl")
DB_PATH = "bd_semantica_fisica"
REGISTRO_PATH = Path("registro_ejercicios_fisica.json")


def detectar_tema(texto: str) -> str:
    t = texto.lower()

    if any(p in t for p in ["newton", "fuerza", "masa", "aceleración", "fricción", "rozamiento", "normal"]):
        return "Dinámica"
    if any(p in t for p in ["velocidad", "posición", "desplazamiento", "tiempo", "mrU".lower(), "mruv", "caída libre"]):
        return "Cinemática"
    if any(p in t for p in ["trabajo", "energía", "cinética", "potencial", "conservación de la energía"]):
        return "Trabajo y energía"
    if any(p in t for p in ["momento", "cantidad de movimiento", "impulso", "choque", "colisión"]):
        return "Cantidad de movimiento"
    if any(p in t for p in ["torque", "rotación", "momento de inercia", "angular"]):
        return "Rotación"
    if any(p in t for p in ["carga", "campo eléctrico", "potencial eléctrico", "corriente", "voltaje", "resistencia"]):
        return "Electricidad"
    if any(p in t for p in ["onda", "frecuencia", "longitud de onda", "sonido"]):
        return "Ondas"
    if any(p in t for p in ["temperatura", "calor", "termodinámica", "gas ideal"]):
        return "Termodinámica"

    return "General"


def detectar_dificultad(texto: str) -> str:
    t = texto.lower()

    formulas = len(re.findall(r"[$=]", texto))
    tiene_literal = bool(re.search(r"\b[a-e]\)", t))
    longitud = len(t)

    if longitud > 2500 or formulas >= 8:
        return "avanzada"
    if longitud > 1200 or formulas >= 4 or tiene_literal:
        return "media"
    return "básica"


def detectar_formulas(texto: str) -> str:
    t = texto.lower()
    formulas = []

    if "f = ma" in t or "f=ma" in t or "segunda ley" in t:
        formulas.append("F = ma")
    if "v = v_0" in t or "v=v_0" in t or "v = vo" in t:
        formulas.append("v = v0 + at")
    if "x = x_0" in t or "1/2" in t or "at^2" in t:
        formulas.append("x = x0 + v0t + 1/2 at^2")
    if "k = " in t or "energía cinética" in t or "cinética" in t:
        formulas.append("K = 1/2 mv^2")
    if "u = mgh" in t or "energía potencial" in t or "potencial gravitatoria" in t:
        formulas.append("U = mgh")
    if "w = f" in t or "trabajo" in t:
        formulas.append("W = Fd cos(theta)")
    if "p = mv" in t or "cantidad de movimiento" in t:
        formulas.append("p = mv")
    if "f_k" in t or "fricción cinética" in t or "rozamiento cinético" in t:
        formulas.append("f_k = mu_k N")

    return ", ".join(formulas) if formulas else "No detectada"


def extraer_messages(item):
    messages = item.get("messages", [])

    system = ""
    user = ""
    assistant = ""

    for m in messages:
        role = m.get("role", "")
        content = m.get("content", "")

        if role == "system":
            system = content
        elif role == "user":
            user = content
        elif role == "assistant":
            assistant = content

    return system, user, assistant


def main():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"No se encontró {DATASET_PATH}")

    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    client = chromadb.PersistentClient(path=DB_PATH)

    try:
        client.delete_collection("ejercicios_fisica")
        print("Colección anterior eliminada.")
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name="ejercicios_fisica",
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"}
    )

    ids = []
    documents = []
    metadatas = []
    registro = {}

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            item = json.loads(line)
            system, pregunta, respuesta = extraer_messages(item)

            if not pregunta or not respuesta:
                continue

            texto_completo = f"{pregunta}\n\n{respuesta}"
            tema = detectar_tema(texto_completo)
            dificultad = detectar_dificultad(texto_completo)
            formulas = detectar_formulas(texto_completo)

            ejercicio_id = f"fisica_{i}"

            texto_para_embedding = f"""
Tema: {tema}
Dificultad: {dificultad}
Fórmulas: {formulas}

Enunciado:
{pregunta}
""".strip()

            ids.append(ejercicio_id)
            documents.append(texto_para_embedding)
            metadatas.append({
                "indice": i,
                "tema": tema,
                "dificultad": dificultad,
                "formulas": formulas
            })

            registro[ejercicio_id] = {
                "system": system,
                "pregunta": pregunta,
                "respuesta": respuesta,
                "tema": tema,
                "dificultad": dificultad,
                "formulas": formulas
            }

    batch_size = 100

    for start in range(0, len(ids), batch_size):
        end = start + batch_size
        collection.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end]
        )
        print(f"Agregados {min(end, len(ids))}/{len(ids)} ejercicios")

    with open(REGISTRO_PATH, "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)

    print("\nBase semántica creada correctamente.")
    print(f"Total de ejercicios: {len(ids)}")
    print(f"Carpeta ChromaDB: {DB_PATH}")
    print(f"Registro completo: {REGISTRO_PATH}")


if __name__ == "__main__":
    main()
