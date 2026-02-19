import os

PROJECT_ROOT = os.environ.get("PROJECT_ROOT", os.path.abspath("."))
CHROMA_PERSIST_DIR = "./chroma_db"
EMBEDDING_MODEL = "models/text-embedding-004"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
    raise ValueError("GEMINI_API_KEY environment variable not set or invalid. Please set it to your actual API key.")

GEMINI_MODEL = "gemini-1.5-pro"
