from __future__ import annotations

import streamlit as st


def render_quick_examples() -> str | None:
    st.subheader("Ejemplos rápidos")

    # Primera fila: dinámica (los originales)
    fila1 = st.columns(6)
    with fila1[0]:
        ejemplo_newton = st.button("Bloque sin fricción")
    with fila1[1]:
        ejemplo_friccion = st.button("Bloque con fricción")
    with fila1[2]:
        ejemplo_polea = st.button("Sistema con polea")
    with fila1[3]:
        ejemplo_energia = st.button("Energía cinética")
    with fila1[4]:
        ejemplo_momento = st.button("Choque inelástico")
    with fila1[5]:
        ejemplo_cinematica = st.button("Movimiento acelerado")


    if ejemplo_newton:
        return (
            "Un bloque de 5 kg está sobre una mesa horizontal sin fricción. "
            "Se le aplica una fuerza constante de 20 N. ¿Cuál es su aceleración?"
        )

    if ejemplo_friccion:
        return (
            "Un bloque de 10 kg se desliza sobre una superficie horizontal rugosa. "
            "Se aplica una fuerza de 50 N en la dirección del movimiento. "
            "El coeficiente de fricción cinética es 0.30 y usa g = 9.8 m/s². "
            "¿Cuál es su aceleración?"
        )

    if ejemplo_polea:
        return (
            "Dos bloques están conectados por una cuerda ligera que pasa sobre una polea sin fricción. "
            "El bloque m1 = 8 kg está sobre una mesa horizontal sin fricción y el bloque m2 = 4 kg cuelga libremente. "
            "Si el sistema se libera desde el reposo, ¿cuál es la aceleración del sistema y la tensión en la cuerda? "
            "Usa g = 9.8 m/s²."
        )

    if ejemplo_energia:
        return (
            "Un cuerpo de 2 kg se mueve con una rapidez de 6 m/s. "
            "¿Cuál es su energía cinética?"
        )

    if ejemplo_momento:
        return (
            "Un carrito de 3 kg que se mueve a 4 m/s choca de frente con otro carrito de 2 kg en reposo. "
            "Después del choque, ambos quedan unidos y se mueven juntos. "
            "¿Cuál es la velocidad final del conjunto?"
        )

    if ejemplo_cinematica:
        return (
            "Un automóvil parte del reposo y acelera de forma constante a 2 m/s² durante 5 segundos. "
            "¿Qué distancia recorre y qué velocidad alcanza al final?"
        )

    return None
