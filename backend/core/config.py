import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Settings:
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")
    
    LLM_BACKEND = os.getenv("LLM_BACKEND", "mlx")
    LLM_MODEL_PATH = os.getenv("LLM_MODEL_PATH", "mlx-community/Mistral-7B-Instruct-v0.2-4bit")
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./embeddings")
    SCRIPTURE_DATA_PATH = os.getenv("SCRIPTURE_DATA_PATH", "./database/bible_data")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")

settings = Settings()
