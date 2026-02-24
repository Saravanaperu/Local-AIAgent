import os

PROJECT_ROOT = os.environ.get("PROJECT_ROOT", os.path.abspath("."))
CHROMA_PERSIST_DIR = "./chroma_db"
EMBEDDING_MODEL = "models/text-embedding-004"

_GEMINI_API_KEY = None

def get_gemini_api_key():
    """
    Returns the GEMINI_API_KEY from environment variables.
    Raises ValueError if the key is not set or is invalid.
    """
    global _GEMINI_API_KEY
    if _GEMINI_API_KEY:
        return _GEMINI_API_KEY

    key = os.environ.get("GEMINI_API_KEY")
    if not key or key == "YOUR_API_KEY_HERE":
        raise ValueError("GEMINI_API_KEY environment variable not set or invalid. Please set it to your actual API key.")

    _GEMINI_API_KEY = key
    return _GEMINI_API_KEY

def validate_config():
    """
    Validates the configuration.
    """
    get_gemini_api_key()

def __getattr__(name):
    if name == "GEMINI_API_KEY":
        return get_gemini_api_key()
    raise AttributeError(f"module {__name__} has no attribute {name}")

GEMINI_MODEL = "gemini-1.5-pro"
