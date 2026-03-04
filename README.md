# LogosAI — Bible Contextual AI Assistant

A locally-running Bible AI assistant powered by **Mistral-7B**. Provides contextual explanations of Bible passages with original Hebrew and Greek language meaning — completely offline, zero cost.

---

## Features

- 🤖 **Local AI** — Mistral-7B runs entirely on your Mac (no API key, no internet)
- 📖 **Full KJV Bible** — 31,000+ verses indexed for semantic search
- 🔤 **Original Languages** — Hebrew & Greek meaning via Strong's Concordance
- 🔍 **RAG Pipeline** — Retrieval-Augmented Generation for grounded answers
- 🖥️ **Chat UI** — Clean, dark-mode web interface at `localhost:8000`

---

## Requirements

- **macOS** with Apple Silicon (M1/M2/M3) recommended
- **Anaconda or Miniconda** installed
- **~6 GB free disk space** (model + embeddings)
- Internet connection on **first run only** (downloads Bible data)

---

## Setup (Anaconda)

### 1. Create and activate a conda environment

```bash
conda create -n logosai python=3.11 -y
conda activate logosai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Mac M3 Metal GPU tip** — for full GPU acceleration with llama-cpp-python, install it separately with the Metal flag:
> ```bash
> conda activate logosai
> CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
> ```
> This lets Mistral-7B run on the M-series GPU instead of CPU only.

### 3. Download the Mistral-7B model

The model file is **not included** in the repository (too large). Download it from HuggingFace:

**Recommended model** (4-bit quantized, ~4.4 GB):
```
mistral-7b-instruct-v0.1.Q4_K_M.gguf
```

Download page: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF

Place the downloaded `.gguf` file in the `models/` directory:
```
LogosAI/
└── models/
    └── mistral-7b-instruct-v0.1.Q4_K_M.gguf   ← here
```

### 4. Run the application

```bash
conda activate logosai
python3 main.py
```

On **first run**, the system will automatically:
1. Download the KJV Bible dataset (~3 MB)
2. Download the Strong's Hebrew & Greek lexicon (~8 MB)
3. Index all 31,000+ Bible verses into the vector database (~5–15 minutes)

Subsequent starts are instant — the index is cached locally in `embeddings/`.

### 5. Open the chat interface

Visit: **http://localhost:8000**

---

## Project Structure

```
LogosAI/
├── main.py                    # Entry point — run this to start
├── requirements.txt
├── frontend/
│   ├── index.html             # Chat UI
│   ├── style.css              # Styling
│   └── app.js                 # Frontend JavaScript
├── backend/
│   ├── api.py                 # FastAPI endpoints
│   ├── controller.py          # RAG pipeline coordinator
│   ├── query_processor.py     # Input cleaning
│   ├── context_retrieval.py   # Semantic search + language lookup
│   ├── prompt_builder.py      # Mistral prompt construction
│   └── llm_engine.py          # Mistral-7B inference engine
├── vector_store/
│   ├── embedder.py            # Sentence-transformer embeddings
│   └── vector_db.py           # ChromaDB vector storage & search
├── database/
│   ├── bible_loader.py        # KJV Bible data loader
│   └── original_language.py   # Strong's lexicon loader
├── data/                      # Auto-downloaded Bible & lexicon JSON
├── embeddings/                # ChromaDB persistent vector index
└── models/                    # Place your .gguf model file here
```

---

## Free & Open-Source Stack

| Component | Tool | License |
|-----------|------|---------|
| Language Model | Mistral-7B (GGUF) | Apache 2.0 |
| LLM Runtime | llama-cpp-python | MIT |
| Embeddings | all-MiniLM-L6-v2 | Apache 2.0 |
| Vector DB | ChromaDB | Apache 2.0 |
| Web Framework | FastAPI + Uvicorn | MIT |
| Bible Data | KJV (scrollmapper) | Public Domain |
| Lexicon | Strong's (openscriptures) | Public Domain |

All components are **completely free** with no usage limits.

---

---

## PEFT Fine-Tuning (Step 2 of Ways.md)

You can now customize the model's reasoning and theological style using the **MLX-LM** pipeline optimized for Apple Silicon.

### 1. Generate Training Data
Synthesize 100 high-quality theological training pairs split into `train.jsonl` and `valid.jsonl`:
```bash
python3 training/generate_dataset.py
```

### 2. Run LoRA Training
Train the model on your Mac's GPU using the MLX library:
```bash
python3 training/train_lora_mlx.py
```

### 3. Fuse and Export
Merge the learned adapters back into the standalone Mistral model:
```bash
python3 training/fuse_and_export.py
```
> After fusion, you can convert the resulting folder to `.gguf` using `llama.cpp` tools to use it in the live API.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serve the chat frontend |
| `POST` | `/chat` | Submit a question, get an AI answer |
| `GET` | `/health` | Health check |
| `GET` | `/status` | Model and index status |

### Example `/chat` request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What does John 3:16 mean?", "top_k": 5}'
```

---

## Troubleshooting

**Wrong environment / `ModuleNotFoundError`:**
> Make sure you ran `conda activate logosai` before `python3 main.py`.
> Check with: `conda info --envs`

**Model not loading:**
> Ensure the `.gguf` file is in `models/` and is a valid Mistral-7B quantized model.

**Slow first start:**
> Indexing 31k verses takes 5–15 minutes on first run. This only happens once.

**Out of memory:**
> Try a smaller quantization like `Q3_K_M` or reduce `n_ctx` in `llm_engine.py`.

**Embedding model download:**
> `sentence-transformers` downloads `all-MiniLM-L6-v2` automatically on first use (~90 MB, cached by Hugging Face).

**Re-entering the environment next time:**
> Each new terminal session requires `conda activate logosai` before running.
