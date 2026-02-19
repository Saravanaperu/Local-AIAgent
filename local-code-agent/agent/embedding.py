import numpy as np
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import config

class GeminiEmbedder:
    def __init__(self, model_name):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model_name = model_name

    def encode(self, content, task_type="retrieval_document"):
        """
        Generates embeddings for content.
        Args:
            content: A string or a list of strings.
            task_type: The task type for embedding (e.g., "retrieval_document", "retrieval_query").
        Returns:
            A numpy array of embeddings.
        """
        if isinstance(content, str):
            result = genai.embed_content(
                model=self.model_name,
                content=content,
                task_type=task_type
            )
            return np.array(result['embedding'])
        elif isinstance(content, list):
            # Batch embedding
            result = genai.embed_content(
                model=self.model_name,
                content=content,
                task_type=task_type
            )
            return np.array(result['embedding'])
        else:
            raise ValueError("Content must be a string or a list of strings.")

class SentenceTransformerEmbedder:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)

    def encode(self, content, **kwargs):
        # SentenceTransformer encode doesn't use task_type, so we ignore kwargs
        return self.model.encode(content)

def get_embedding_model(model_name):
    if model_name.startswith("models/"):
        return GeminiEmbedder(model_name)
    else:
        return SentenceTransformerEmbedder(model_name)
