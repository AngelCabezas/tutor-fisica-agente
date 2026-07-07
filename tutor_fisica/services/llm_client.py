from __future__ import annotations

import requests

from tutor_fisica.utils.text_formatting import corregir_formato_salida


def llamar_modelo(
    endpoint: str,
    model_name: str,
    system_prompt: str,
    historial: list,
    pregunta: str,
    temperature: float,
    top_p: float,
    max_tokens: int,
    intento: int = 1,
) -> str:
    user_content = pregunta

    if intento > 1:
        user_content = f"""
Tu respuesta anterior no cumplió el formato.

Corrige y responde nuevamente.

OBLIGATORIO:

* La primera línea debe ser exactamente: 1. Principio físico
* Cada encabezado debe ir solo en una línea.
* Después de cada encabezado deja una línea en blanco.
* Usa Markdown simple para listas.
* Usa LaTeX solo para ecuaciones dentro de $$...$$.
* Separa las ecuaciones del texto con saltos de línea.
* No repitas ecuaciones.
* No inventes datos.
* No generes código Python.
* No uses matplotlib.
* No generes gráficos.
* No generes bloques <GRAFICO_PYTHON>.
* No escribas Estudiante ni Tutor.

Problema:
{pregunta}
""".strip()

    mensajes = [{"role": "system", "content": system_prompt}]

    if intento == 1 and not historial:
        mensajes.append({
            "role": "user",
            "content": "Calcula la fuerza neta si una masa m = 2 kg acelera a a = 3 m/s^2."
        })
        mensajes.append({
            "role": "assistant",
            "content": r"""1. Principio físico

La Segunda Ley de Newton establece la relación directa entre fuerza, masa y aceleración. Este principio aplica porque se conoce la masa del cuerpo y la aceleración que experimenta. Por lo tanto, la fuerza neta se obtiene multiplicando la masa por la aceleración.

2. Datos del problema

* Masa: $m = 2 \text{ kg}$
* Aceleración: $a = 3 \text{ m/s}^2$

3. Incógnitas

Se debe calcular la fuerza neta:

$$
F = ?
$$

4. Ecuaciones

La Segunda Ley de Newton establece:

$$
F = m a
$$

5. Sustitución con unidades

Sustituimos los valores:

$$
F = (2 \text{ kg})(3 \text{ m/s}^2)
$$

6. Desarrollo matemático

Multiplicamos los valores numéricos:

$$
F = 6 \text{ N}
$$

7. Respuestas finales

$$
\boxed{F = 6 \text{ N}}
$$

8. Interpretación física breve

El resultado indica que se requiere una fuerza neta de 6 N para producir esa aceleración en la masa dada."""
        })

    for item in historial:
        mensajes.append({"role": item["role"], "content": item["content"]})

    mensajes.append({"role": "user", "content": user_content})

    payload = {
        "model": model_name,
        "messages": mensajes,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "stream": False,
        "stop": [
            "```",
            "<GRAFICO_PYTHON>",
            "<|im_end|>",
            "<|end|>",
            "<|endoftext|>",
            "\nEstudiante:",
            "\nTutor:",
            "### User:",
            "### System:",
        ],
    }

    response = requests.post(endpoint, json=payload, timeout=300)
    response.raise_for_status()

    data = response.json()
    texto = data["choices"][0]["message"]["content"].strip()

    return corregir_formato_salida(texto)
