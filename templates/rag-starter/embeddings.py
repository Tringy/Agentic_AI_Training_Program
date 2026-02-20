"""
Embedding utilities for RAG system.
Simple functions for getting embeddings and calculating similarity.
"""
import numpy as np
from typing import List


def get_embedding(
    openai_client,
    text: str,
    model: str = "text-embedding-3-small"
) -> List[float]:
    """
    Get embedding vector for text using OpenAI.

    Args:
        openai_client: OpenAI client instance
        text: Text to embed
        model: Embedding model to use

    Returns:
        Embedding vector as list of floats
    """
    # Replace newlines with spaces for better embeddings
    text = text.replace("\n", " ")

    response = openai_client.embeddings.create(
        model=model,
        input=[text]
    )

    return response.data[0].embedding


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Cosine similarity measures the cosine of the angle between two vectors.
    Returns a value between -1 and 1, where 1 means identical direction.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity score (0 to 1)
    """
    # Convert to numpy arrays
    a = np.array(vec1)
    b = np.array(vec2)

    # Calculate cosine similarity
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    similarity = dot_product / (norm_a * norm_b)

    return float(similarity)
