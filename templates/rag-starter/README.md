# RAG Starter Template

A minimal Retrieval-Augmented Generation (RAG) system for beginners. This template provides a simple, easy-to-understand implementation of RAG using FastAPI and OpenAI.

## Overview

This is a simplified RAG implementation that:
- Uses in-memory vector storage (no database required)
- Implements basic cosine similarity for retrieval
- Supports document indexing and querying
- Provides a REST API for easy integration

Perfect for learning RAG fundamentals before moving to production systems.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Features

- **In-Memory Vector Store**: Simple numpy-based storage with cosine similarity
- **Fixed-Size Chunking**: Basic text chunking for document processing
- **OpenAI Embeddings**: Uses `text-embedding-3-small` model
- **REST API**: Three simple endpoints for indexing, querying, and health checks
- **No Database Required**: Everything runs in memory for simplicity

## API Endpoints

### POST /index

Index documents or code for later retrieval.

**Request Body:**
```json
{
  "documents": [
    {
      "id": "doc1",
      "content": "Your document content here",
      "metadata": {
        "source": "file.txt",
        "type": "documentation"
      }
    }
  ]
}
```

**Response:**
```json
{
  "indexed_count": 3,
  "total_chunks": 15
}
```

### POST /query

Query indexed documents using natural language.

**Request Body:**
```json
{
  "question": "How do I configure the system?",
  "top_k": 3
}
```

**Response:**
```json
{
  "answer": "Based on the documentation...",
  "sources": [
    {
      "id": "doc1_chunk_0",
      "content": "Configuration section...",
      "similarity": 0.89,
      "metadata": {
        "source": "config.txt"
      }
    }
  ],
  "context_used": "Configuration section..."
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "indexed_chunks": 15
}
```

## Configuration

Edit `.env` file:

```bash
# Required
OPENAI_API_KEY=your_api_key_here

# Optional
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

## Usage Example

```python
import requests

# Index documents
response = requests.post("http://localhost:8000/index", json={
    "documents": [
        {
            "id": "python_guide",
            "content": "Python is a high-level programming language...",
            "metadata": {"source": "python_guide.txt"}
        }
    ]
})

# Query
response = requests.post("http://localhost:8000/query", json={
    "question": "What is Python?",
    "top_k": 3
})

print(response.json()["answer"])
```

## How It Works

1. **Indexing**: Documents are split into fixed-size chunks with overlap
2. **Embedding**: Each chunk is converted to a vector using OpenAI embeddings
3. **Storage**: Vectors are stored in-memory with numpy arrays
4. **Retrieval**: Queries are embedded and matched using cosine similarity
5. **Generation**: Top-k chunks are sent to LLM for answer generation

## Deployment

### Local Development
```bash
python main.py
```

### Production (Docker)
```bash
docker build -t rag-starter .
docker run -p 8000:8000 --env-file .env rag-starter
```

### Production (Cloud)
```bash
# Deploy to any cloud platform that supports Python
# Ensure OPENAI_API_KEY is set in environment variables
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Extending This Template

This is a starter template. For production use, consider:

- **Persistent Storage**: Replace in-memory store with ChromaDB, Pinecone, or Weaviate
- **Better Chunking**: Use semantic chunking or code-aware chunking
- **Hybrid Search**: Combine vector search with keyword search (BM25)
- **Evaluation**: Add retrieval metrics (precision, recall, MRR)
- **Caching**: Cache embeddings to reduce API costs
- **Authentication**: Add API key authentication
- **Rate Limiting**: Prevent abuse

See `/labs/lab04-rag-system` for a more advanced implementation.

## Limitations

- **In-Memory Only**: Data is lost when server restarts
- **No Persistence**: Not suitable for production use
- **Simple Chunking**: Fixed-size chunks may split logical units
- **No Hybrid Search**: Only uses semantic similarity
- **Limited Scale**: Performance degrades with large document sets

## License

MIT - Use freely for learning and prototyping
