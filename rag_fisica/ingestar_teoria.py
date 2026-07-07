import json
import re
from pathlib import Path
import fitz  # PyMuPDF
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# --- RUTAS ---
RAG_DIR = Path.home() / "tutor_fisica_agente" / "rag_fisica"
PDF_DIR = RAG_DIR / "libro_hewitt"  # <- Cambia esto si tu carpeta se llama distinto
DB_PATH = str(RAG_DIR / "bd_semantica_fisica")
REGISTRO_TEORIA_PATH = RAG_DIR / "registro_teoria_fisica.json"

def limpiar_texto(texto: str) -> str:
    """Elimina saltos de línea y espacios dobles."""
    texto = texto.replace('\n', ' ')
    return re.sub(r'\s+', ' ', texto).strip()

def fragmentar_texto(texto: str, max_chars: int = 1200, overlap: int = 200) -> list:
    """Divide el texto continuo en fragmentos solapados (Sliding Window)."""
    fragmentos = []
    inicio = 0
    while inicio < len(texto):
        fin = inicio + max_chars
        fragmento = texto[inicio:fin]
        # Buscar el último punto para no cortar la oración a la mitad si es posible
        if fin < len(texto):
            ultimo_punto = fragmento.rfind('.')
            if ultimo_punto > max_chars // 2:
                fin = inicio + ultimo_punto + 1
                fragmento = texto[inicio:fin]
        
        fragmentos.append(fragmento)
        inicio = fin - overlap
    return fragmentos

def main():
    if not PDF_DIR.exists():
        raise FileNotFoundError(f"No se encontró la carpeta de PDFs: {PDF_DIR}")

    print("Cargando modelo de Embeddings...")
    embedding_func = SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    client = chromadb.PersistentClient(path=DB_PATH)

    # Creamos una colección NUEVA dedicada solo a la teoría
    try:
        client.delete_collection("teoria_fisica")
        print("Colección de teoría anterior eliminada para limpieza.")
    except Exception:
        pass

    coleccion_teoria = client.get_or_create_collection(
        name="teoria_fisica",
        embedding_function=embedding_func,
        metadata={"hnsw:space": "cosine"}
    )

    ids = []
    documents = []
    metadatas = []
    registro = {}
    contador_fragmentos = 0

    print("Procesando capítulos PDF...")
    # Ordenar los archivos para que se procesen alfabéticamente
    archivos_pdf = sorted(PDF_DIR.glob("*.pdf"))

    for archivo in archivos_pdf:
        nombre_capitulo = archivo.stem # Extrae "01_Acerca_de_la_ciencia"
        print(f"-> Leyendo: {nombre_capitulo}")
        
        doc = fitz.open(archivo)
        texto_completo = ""
        
        for pagina in doc:
            texto_completo += pagina.get_text()
            
        texto_limpio = limpiar_texto(texto_completo)
        fragmentos = fragmentar_texto(texto_limpio)
        
        for i, fragmento in enumerate(fragmentos):
            if len(fragmento) < 50: # Ignorar fragmentos muy pequeños o vacíos
                continue
                
            frag_id = f"hewitt_{nombre_capitulo}_{i}"
            
            ids.append(frag_id)
            documents.append(fragmento)
            metadatas.append({
                "fuente": "Física Conceptual - Hewitt",
                "capitulo": nombre_capitulo
            })
            
            registro[frag_id] = {
                "capitulo": nombre_capitulo,
                "texto": fragmento
            }
            contador_fragmentos += 1

    print(f"\nVectorizando e inyectando {contador_fragmentos} fragmentos en ChromaDB...")
    
    # Subir en lotes para no saturar la memoria
    batch_size = 100
    for start in range(0, len(ids), batch_size):
        end = start + batch_size
        coleccion_teoria.add(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end]
        )
        print(f"Inyectados {min(end, len(ids))}/{len(ids)} fragmentos")

    with open(REGISTRO_TEORIA_PATH, "w", encoding="utf-8") as f:
        json.dump(registro, f, ensure_ascii=False, indent=2)

    print("\n✅ Base de datos teórica construida exitosamente.")

if __name__ == "__main__":
    main()
