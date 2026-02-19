
import sys
import unittest
from unittest.mock import MagicMock

# Mock chromadb
mock_chromadb = MagicMock()
sys.modules["chromadb"] = mock_chromadb

# Mock tree_sitter_languages
mock_tsl = MagicMock()
sys.modules["tree_sitter_languages"] = mock_tsl

# Mock google
mock_google = MagicMock()
sys.modules["google"] = mock_google

# Mock google.generativeai
mock_genai = MagicMock()
sys.modules["google.generativeai"] = mock_genai

# Mock numpy
mock_np = MagicMock()
sys.modules["numpy"] = mock_np

# Mock sentence_transformers
mock_st = MagicMock()
sys.modules["sentence_transformers"] = mock_st

import os
# Set dummy API key for testing
os.environ["GEMINI_API_KEY"] = "fake_key_for_test"

# Add local-code-agent to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

from agent.tools import ask_orchestrator, execute_tool

class TestTools(unittest.TestCase):
    def test_ask_orchestrator_returns_error_string(self):
        # New behavior: Returns error string
        result = ask_orchestrator(action="some_action")
        self.assertEqual(result, "Error: This tool is only available when running under the Orchestrator.")

    def test_execute_tool_ask_orchestrator(self):
         # New behavior: execute_tool returns the error string directly
        result = execute_tool("ask_orchestrator", {"action": "some_action"})
        # It should NOT start with "Error executing tool" because no exception was raised.
        self.assertEqual(result, "Error: This tool is only available when running under the Orchestrator.")

if __name__ == "__main__":
    unittest.main()
