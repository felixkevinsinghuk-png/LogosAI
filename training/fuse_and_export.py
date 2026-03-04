"""
fuse_and_export.py
==================
Fuses trained LoRA adapters back into the base Mistral model.

This is the final step of the PEFT pipeline. It merges the 'style' 
learned during fine-tuning into the base weights, creating a new
standalone model folder that can then be converted to .gguf.
"""
import os
import subprocess
import sys

def fuse_model():
    # Configuration
    # Must match the base model used in train_lora_mlx.py
    base_model = "mlx-community/Mistral-7B-Instruct-v0.2-4bit"
    adapter_path = os.path.join(os.path.dirname(__file__), "adapters")
    save_path = os.path.join(os.path.dirname(__file__), "logosai-fused")
    
    if not os.path.exists(adapter_path):
        print(f"Error: No adapters found at {adapter_path}. Please run training first.")
        return

    # MLX-LM Fuse command
    cmd = [
        sys.executable, "-m", "mlx_lm.fuse",
        "--model", base_model,
        "--adapter-path", adapter_path,
        "--save-path", save_path
    ]
    
    print("--- LogosAI Model Fusion ---")
    print(f"Base Model:    {base_model}")
    print(f"Adapter Path:  {adapter_path}")
    print(f"Saving to:     {save_path}\n")
    print("Merging weights... this may take a few minutes.")
    
    try:
        subprocess.run(cmd, check=True)
        print("\nFusion completed successfully!")
        print(f"Your fused model is saved in: {save_path}")
        print("\nNEXT STEP (Final GGUF Conversion):")
        print("To use this in the LogosAI backend, you must convert it to GGUF format.")
        print("If you have llama.cpp installed, run:")
        print(f"python3 llama.cpp/convert.py {save_path} --outfile {save_path}/model.gguf --outtype q4_k_m")
    except subprocess.CalledProcessError as e:
        print(f"\nFusion failed with error: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    fuse_model()
