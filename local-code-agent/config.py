import os

PROJECT_ROOT = os.environ.get("PROJECT_ROOT", os.path.abspath("."))
CHROMA_PERSIST_DIR = "./chroma_db"
EMBEDDING_MODEL = "models/text-embedding-004"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-pro"
