# Arquitectura modular del Tutor de Física EPN

## Archivo principal

### app_tutor_fisica.py

Es la entrada principal de la interfaz Streamlit.

Responsabilidades:
- Configurar la página.
- Mostrar título, subtítulo y ejemplos rápidos.
- Leer la pregunta del usuario.
- Coordinar Skill, RAG, modelo, formato de respuesta, diagramas y logs.

No debe contener lógica extensa de RAG, diagramas, validación o conexión al modelo.

---

## Paquete principal

### tutor_fisica/

Contiene la lógica modular del tutor.

---

## Configuración

### tutor_fisica/config.py

Responsabilidades:
- Definir rutas principales del proyecto.
- Definir rutas de Skill, RAG y logs.
- Definir nombres de colecciones ChromaDB.
- Definir límites de distancia semántica.

Modificar aquí si cambian:
- La ruta de la skill.
- La ruta de la base semántica.
- Los nombres de colecciones.
- Los archivos de historial.

---

## Prompts

### tutor_fisica/prompts.py

Responsabilidades:
- Construir el system prompt usando la skill.
- Construir la pregunta enriquecida con RAG.
- Definir reglas de control para evitar que el modelo copie datos recuperados.

Modificar aquí si quieres cambiar:
- La estructura pedagógica.
- Las reglas de formato.
- Las restricciones del modelo.
- Las instrucciones RAG.

---

## Servicios

### tutor_fisica/services/skill_service.py

Carga el archivo SKILL.md.

---

### tutor_fisica/services/llm_client.py

Responsabilidades:
- Enviar la solicitud al backend llama.cpp u Ollama.
- Construir los mensajes system/user/assistant.
- Manejar temperature, top_p y max_tokens.
- Aplicar stop words.
- Devolver la respuesta del modelo.

Modificar aquí si cambias:
- Backend.
- Formato de API.
- Mensajes few-shot.
- Reintentos del modelo.

---

### tutor_fisica/services/rag_service.py

Responsabilidades:
- Cargar ChromaDB.
- Cargar el registro JSON de ejercicios.
- Buscar ejercicios similares.
- Buscar fragmentos teóricos.
- Construir el contexto RAG.

Modificar aquí si cambias:
- Modelo de embeddings.
- Número de ejercicios recuperados.
- Número de fragmentos teóricos.
- Filtros por capítulo.
- Reglas de clasificación temática.

---

### tutor_fisica/services/log_service.py

Responsabilidades:
- Guardar historial de preguntas y respuestas en JSONL.

Modificar aquí si cambias:
- Formato del log.
- Ruta del historial.
- Campos guardados.

---

## Utilidades

### tutor_fisica/utils/text_formatting.py

Responsabilidades:
- Limpiar LaTeX malformado.
- Corregir salida del modelo.
- Convertir encabezados a Markdown.
- Eliminar bloques no permitidos.

Modificar aquí si el modelo genera:
- LaTeX incorrecto.
- Encabezados mal formateados.
- Bloques de código no deseados.
- Texto repetido.

---

### tutor_fisica/utils/response_validation.py

Responsabilidades:
- Detectar respuestas malas.
- Validar que empiecen con "1. Principio físico".
- Detectar código, matplotlib, bloques prohibidos o símbolos arrastrados.

Modificar aquí si quieres añadir nuevas reglas de rechazo.

---

### tutor_fisica/utils/value_extractors.py

Responsabilidades:
- Extraer valores numéricos desde el enunciado.
- Extraer masa, fuerza, ángulo, gravedad, coeficientes de fricción, peso, etc.

Modificar aquí si un diagrama no lee bien los datos del problema.

---

## Diagramas

### tutor_fisica/diagrams/detector.py

Responsabilidades:
- Detectar qué tipo de diagrama corresponde a una pregunta.

Tipos actuales:
- bloque_simple
- friccion
- friccion_estatica_coeficiente
- polea
- atwood
- plano_inclinado
- tiro_parabolico
- campo_magnetico
- flotacion
- hidrostatica
- mrua
- vectores

Modificar aquí si quieres que una pregunta active otro tipo de diagrama.

---

### tutor_fisica/diagrams/drawers.py

Responsabilidades:
- Generar los diagramas con Matplotlib.
- Dibujar bloques, poleas, vectores, plano inclinado, tiro parabólico, etc.
- Mostrar figuras en Streamlit.

Modificar aquí si quieres cambiar la apariencia de los gráficos.

---

## Interfaz

### tutor_fisica/ui/sidebar.py

Responsabilidades:
- Mostrar configuración del backend.
- Mostrar ruta de skill.
- Mostrar sliders de temperature, top_p y max_tokens.
- Mostrar controles RAG.

---

### tutor_fisica/ui/examples.py

Responsabilidades:
- Definir los ejemplos rápidos de la interfaz.

Modificar aquí si quieres agregar más botones de ejemplo.

---

## Lanzadores

### iniciar_app_tutor_fisica.sh

Lanza la app principal usando entorno_gui.

Incluye:
- Activación del entorno.
- Modo offline para Hugging Face.
- Desactivación del file watcher de Streamlit.
- Puerto 8502.

Uso:

./iniciar_app_tutor_fisica.sh

---

## Respaldos importantes

### app_tutor_fisica_legacy_*.py

Contiene la versión anterior completa antes de modularizar.

No borrar todavía.

---

### app_modular.py

Copia de prueba de la versión modular.

Se puede conservar como respaldo temporal.

---

## Regla general de mantenimiento

Si quiero cambiar la respuesta pedagógica:
- Revisar prompts.py
- Revisar SKILL.md

Si quiero cambiar RAG:
- Revisar rag_service.py
- Revisar config.py

Si quiero cambiar gráficos:
- Revisar diagrams/detector.py
- Revisar diagrams/drawers.py

Si quiero cambiar la interfaz:
- Revisar app_tutor_fisica.py
- Revisar ui/sidebar.py
- Revisar ui/examples.py

Si quiero cambiar validaciones:
- Revisar utils/response_validation.py
- Revisar utils/text_formatting.py
