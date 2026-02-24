
import sys
import unittest
from unittest.mock import MagicMock, patch
import os

# Mock dependencies before they are imported by agent.indexer
mock_chromadb = MagicMock()
sys.modules["chromadb"] = mock_chromadb

mock_tsl = MagicMock()
sys.modules["tree_sitter_languages"] = mock_tsl

# Mock embedding model
mock_embedding_model = MagicMock()
mock_get_embedding_model = MagicMock(return_value=mock_embedding_model)
sys.modules["agent.embedding"] = MagicMock(get_embedding_model=mock_get_embedding_model)

# Set dummy API key for testing
os.environ["GEMINI_API_KEY"] = "fake_key_for_test"

# Add local-code-agent to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import config
from agent.indexer import extract_chunks

class TestIndexerSecurity(unittest.TestCase):
    def setUp(self):
        self.test_file = "large_test_file.py"
        # Create a file that exceeds MAX_FILE_SIZE
        with open(self.test_file, "wb") as f:
            f.write(b"a" * (config.MAX_FILE_SIZE + 1))

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    @patch("agent.indexer.get_parser_for_file")
    def test_extract_chunks_skips_large_file(self, mock_get_parser):
        # Mock parser so it doesn't return None
        mock_get_parser.return_value = (MagicMock(), MagicMock())

        # Call extract_chunks with the large file
        result = extract_chunks(self.test_file)

        # Verify it returns an empty list
        self.assertEqual(result, [])

    @patch("agent.indexer.get_parser_for_file")
    def test_extract_chunks_reads_small_file(self, mock_get_parser):
        # Create a small file
        small_file = "small_test_file.py"
        content = b"def hello(): pass"
        with open(small_file, "wb") as f:
            f.write(content)

        try:
            # Mock parser and language
            mock_parser = MagicMock()
            mock_language = MagicMock()
            mock_get_parser.return_value = (mock_parser, mock_language)

            # Mock tree-sitter objects
            mock_tree = MagicMock()
            mock_parser.parse.return_value = mock_tree
            mock_tree.root_node = MagicMock()

            # Mock query and captures
            mock_query = MagicMock()
            mock_language.query.return_value = mock_query
            mock_query.captures.return_value = [] # No chunks found, will add whole file

            # Call extract_chunks
            result = extract_chunks(small_file)

            # Verify it read the file (it should return one chunk for the whole file since captures is empty)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["text"], content.decode("utf-8"))

        finally:
            if os.path.exists(small_file):
                os.remove(small_file)

if __name__ == "__main__":
    unittest.main()
