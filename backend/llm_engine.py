"""
Language Model Engine Module
Builds structured prompts for the Mistral-7B language model using

The model runs entirely on-device with no internet connection required.
On Mac M3, Metal GPU acceleration is used automatically via the
n_gpu_layers parameter.

Model file (GGUF format) must be placed in the 'models/' directory.
See README.md for download instructions.
"""

from __future__ import annotations
import os
import gc
import sys

import threading

# The model file must be a GGUF-format Mistral-7B quantized model or an MLX folder
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MLX_FUSED_DIR = os.path.join(BASE_DIR, "training", "logosai-fused")

DEFAULT_MODEL_FILENAME = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"

# Module-level cached model instances
_llm = None       # llama-cpp instance
_mlx_model = None # mlx-lm model instance
_mlx_tokenizer = None
_engine_type = None # "llama-cpp" or "mlx"

# Concurrency & Memory Safeguards
_inference_lock = threading.Lock()
_load_lock = threading.Lock()


def _find_model_path() -> tuple[str, str] | None:
    """
    Finds either the MLX fused model or a GGUF file.
    Returns: (path, type) or None
    """
    # 1. Prefer the fine-tuned MLX model if it exists
    if os.path.isdir(MLX_FUSED_DIR) and os.path.exists(os.path.join(MLX_FUSED_DIR, "config.json")):
        return MLX_FUSED_DIR, "mlx"

    # 2. Fall back to GGUF models
    if os.path.isdir(MODELS_DIR):
        preferred = os.path.join(MODELS_DIR, DEFAULT_MODEL_FILENAME)
        if os.path.isfile(preferred):
            return preferred, "llama-cpp"

        # Any .gguf file
        for filename in os.listdir(MODELS_DIR):
            if filename.endswith(".gguf"):
                return os.path.join(MODELS_DIR, filename), "llama-cpp"

    return None


def load_model(n_ctx: int = 4096, n_gpu_layers: int = -1) -> bool:
    """
    Load the model into memory. Prefers MLX-LM if the fine-tuned folder exists.
    Thread-safe singleton loader.
    """
    global _llm, _mlx_model, _mlx_tokenizer, _engine_type

    with _load_lock:
        if _llm is not None or _mlx_model is not None:
            return True

        found = _find_model_path()
        if not found:
            print("[LLMEngine] No model found (checked training/logosai-fused and models/*.gguf)")
            return False

        model_path, engine = found
        _engine_type = engine

        if engine == "mlx":
            try:
                from mlx_lm import load
                print(f"[LLMEngine] Loading Mac-Native MLX-LM model: {os.path.basename(model_path)}")
                # Loading with local_path
                _mlx_model, _mlx_tokenizer = load(model_path)
                print("[LLMEngine] MLX-LM model loaded successfully.")
                return True
            except Exception as e:
                print(f"[LLMEngine] Error loading MLX model: {e}")
                return False
        else:
            # Llama-cpp (GGUF) fallback
            try:
                from llama_cpp import Llama
                print(f"[LLMEngine] Loading llama-cpp model: {os.path.basename(model_path)}")
                _llm = Llama(
                    model_path=model_path,
                    n_ctx=n_ctx,
                    n_gpu_layers=n_gpu_layers,
                    verbose=False
                )
                print("[LLMEngine] llama-cpp model loaded successfully.")
                return True
            except Exception as e:
                print(f"[LLMEngine] Error loading GGUF model: {e}")
                return False


def generate_answer_stream(
    prompt: str,
    max_tokens: int = 2048,  # Reduced from 8192 to save memory
    temperature: float = 0.8,
    top_p: float = 0.95,
    repeat_penalty: float = 1.1
):
    """
    Generator that yields tokens/chunks from the LLM.
    Protected by a global inference lock to prevent Metal OOM crashes
    from concurrent requests.
    """
    global _llm, _mlx_model, _mlx_tokenizer, _engine_type

    if _llm is None and _mlx_model is None:
        if not load_model():
            yield "⚠️ No model loaded. Please check model paths."
            return

    # Use lock to ensure only one user processes at a time on the GPU
    with _inference_lock:
        try:
            if _engine_type == "mlx":
                from mlx_lm import stream_generate
                from mlx_lm.sample_utils import make_sampler
                
                s = make_sampler(temperature, top_p)
                
                gen_kwargs = {
                    "sampler": s,
                    "max_tokens": max_tokens
                }
                
                # stream_generate yields tokens as strings (or objects in some versions)
                for token in stream_generate(
                    _mlx_model, 
                    _mlx_tokenizer, 
                    prompt,
                    **gen_kwargs
                ):
                    if isinstance(token, str):
                        yield token
                    elif hasattr(token, 'text'):
                        yield token.text
            else:
                # llama-cpp
                stream = _llm(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    repeat_penalty=repeat_penalty,
                    stop=["</s>", "[INST]"],
                    stream=True
                )
                for chunk in stream:
                    token = chunk["choices"][0]["text"]
                    if token:
                        yield token

        except RuntimeError as re:
            # Catch Metal OOM or related GPU errors
            if "Metal" in str(re) or "Out of Memory" in str(re):
                yield "\n[System Error] GPU memory limit reached. Please try your question again in a moment."
            else:
                yield f"\n[System Error] Inference failure: {str(re)}"
        except Exception as e:
            yield f"\n[LLMEngine] Error during inference: {str(e)}"
        finally:
            # Aggressive memory cleanup
            gc.collect()


def generate_answer(
    prompt: str,
    max_tokens: int = 2048,  # Reduced from 8192
    temperature: float = 0.8,
    top_p: float = 0.95,
    repeat_penalty: float = 1.1
) -> str:
    """
    Non-streaming wrapper for compatibility.
    """
    full_text = ""
    for token in generate_answer_stream(
        prompt, max_tokens, temperature, top_p, repeat_penalty
    ):
        full_text += token
    return full_text.strip()


def unload_model() -> None:
    """Free resources."""
    global _llm, _mlx_model, _mlx_tokenizer, _engine_type
    with _load_lock:
        _llm = None
        _mlx_model = None
        _mlx_tokenizer = None
        _engine_type = None
        gc.collect()
        print("[LLMEngine] Model unloaded.")


def is_model_available() -> bool:
    """Check if any model is available."""
    return _find_model_path() is not None
