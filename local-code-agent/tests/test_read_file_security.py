
import sys
import unittest
from unittest.mock import MagicMock
import os

# Mock chromadb
sys.modules["chromadb"] = MagicMock()
# Mock tree_sitter_languages
sys.modules["tree_sitter_languages"] = MagicMock()
# Mock google
sys.modules["google"] = MagicMock()
# Mock google.generativeai
sys.modules["google.generativeai"] = MagicMock()
# Mock numpy
sys.modules["numpy"] = MagicMock()
# Mock sentence_transformers
sys.modules["sentence_transformers"] = MagicMock()

# Set dummy API key for testing
os.environ["GEMINI_API_KEY"] = "fake_key_for_test"

# Add local-code-agent to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agent.tools import read_file
import config

class TestReadFileSecurity(unittest.TestCase):
    def setUp(self):
        self.large_file = os.path.join(project_root, "large_test_file.txt")
        # Create a file slightly larger than MAX_FILE_SIZE
        with open(self.large_file, "wb") as f:
            f.write(b"a" * (config.MAX_FILE_SIZE + 100))

    def tearDown(self):
        if os.path.exists(self.large_file):
            os.remove(self.large_file)

    def test_read_file_unbounded_read(self):
        # This should return an error message.
        result = read_file(self.large_file)

        self.assertTrue(result.startswith("Error:"), f"Expected error message, but got: {result[:100]}...")
        self.assertIn("too large", result)
        self.assertIn(str(config.MAX_FILE_SIZE), result)

    def test_read_file_normal_size(self):
        small_file = os.path.join(project_root, "small_test_file.txt")
        content = "Hello, world!"
        with open(small_file, "w") as f:
            f.write(content)

        try:
            result = read_file(small_file)
            self.assertEqual(result, content)
        finally:
            if os.path.exists(small_file):
                os.remove(small_file)

if __name__ == "__main__":
    unittest.main()
