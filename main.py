"""
LogosAI — Main Entry Point
===========================
Starts the FastAPI web server and performs first-run initialization.

On first run:
  1. Downloads the KJV Bible dataset (if not already on disk).
  2. Downloads the Strong's lexicon (if not already on disk).
  3. Indexes all Bible verses into ChromaDB (one-time, ~5–10 minutes).
  4. Starts the Uvicorn web server.

Usage:
    python main.py

Then open http://localhost:8000 in your browser.
"""

import os
import sys

# ── Ensure the project root is on the Python path ────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def run_startup_checks() -> None:
    """
    Download data and index the Bible if this is the first run.
    Skips any step that has already been completed.
    """
    print("\n[LogosAI] Bible Contextual AI Assistant")

    # Step 1: Bible data
    print("\n[Setup] Checking Bible dataset...")
    try:
        from database.bible_loader import download_bible_data
        download_bible_data()
        print("[Setup] ✓ Bible dataset ready.")
    except Exception as e:
        print(f"[Setup] ⚠ Could not load Bible data: {e}")

    # Step 2: Strong's lexicon
    print("\n[Setup] Checking Strong's lexicon...")
    try:
        from database.original_language import download_lexicon
        download_lexicon()
        print("[Setup] ✓ Strong's lexicon ready.")
    except Exception as e:
        print(f"[Setup] ⚠ Could not load Strong's lexicon: {e}")

    # Step 3: Vector index
    print("\n[Setup] Checking Bible vector index...")
    try:
        from vector_store.vector_db import is_indexed, index_bible
        if not is_indexed():
            print("[Setup] First run detected — indexing Bible verses...")
            print("[Setup] This will take 5–15 minutes. Please wait.")
            index_bible()
            print("[Setup] ✓ Bible index complete.")
        else:
            print("[Setup] ✓ Bible index already exists. Skipping.")
    except Exception as e:
        print(f"[Setup] ⚠ Could not index Bible: {e}")

    # Step 4: LLM availability check
    print("\n[Setup] Checking language model...")
    try:
        from backend.llm_engine import is_model_available
        if is_model_available():
            print("[Setup] ✓ Mistral-7B model found.")
        else:
            print(
                "[Setup] ⚠ No GGUF model found in the models/ directory.\n"
                "[Setup]   Download a Mistral-7B GGUF model and place it there.\n"
                "[Setup]   The app will still run but responses will be limited."
            )
    except Exception as e:
        print(f"[Setup] ⚠ Could not check model: {e}")

    print("\n[LogosAI] Web server: http://localhost:8000")
    print("[LogosAI] Press Ctrl+C to stop.\n")


def main() -> None:
    run_startup_checks()

    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn is not installed.")
        print("Run: pip install uvicorn")
        sys.exit(1)

    uvicorn.run(
        "backend.api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,          # Set True for development hot-reload
        log_level="info"
    )


if __name__ == "__main__":
    main()
