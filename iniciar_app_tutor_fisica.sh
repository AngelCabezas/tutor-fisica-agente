#!/bin/bash

cd ~/tutor_fisica_agente || exit 1

source entorno_gui/bin/activate

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export HF_HUB_DISABLE_TELEMETRY=1

streamlit run app_tutor_fisica.py \
  --server.port 8502 \
  --server.fileWatcherType none
