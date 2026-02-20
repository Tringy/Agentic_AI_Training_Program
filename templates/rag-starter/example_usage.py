"""
Example Usage - RAG Starter Template
Demonstrates how to use the RAG API.
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"


def main():
    print("RAG Starter - Example Usage\n")

    # 1. Check health
    print("1. Checking API health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.json()}")
    print()

    # 2. Index some documents
    print("2. Indexing documents...")
    documents = [
        {
            "id": "python_intro",
            "content": """Python is a high-level, interpreted programming language known for its simplicity and readability.
            It was created by Guido van Rossum and first released in 1991. Python supports multiple programming paradigms,
            including procedural, object-oriented, and functional programming. It has a comprehensive standard library
            and a large ecosystem of third-party packages.""",
            "metadata": {"source": "python_guide.txt", "topic": "introduction"}
        },
        {
            "id": "python_uses",
            "content": """Python is widely used in various domains including web development, data science, machine learning,
            artificial intelligence, automation, and scientific computing. Popular frameworks include Django and Flask for
            web development, NumPy and Pandas for data analysis, and TensorFlow and PyTorch for machine learning.""",
            "metadata": {"source": "python_guide.txt", "topic": "applications"}
        },
        {
            "id": "rag_concept",
            "content": """Retrieval-Augmented Generation (RAG) is a technique that enhances large language models by
            retrieving relevant information from a knowledge base before generating responses. This approach combines
            the benefits of retrieval systems and generative models, enabling more accurate and contextual answers.""",
            "metadata": {"source": "rag_guide.txt", "topic": "concepts"}
        }
    ]

    response = requests.post(f"{BASE_URL}/index", json={"documents": documents})
    print(f"   Result: {json.dumps(response.json(), indent=2)}")
    print()

    # 3. Query the system
    print("3. Querying the RAG system...")
    queries = [
        "What is Python used for?",
        "Who created Python?",
        "What is RAG?"
    ]

    for query in queries:
        print(f"\n   Question: {query}")
        response = requests.post(
            f"{BASE_URL}/query",
            json={"question": query, "top_k": 2}
        )
        result = response.json()

        print(f"   Answer: {result['answer']}")
        print(f"   Sources: {len(result['sources'])} chunks retrieved")
        print(f"   Top similarity: {result['sources'][0]['similarity']}")

    print("\n4. Final health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.json()}")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API.")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"Error: {e}")
