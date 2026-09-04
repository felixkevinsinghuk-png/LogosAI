"""
train_lora_mlx.py
=================
Executes Parameter-Efficient Fine-Tuning (LoRA) on Apple Silicon using MLX.

This script wraps the 'mlx_lm.lora' module to train the RhemaLight AI assistant
on the synthetically generated theological dataset. It is optimized for 
Mac unified memory (MPS).
"""
import os
import subprocess
import sys

def run_training():
    # Configuration
    # Use a 4-bit quantized base model from mlx-community to fit in MacBook Air RAM (~4GB vs 14GB)
    base_model = "mlx-community/Mistral-7B-Instruct-v0.2-4bit"
    data_path = os.path.join(os.path.dirname(__file__), "data")
    output_path = os.path.join(os.path.dirname(__file__), "adapters")
    
    # MLX-LM LoRA training command
    # --iters: Number of training steps (500-1000 is a good start)
    # --batch-size: Set to 1 for memory-constrained MacBooks
    # --learning-rate: 1e-5 is a standard LoRA starting point
    # --max-seq-length: Reduced to 1024 to save VRAM
    # --grad-checkpoint: Recomputes activations to save memory
    cmd = [
        sys.executable, "-m", "mlx_lm", "lora",
        "--model", base_model,
        "--train",
        "--data", data_path,
        "--iters", "500",
        "--batch-size", "1",
        "--learning-rate", "1e-5",
        "--adapter-path", output_path,
        "--max-seq-length", "1024",
        "--grad-checkpoint"
    ]
    
    print("--- RhemaLight AI PEFT Training (MLX/Apple Silicon) ---")
    print(f"Base Model: {base_model}")
    print(f"Data Path:  {data_path}")
    print(f"Output:     {output_path}\n")
    print("Starting training process. This will utilize your Mac's GPU...")
    
    try:
        subprocess.run(cmd, check=True)
        print("\nTraining completed successfully!")
        print(f"Your fine-tuned LoRA adapters are saved in: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"\nTraining failed with error: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    # Ensure dependencies are installed
    try:
        import mlx_lm
    except ImportError:
        print("Required library 'mlx-lm' not found. Please run: pip install mlx-lm mlx")
        sys.exit(1)
        
    run_training()
