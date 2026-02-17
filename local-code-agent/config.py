import os

PROJECT_ROOT = os.path.abspath(".")  # Will be overridden by user input later
CHROMA_PERSIST_DIR = "./chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # or use Gemini embeddings later

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-pro"
