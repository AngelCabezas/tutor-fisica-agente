from __future__ import annotations

import requests
import streamlit as st

from tutor_fisica.config import LOG_DIR
from tutor_fisica.diagrams.drawers import crear_diagrama_desde_pregunta, mostrar_figura
from tutor_fisica.prompts import construir_pregunta_con_rag, construir_system_prompt
from tutor_fisica.services.llm_client import llamar_modelo
from tutor_fisica.services.log_service import guardar_log
from tutor_fisica.services.rag_service import cargar_rag, construir_contexto_rag
from tutor_fisica.services.skill_service import cargar_skill
from tutor_fisica.ui.examples import render_quick_examples
from tutor_fisica.ui.sidebar import render_sidebar
from tutor_fisica.utils.response_validation import respuesta_mala
from tutor_fisica.utils.text_formatting import formatear_respuesta_markdown


def inicializar_estado() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []


def limpiar_chat() -> None:
    st.session_state.messages = []


def mostrar_historial() -> None:
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(msg["content"])


def mostrar_resumen_rag(resumen_rag: dict) -> None:
    with st.expander("Contexto RAG recuperado", expanded=False):
        st.markdown("**Ejercicios recuperados:**")
        for item in resumen_rag["ejercicios"]:
            st.write(item)

        st.markdown("**Consulta teórica usada:**")
        st.write(resumen_rag["consulta_teoria"])

        st.markdown("**Capítulos preferidos:**")
        capitulos = resumen_rag["capitulos_preferidos"]
        st.write(", ".join(capitulos) if capitulos else "Ninguno")

        st.markdown("**Fragmentos teóricos recuperados:**")
        if resumen_rag["teoria"]:
            for item in resumen_rag["teoria"]:
                st.write(item)
        else:
            st.write("No se recuperaron fragmentos teóricos suficientemente relacionados.")


def preparar_pregunta(prompt: str, usar_rag: bool, mostrar_rag: bool) -> str:
    if not usar_rag:
        return prompt

    try:
        collection_ejercicios, registro_ejercicios, collection_teoria = cargar_rag()

        contexto_rag, resumen_rag = construir_contexto_rag(
            pregunta=prompt,
            collection_ejercicios=collection_ejercicios,
            registro_ejercicios=registro_ejercicios,
            collection_teoria=collection_teoria,
        )

        if mostrar_rag:
            mostrar_resumen_rag(resumen_rag)

        return construir_pregunta_con_rag(
            pregunta=prompt,
            contexto_rag=contexto_rag,
        )

    except Exception as exc:
        st.warning(f"No se pudo usar RAG. Se consultará solo el modelo. Detalle: {exc}")
        return prompt


def generar_respuesta(prompt: str, pregunta_para_modelo: str, settings, system_prompt: str) -> str:
    mejor_respuesta = ""

    for intento in range(1, 4):
        respuesta_temp = llamar_modelo(
            endpoint=settings.endpoint,
            model_name=settings.model_name,
            system_prompt=system_prompt,
            historial=[],
            pregunta=pregunta_para_modelo,
            temperature=settings.temperature,
            top_p=settings.top_p,
            max_tokens=settings.max_tokens,
            intento=intento,
        )

        mejor_respuesta = respuesta_temp

        if not respuesta_mala(respuesta_temp, prompt):
            return respuesta_temp

    st.warning(
        "La respuesta generada todavía contiene formato no permitido. "
        "Se muestra la mejor respuesta disponible, pero conviene revisar la skill."
    )

    return mejor_respuesta


def resolver_pregunta(prompt: str, settings, system_prompt: str) -> None:
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Resolviendo paso a paso..."):
            pregunta_para_modelo = preparar_pregunta(
                prompt=prompt,
                usar_rag=settings.usar_rag,
                mostrar_rag=settings.mostrar_rag,
            )

            respuesta = generar_respuesta(
                prompt=prompt,
                pregunta_para_modelo=pregunta_para_modelo,
                settings=settings,
                system_prompt=system_prompt,
            )

            respuesta_visible = formatear_respuesta_markdown(respuesta)
            st.markdown(respuesta_visible)

            _, fig = crear_diagrama_desde_pregunta(prompt)
            if fig is not None:
                st.subheader("Diagrama de apoyo")
                mostrar_figura(fig)

            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": respuesta_visible})

            guardar_log(
                pregunta=prompt,
                respuesta=respuesta,
                backend=settings.backend,
                modelo=settings.model_name,
            )


def main() -> None:
    LOG_DIR.mkdir(exist_ok=True)

    st.set_page_config(
        page_title="Tutor de Física EPN",
        page_icon="📘",
        layout="wide",
    )

    inicializar_estado()

    st.title("📘 Tutor de Física EPN")
    st.caption("Interfaz gráfica para modelo Phi-4 GGUF con skill pedagógica y diagramas controlados")

    settings, clear_chat = render_sidebar()

    if clear_chat:
        limpiar_chat()
        st.rerun()

    try:
        skill = cargar_skill(settings.skill_path)
        system_prompt = construir_system_prompt(skill)
        st.sidebar.success("Skill cargada correctamente")
    except Exception as exc:
        st.sidebar.error(f"No se pudo cargar la skill: {exc}")
        return

    ejemplo = render_quick_examples()
    mostrar_historial()

    prompt = st.chat_input("Escribe o pega un ejercicio de Física...")
    if ejemplo:
        prompt = ejemplo

    if not prompt:
        return

    try:
        resolver_pregunta(
            prompt=prompt,
            settings=settings,
            system_prompt=system_prompt,
        )
    except requests.exceptions.ConnectionError:
        st.error(
            "No se pudo conectar con el servidor local. "
            "Verifica que llama.cpp u Ollama esté ejecutándose."
        )
    except requests.exceptions.HTTPError as exc:
        st.error(f"Error HTTP del backend: {exc}")
    except Exception as exc:
        st.error(f"Error inesperado: {exc}")


if __name__ == "__main__":
    main()
