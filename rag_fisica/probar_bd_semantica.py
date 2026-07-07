import json
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


DB_PATH = "bd_semantica_fisica"
REGISTRO_PATH = Path("registro_ejercicios_fisica.json")


embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_collection(
    name="ejercicios_fisica",
    embedding_function=embedding_function
)

with open(REGISTRO_PATH, "r", encoding="utf-8") as f:
    registro = json.load(f)


pregunta = input("Pregunta de prueba: ")

resultados = collection.query(
    query_texts=[pregunta],
    n_results=3
)

for pos, ejercicio_id in enumerate(resultados["ids"][0], start=1):
    distancia = resultados["distances"][0][pos - 1]
    item = registro[ejercicio_id]

    print("\n" + "=" * 80)
    print(f"Resultado {pos}")
    print(f"ID: {ejercicio_id}")
    print(f"Distancia semántica: {distancia:.4f}")
    print(f"Tema: {item['tema']}")
    print(f"Dificultad: {item['dificultad']}")
    print(f"Fórmulas: {item['formulas']}")
    print("\nPregunta recuperada:")
    print(item["pregunta"][:800])
    print("\nInicio de solución:")
    print(item["respuesta"][:800])
