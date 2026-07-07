# Tutor de Física EPN - versión modular

Esta carpeta contiene una reorganización del archivo Streamlit original en módulos pequeños.

## Ejecutar

```bash
cd tutor_fisica_clean
streamlit run app.py
```

## Estructura

- `app.py`: punto de entrada de Streamlit.
- `tutor_fisica/config.py`: rutas, constantes y configuración.
- `tutor_fisica/prompts.py`: construcción de prompts.
- `tutor_fisica/services/`: conexión al modelo, RAG, skill y logs.
- `tutor_fisica/utils/`: limpieza de texto, validaciones y extracción de valores.
- `tutor_fisica/diagrams/`: detección y generación de diagramas.
- `tutor_fisica/ui/`: componentes visuales de Streamlit.

## Nota

Se mantuvo la lógica funcional del archivo original, pero se separó por responsabilidades para facilitar mantenimiento, pruebas y extensión.
