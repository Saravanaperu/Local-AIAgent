import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Mock dependencies before importing anything that might use them
sys.modules["chromadb"] = MagicMock()
sys.modules["tree_sitter_languages"] = MagicMock()
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["google.ai"] = MagicMock()
sys.modules["google.ai.generativelanguage"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()

# Set dummy API key for testing
os.environ["GEMINI_API_KEY"] = "fake_key_for_test"

# Add local-code-agent to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

# Mock internal agent modules that are not needed for testing handle_orchestrator_request
sys.modules["agent.agents"] = MagicMock()
sys.modules["agent.execution"] = MagicMock()

from agent.orchestrator import Orchestrator

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = Orchestrator()

    @patch("agent.orchestrator.search_code")
    def test_handle_orchestrator_request_search(self, mock_search):
        mock_search.return_value = "search result"
        args = {"action": "search", "query": "test query"}
        result = self.orchestrator.handle_orchestrator_request(args)

        mock_search.assert_called_once_with("test query")
        self.assertEqual(result, "search result")

    @patch("agent.orchestrator.read_file")
    def test_handle_orchestrator_request_read_file(self, mock_read):
        mock_read.return_value = "file content"
        args = {"action": "read_file", "path": "test.txt"}
        result = self.orchestrator.handle_orchestrator_request(args)

        mock_read.assert_called_once_with("test.txt")
        self.assertEqual(result, "file content")

    @patch("agent.orchestrator.list_directory")
    def test_handle_orchestrator_request_list_dir(self, mock_list):
        mock_list.return_value = ["file1.txt", "file2.txt"]
        args = {"action": "list_dir", "path": "."}
        result = self.orchestrator.handle_orchestrator_request(args)

        mock_list.assert_called_once_with(".")
        self.assertEqual(result, ["file1.txt", "file2.txt"])

    def test_handle_orchestrator_request_get_state(self):
        self.orchestrator.state = {"some": "state"}
        args = {"action": "get_state"}
        result = self.orchestrator.handle_orchestrator_request(args)

        self.assertEqual(result, json.dumps({"some": "state"}))

    @patch("agent.orchestrator.run_command")
    def test_handle_orchestrator_request_run_test(self, mock_run):
        mock_run.return_value = "test passed"
        args = {"action": "run_test", "command": "pytest"}
        result = self.orchestrator.handle_orchestrator_request(args)

        mock_run.assert_called_once_with("pytest")
        self.assertEqual(result, "test passed")

    def test_handle_orchestrator_request_unknown(self):
        args = {"action": "invalid"}
        result = self.orchestrator.handle_orchestrator_request(args)

        self.assertEqual(result, "Unknown orchestrator action: invalid")

if __name__ == "__main__":
    unittest.main()
