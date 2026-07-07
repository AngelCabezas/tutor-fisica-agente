import requests
import json
from pathlib import Path

URL = "http://localhost:8080/v1/chat/completions"
SKILL_PATH = Path.home() / "tutor_fisica_agente" / "skills" / "skill_phi4_tutor_fisica_epn.md"


def cargar_skill() -> str:
    if not SKILL_PATH.exists():
        raise FileNotFoundError(f"No se encontró la skill: {SKILL_PATH}")
    return SKILL_PATH.read_text(encoding="utf-8")


def construir_system_prompt(skill: str) -> str:
    return f"""
Eres un tutor experto en Física para estudiantes universitarios de primeros niveles.

Debes seguir estrictamente esta skill pedagógica:

{skill}

REGLAS CRÍTICAS:
- Responde siempre en español.
- No menciones la skill.
- No escribas "Estudiante:" ni "Tutor:" dentro de la respuesta.
- No simules una conversación.
- No generes código Python.
- No generes pseudocódigo.
- No generes bloques de código.
- No uses triple comilla invertida.
- No generes gráficos ni diagramas.
- No uses matplotlib.
- No inventes datos.
- No cambies valores dados en el enunciado.
- Si el enunciado dice g = 9.8, debes usar exactamente g = 9.8.
- Si el enunciado dice μk = 0.20, debes usar exactamente μk = 0.20.
- Si el problema tiene literales a), b), c), resuelve todos los literales en una sola respuesta.
- No respondas solo una parte del problema.
- No agregues fuerzas externas que el enunciado no menciona.
- No asumas reposo si el enunciado dice que el bloque se desliza.
- Muestra solo el procedimiento pedagógico necesario.
- Termina con una conclusión clara.

FORMATO OBLIGATORIO PARA EJERCICIOS:
1. Datos del problema.
2. Incógnitas.
3. Principio físico.
4. Ecuaciones.
5. Sustitución con unidades.
6. Desarrollo matemático.
7. Respuestas finales.
8. Interpretación física breve.
""".strip()


def leer_pregunta_multilinea() -> str:
    print("\nPega tu pregunta completa.")
    print("Cuando termines, escribe FIN en una línea nueva.\n")

    lineas = []

    while True:
        linea = input()

        if linea.strip().upper() == "FIN":
            break

        lineas.append(linea)

    return "\n".join(lineas).strip()


def respuesta_mala(texto: str, pregunta: str) -> bool:
    texto_lower = texto.lower()
    pregunta_lower = pregunta.lower()

    señales_malas = [
        "```",
        "python",
        "matplotlib",
        "import numpy",
        "import matplotlib",
        "estudiante:",
        "tutor:",
        "specified by the user",
        "final_conclusion",
    ]

    if any(s in texto_lower for s in señales_malas):
        return True

    if "9.8" in pregunta_lower and ("g = 10" in texto_lower or "10\\," in texto_lower or "10 m/s" in texto_lower):
        return True

    if "0.20" in pregunta_lower and ("0.3" in texto_lower or "μ = 0.3" in texto_lower or "\\mu = 0.3" in texto_lower):
        return True

    return False


def enviar_pregunta(system_prompt: str, pregunta: str, intento: int = 1):
    user_content = pregunta

    if intento > 1:
        user_content = f"""
Resuelve nuevamente el problema, corrigiendo la respuesta anterior.

Obligatorio:
- No generes código.
- No uses Python.
- No uses gráficos.
- No escribas Estudiante ni Tutor.
- Usa exactamente los datos del enunciado.
- Resuelve todos los literales.

Problema:
{pregunta}
""".strip()

    mensajes = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    payload = {
        "messages": mensajes,
        "temperature": 0.05,
        "top_p": 0.85,
        "max_tokens": 1400,
        "stream": False,
        "stop": [
            "```",
            "\nEstudiante:",
            "\nTutor:",
            "### User:",
            "### System:",
            "specified by the user",
            "final_conclusion"
        ]
    }

    try:
        response = requests.post(URL, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    except requests.exceptions.RequestException as e:
        print(f"\n[Error de conexión con el servidor local]: {e}")
        return None
    except Exception as e:
        print(f"\n[Error procesando respuesta]: {e}")
        return None


def main():
    print("===================================================")
    print(" AGENTE TUTOR DE FÍSICA - PHI-4 GGUF MODO SEGURO")
    print("===================================================")
    print("Comandos:")
    print("  salir  -> cerrar")
    print("  multi  -> pegar pregunta de varias líneas")
    print("===================================================\n")

    skill = cargar_skill()
    system_prompt = construir_system_prompt(skill)

    while True:
        entrada = input("\nEstudiante: ").strip()

        if entrada.lower() in {"salir", "exit", "quit"}:
            print("Cerrando sesión del tutor.")
            break

        if entrada.lower() == "multi":
            pregunta = leer_pregunta_multilinea()
        else:
            pregunta = entrada

        if not pregunta.strip():
            continue

        respuesta = enviar_pregunta(system_prompt, pregunta, intento=1)

        if respuesta and respuesta_mala(respuesta, pregunta):
            respuesta = enviar_pregunta(system_prompt, pregunta, intento=2)

        print("\nTutor:\n")
        print(respuesta if respuesta else "[No se obtuvo respuesta]")
        print("\n" + "-" * 60)


if __name__ == "__main__":
    main()
