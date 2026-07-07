from __future__ import annotations

from pathlib import Path

import streamlit as st

from tutor_fisica.config import AppSettings, DEFAULT_SKILL_PATH


def render_sidebar() -> tuple[AppSettings, bool]:
    with st.sidebar:
        st.header("Configuración")

        with st.expander("Conexión", expanded=True):
            backend = st.selectbox(
                "Backend",
                options=["llama.cpp", "Ollama"],
                index=0,
            )

            if backend == "llama.cpp":
                endpoint = st.text_input(
                    "Endpoint",
                    value="http://localhost:8080/v1/chat/completions",
                )
                model_name = st.text_input(
                    "Nombre del modelo",
                    value="modelo_tutor_fisica_phi4_reasoning_q4_k_m.gguf",
                )
            else:
                endpoint = st.text_input(
                    "Endpoint",
                    value="http://localhost:11434/v1/chat/completions",
                )
                model_name = st.text_input(
                    "Nombre del modelo en Ollama",
                    value="tutor-fisica-epn",
                )

            skill_path_str = st.text_input(
                "Ruta de la skill",
                value=str(DEFAULT_SKILL_PATH),
            )

        with st.expander("Parámetros de generación", expanded=False):
            temperature = st.slider("Temperature", 0.0, 1.0, 0.05, 0.01)
            top_p = st.slider("Top-p", 0.1, 1.0, 0.85, 0.01)
            max_tokens = st.slider("Máximo de tokens", 512, 4096, 2200, 128)

        with st.expander("Opciones de RAG", expanded=True):
            usar_rag = st.checkbox(
                "Usar base semántica RAG",
                value=True,
                help="Recupera ejercicios similares y teoría del libro antes de consultar el modelo.",
            )
            mostrar_rag = st.checkbox(
                "Mostrar contexto recuperado",
                value=True,
                help="Muestra los IDs de ejercicios y fragmentos teóricos recuperados.",
            )

        st.divider()
        clear_chat = st.button("Limpiar conversación")
        st.info("Asegúrate de tener llama.cpp server corriendo en localhost:8080.")

    settings = AppSettings(
        backend=backend,
        endpoint=endpoint,
        model_name=model_name,
        skill_path=Path(skill_path_str).expanduser(),
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        usar_rag=usar_rag,
        mostrar_rag=mostrar_rag,
    )

    return settings, clear_chat
