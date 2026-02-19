import sys
from unittest.mock import MagicMock

# Mock dependencies
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["google.ai"] = MagicMock()
sys.modules["google.ai.generativelanguage"] = MagicMock()
sys.modules["chromadb"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()
sys.modules["tree_sitter"] = MagicMock()
sys.modules["tree_sitter_languages"] = MagicMock()

import os
# Set dummy API key for testing
os.environ["GEMINI_API_KEY"] = "fake_key_for_test"

sys.path.append(os.path.abspath("local-code-agent"))

# Try to import run
import run
print("Successfully imported run.py")
