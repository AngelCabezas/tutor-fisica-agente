import os
import gc
import torch

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel


# ============================================================
# CONFIGURACIÓN
# ============================================================

MODELO_BASE = "microsoft/Phi-4-reasoning"

# Opción recomendada: usar el adaptador final guardado
ADAPTADOR = "./modelo_tutor_fisica_phi4_reasoning_qlora"

# Si quieres fusionar directamente desde el checkpoint ganador, usa esta línea:
# ADAPTADOR = "./checkpoints_phi4_reasoning_qlora/checkpoint-250"

SALIDA = "./modelo_tutor_fisica_phi4_reasoning_fusionado"


print("====================================================")
print(" FUSIÓN DEL MODELO GANADOR PHI-4 REASONING + QLORA ")
print("====================================================")
print(f"Modelo base: {MODELO_BASE}")
print(f"Adaptador: {ADAPTADOR}")
print(f"Salida: {SALIDA}")


# ============================================================
# LIMPIEZA INICIAL
# ============================================================

gc.collect()

if torch.cuda.is_available():
    torch.cuda.empty_cache()
    torch.cuda.synchronize()


# ============================================================
# TOKENIZER
# ============================================================

print("\n📚 Cargando tokenizer...")

try:
    tokenizer = AutoTokenizer.from_pretrained(
        ADAPTADOR,
        trust_remote_code=True,
        use_fast=True,
    )
except Exception:
    tokenizer = AutoTokenizer.from_pretrained(
        MODELO_BASE,
        trust_remote_code=True,
        use_fast=True,
    )

tokenizer.padding_side = "right"

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


# ============================================================
# MODELO BASE EN BF16
# ============================================================

print("\n🧠 Cargando modelo base en BF16...")

modelo_base = AutoModelForCausalLM.from_pretrained(
    MODELO_BASE,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True,
    low_cpu_mem_usage=True,
)

modelo_base.config.use_cache = False


# ============================================================
# ACOPLAR ADAPTADOR QLORA
# ============================================================

print("\n🎓 Acoplando adaptador QLoRA ganador...")

modelo = PeftModel.from_pretrained(
    modelo_base,
    ADAPTADOR,
    is_trainable=False,
)

modelo.eval()


# ============================================================
# FUSIONAR
# ============================================================

print("\n🔗 Fusionando adaptador con el modelo base...")

modelo_fusionado = modelo.merge_and_unload()

modelo_fusionado.eval()


# ============================================================
# GUARDAR MODELO FUSIONADO
# ============================================================

print(f"\n💾 Guardando modelo fusionado en: {SALIDA}")

os.makedirs(SALIDA, exist_ok=True)

modelo_fusionado.save_pretrained(
    SALIDA,
    safe_serialization=True,
    max_shard_size="4GB",
)

tokenizer.save_pretrained(SALIDA)

print("\n✅ Fusión completada correctamente.")
print(f"Modelo fusionado guardado en: {SALIDA}")
