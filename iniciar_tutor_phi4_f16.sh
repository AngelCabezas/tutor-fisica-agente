#!/bin/bash

# Activar el entorno virtual (ruta relativa)
source ./entorno_llamacpp/bin/activate

# Entrar a la carpeta de llama.cpp (ruta relativa)
cd ./llama.cpp

# Iniciar el servidor apuntando al modelo un nivel arriba
./build/bin/llama-server \
  -m ../modelo_tutor_fisica_phi4_reasoning_f16.gguf \
  --host 127.0.0.1 \
  --port 8082 \
  -c 32768
  -ngl 999
