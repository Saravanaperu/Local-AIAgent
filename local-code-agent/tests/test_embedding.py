import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock numpy
mock_np = MagicMock()
sys.modules["numpy"] = mock_np

# Mock google
mock_google = MagicMock()
sys.modules["google"] = mock_google

# Mock google.generativeai
mock_genai = MagicMock()
sys.modules["google.generativeai"] = mock_genai
# Ensure mock_google.generativeai points to the same mock
mock_google.generativeai = mock_genai

# Mock sentence_transformers
mock_sentence_transformers = MagicMock()
sys.modules["sentence_transformers"] = mock_sentence_transformers

# Add local-code-agent to path
import os
# Set dummy API key for testing
os.environ["GEMINI_API_KEY"] = "fake_key_for_test"

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

from agent.embedding import get_embedding_model, GeminiEmbedder, SentenceTransformerEmbedder

class TestEmbedding(unittest.TestCase):
    def setUp(self):
        mock_genai.reset_mock()
        mock_genai.embed_content.side_effect = None

        mock_sentence_transformers.reset_mock()
        mock_np.reset_mock()
        # Mock np.array to return the list so we can compare
        mock_np.array.side_effect = lambda x: x
        # Mock np.array_equal to compare lists
        mock_np.array_equal.side_effect = lambda x, y: x == y

    def test_get_embedding_model_gemini(self):
        model = get_embedding_model("models/text-embedding-004")
        self.assertIsInstance(model, GeminiEmbedder)
        self.assertEqual(model.model_name, "models/text-embedding-004")

    def test_get_embedding_model_sentence_transformer(self):
        model = get_embedding_model("all-MiniLM-L6-v2")
        self.assertIsInstance(model, SentenceTransformerEmbedder)

    def test_gemini_embedder_encode_single(self):
        mock_genai.embed_content.return_value = {"embedding": [0.1, 0.2, 0.3]}
        embedder = GeminiEmbedder("models/test")
        result = embedder.encode("test string")

        # result is now the list [0.1, 0.2, 0.3] because np.array is identity
        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_genai.embed_content.assert_called_with(
            model="models/test",
            content="test string",
            task_type="retrieval_document"
        )

    def test_gemini_embedder_encode_list(self):
        mock_genai.embed_content.side_effect = [
            {"embedding": [0.1, 0.1]},
            {"embedding": [0.2, 0.2]}
        ]
        embedder = GeminiEmbedder("models/test")
        result = embedder.encode(["doc1", "doc2"], task_type="retrieval_query")

        expected = [[0.1, 0.1], [0.2, 0.2]]
        self.assertEqual(result, expected)

        # Verify calls
        self.assertEqual(mock_genai.embed_content.call_count, 2)

        calls = mock_genai.embed_content.call_args_list
        # call is a tuple (args, kwargs)
        # but in python 3.8+ call object has kwargs attribute
        # mock_genai.embed_content.call_args_list returns a list of 'Call' objects
        # accessing kwargs attribute should work
        self.assertEqual(calls[0].kwargs['content'], "doc1")
        self.assertEqual(calls[0].kwargs['task_type'], "retrieval_query")
        self.assertEqual(calls[1].kwargs['content'], "doc2")
        self.assertEqual(calls[1].kwargs['task_type'], "retrieval_query")

    def test_sentence_transformer_embedder_encode(self):
        mock_model = MagicMock()
        mock_model.encode.return_value = [0.5, 0.6] # Mocked return
        mock_sentence_transformers.SentenceTransformer.return_value = mock_model

        embedder = SentenceTransformerEmbedder("model_name")
        result = embedder.encode("text")

        self.assertEqual(result, [0.5, 0.6])
        mock_model.encode.assert_called_with("text")

if __name__ == "__main__":
    unittest.main()
