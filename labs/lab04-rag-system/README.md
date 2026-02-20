# Lab 04: RAG System with Evaluation

## Objective
Build a complete RAG system for querying a codebase, including proper evaluation.

**Time Allotted**: 1 hour 45 minutes

## Learning Goals
- Implement a RAG pipeline from scratch
- Use appropriate chunking for code
- Build an evaluation framework
- Understand retrieval metrics

---

## Choose Your Language

| Aspect | Python | TypeScript |
|--------|--------|------------|
| Directory | `./python` | `./typescript` |
| Vector DB | ChromaDB | In-memory (OpenAI embeddings) |
| Embeddings | sentence-transformers / OpenAI | OpenAI API |
| Framework | FastAPI | Hono |

---

## What You'll Build

A codebase Q&A system that:
1. Indexes code files with embeddings
2. Retrieves relevant code for questions
3. Generates answers grounded in code
4. Evaluates retrieval and generation quality

```
┌─────────────────────────────────────────────────────────────┐
│                    Codebase RAG System                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INDEXING                                                   │
│  ────────                                                   │
│  Code Files → Chunk → Embed → Store (Vector DB)             │
│                                                             │
│  QUERYING                                                   │
│  ────────                                                   │
│  Question → Embed → Search → Retrieve → Generate Answer     │
│                                                             │
│  EVALUATION                                                 │
│  ──────────                                                 │
│  Test Questions → RAG → Compare to Ground Truth → Metrics   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Python Setup

```bash
cd python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set API key (OpenAI for embeddings, or use free sentence-transformers)
export OPENAI_API_KEY=your-key
# And for generation:
export ANTHROPIC_API_KEY=your-key

uvicorn main:app --reload
```

### TypeScript Setup

```bash
cd typescript
npm install

# OpenAI is required for embeddings
export OPENAI_API_KEY=your-key
export ANTHROPIC_API_KEY=your-key

npm run dev
```

---

## Step-by-Step Instructions

### Step 1: Implement Code Chunking (20 min)

<details>
<summary><b>Python</b></summary>

```python
# rag/chunker.py
from dataclasses import dataclass
from typing import List, Dict
import re

@dataclass
class CodeChunk:
    content: str
    metadata: Dict
    chunk_id: str

class CodeChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_file(self, content: str, filename: str) -> List[CodeChunk]:
        language = self._detect_language(filename)
        if language == "python":
            return self._chunk_python(content, filename)
        return self._chunk_generic(content, filename, language)

    def _chunk_python(self, content: str, filename: str) -> List[CodeChunk]:
        # Split by function/class definitions
        pattern = r'(^(?:def|class|async def)\s+\w+.*?)(?=\n(?:def|class|async def)|\Z)'
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        # ... return chunks
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// chunker.ts
interface CodeChunk {
  content: string;
  metadata: { filename: string; language: string; type: string; name?: string };
  chunkId: string;
}

class CodeChunker {
  constructor(
    private chunkSize: number = 1000,
    private chunkOverlap: number = 100
  ) {}

  chunkFile(content: string, filename: string): CodeChunk[] {
    const language = this.detectLanguage(filename);
    if (language === 'python') {
      return this.chunkPython(content, filename);
    }
    return this.chunkGeneric(content, filename, language);
  }

  private chunkPython(content: string, filename: string): CodeChunk[] {
    const pattern = /(^(?:def|class|async def)\s+\w+.*?)(?=\n(?:def|class|async def)|\Z)/gms;
    const matches = [...content.matchAll(pattern)];
    // ... return chunks
  }
}
```

</details>

### Step 2: Set Up Vector Store (15 min)

<details>
<summary><b>Python (ChromaDB)</b></summary>

```python
# rag/vector_store.py
import chromadb
from chromadb.utils import embedding_functions

class CodebaseVectorStore:
    def __init__(self, collection_name: str = "codebase"):
        self.client = chromadb.PersistentClient(path="./chroma_db")

        # OpenAI embeddings (or use sentence-transformers for free)
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def add_documents(self, documents, metadatas, ids):
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def query(self, query: str, n_results: int = 5):
        return self.collection.query(query_texts=[query], n_results=n_results)
```

</details>

<details>
<summary><b>TypeScript (In-Memory + OpenAI)</b></summary>

```typescript
// vector-store.ts
class OpenAIEmbeddings {
  async embed(texts: string[]): Promise<number[][]> {
    const response = await openai.embeddings.create({
      model: 'text-embedding-3-small',
      input: texts,
    });
    return response.data.map((d) => d.embedding);
  }
}

class InMemoryVectorStore {
  private documents = new Map<string, { content: string; embedding: number[] }>();

  async addDocuments(docs: string[], metadatas: any[], ids: string[]) {
    const embeddings = await this.embeddings.embed(docs);
    for (let i = 0; i < docs.length; i++) {
      this.documents.set(ids[i], { content: docs[i], embedding: embeddings[i] });
    }
  }

  async query(queryText: string, nResults: number = 5) {
    const [queryEmb] = await this.embeddings.embed([queryText]);
    // Calculate cosine similarity, sort, return top N
  }
}
```

</details>

### Step 3: Build RAG Pipeline (20 min)

<details>
<summary><b>Python</b></summary>

```python
# rag/pipeline.py
class CodebaseRAG:
    def __init__(self, llm_client, collection_name: str = "codebase"):
        self.llm = llm_client
        self.vector_store = CodebaseVectorStore(collection_name)
        self.chunker = CodeChunker()

    def index_files(self, files: Dict[str, str]) -> int:
        for filename, content in files.items():
            chunks = self.chunker.chunk_file(content, filename)
            self.vector_store.add_documents(
                [c.content for c in chunks],
                [c.metadata for c in chunks],
                [c.chunk_id for c in chunks]
            )
        return len(chunks)

    def query(self, question: str, n_results: int = 5) -> Dict:
        results = self.vector_store.query(question, n_results)
        context = self._build_context(results)

        answer = self.llm.chat([
            {"role": "system", "content": "Answer based on the code context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ])

        return {"answer": answer, "sources": results}
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// pipeline.ts
class CodebaseRAG {
  private vectorStore: InMemoryVectorStore;
  private chunker = new CodeChunker();

  constructor(private llm: LLMClient) {
    this.vectorStore = createVectorStore();
  }

  async indexFiles(files: Record<string, string>): Promise<number> {
    for (const [filename, content] of Object.entries(files)) {
      const chunks = this.chunker.chunkFile(content, filename);
      await this.vectorStore.addDocuments(
        chunks.map(c => c.content),
        chunks.map(c => c.metadata),
        chunks.map(c => c.chunkId)
      );
    }
    return chunks.length;
  }

  async query(question: string, nResults = 5): Promise<RAGResponse> {
    const results = await this.vectorStore.query(question, nResults);
    const context = this.buildContext(results);

    const answer = await this.llm.chat([
      { role: 'system', content: 'Answer based on the code context.' },
      { role: 'user', content: `Context:\n${context}\n\nQuestion: ${question}` }
    ]);

    return { answer, sources: results };
  }
}
```

</details>

### Step 4: Implement Evaluation (25 min)

<details>
<summary><b>Python</b></summary>

```python
# rag/evaluation.py
def precision_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    retrieved_k = retrieved[:k]
    return len(set(retrieved_k) & relevant) / k

def recall_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    retrieved_k = retrieved[:k]
    return len(set(retrieved_k) & relevant) / len(relevant)

def mrr(retrieved: List[str], relevant: Set[str]) -> float:
    for i, doc in enumerate(retrieved):
        if doc in relevant:
            return 1.0 / (i + 1)
    return 0.0

class RAGEvaluator:
    def evaluate_retrieval(self, examples, k=5) -> Dict:
        metrics = {'precision': [], 'recall': [], 'mrr': []}
        for ex in examples:
            result = self.rag.query(ex.question, k)
            retrieved = [s['file'] for s in result['sources']]
            # Calculate metrics...
        return averaged_metrics
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// evaluation.ts
function precisionAtK(retrieved: string[], relevant: Set<string>, k: number): number {
  const retrievedK = retrieved.slice(0, k);
  return retrievedK.filter(doc => relevant.has(doc)).length / k;
}

function recallAtK(retrieved: string[], relevant: Set<string>, k: number): number {
  const retrievedK = retrieved.slice(0, k);
  return retrievedK.filter(doc => relevant.has(doc)).length / relevant.size;
}

function mrr(retrieved: string[], relevant: Set<string>): number {
  for (let i = 0; i < retrieved.length; i++) {
    if (relevant.has(retrieved[i])) return 1 / (i + 1);
  }
  return 0;
}

class RAGEvaluator {
  async evaluateRetrieval(examples: EvalExample[], k = 5) {
    const metrics = { precision: [], recall: [], mrr: [] };
    for (const ex of examples) {
      const result = await this.rag.query(ex.question, k);
      const retrieved = result.sources.map(s => s.file);
      // Calculate metrics...
    }
    return averagedMetrics;
  }
}
```

</details>

### Step 5: Test the System (15 min)

```bash
# Index some files
curl -X POST http://localhost:8000/index/files \
  -H "Content-Type: application/json" \
  -d '{
    "files": {
      "auth.py": "def login(user, password):\n    # Validate credentials\n    return token",
      "api.py": "def get_users():\n    return db.query(User).all()"
    }
  }'

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How does login work?"}'

# Evaluate
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "examples": [{
      "question": "How does login work?",
      "expected_answer": "Login validates credentials and returns a token",
      "relevant_files": ["auth.py"]
    }]
  }'
```

---

## Project Structure

```
lab04-rag-system/
├── README.md
├── python/
│   ├── main.py              # FastAPI application
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── vector_store.py  # ChromaDB wrapper
│   │   ├── chunker.py       # Code chunking
│   │   ├── pipeline.py      # RAG pipeline
│   │   └── evaluation.py    # Evaluation metrics
│   └── requirements.txt
└── typescript/
    ├── src/
    │   ├── index.ts         # Hono application
    │   ├── vector-store.ts  # In-memory + OpenAI
    │   ├── chunker.ts       # Code chunking
    │   ├── pipeline.ts      # RAG pipeline
    │   ├── evaluation.ts    # Evaluation metrics
    │   ├── llm-client.ts
    │   └── types.ts
    ├── package.json
    └── tsconfig.json
```

---

## Key Differences: Python vs TypeScript

| Aspect | Python | TypeScript |
|--------|--------|------------|
| Vector DB | ChromaDB (persistent) | In-memory (demo) |
| Embeddings | sentence-transformers (free) or OpenAI | OpenAI API only |
| Production | Use ChromaDB/Pinecone | Use Pinecone/Weaviate |

**Note**: The TypeScript implementation uses an in-memory vector store for simplicity. For production, use Pinecone (`@pinecone-database/pinecone`) or Weaviate (`weaviate-ts-client`).

---

## Deliverables

- [ ] Working RAG system with code indexing
- [ ] Smart code-aware chunking
- [ ] Evaluation framework with retrieval metrics
- [ ] LLM-as-judge generation evaluation
- [ ] Deployed to Railway/Vercel
- [ ] Evaluation dataset (10+ examples)

---

## Extension Challenges

1. **Hybrid Search**: Add BM25 keyword search alongside vector search
2. **Reranking**: Add a reranking step to improve retrieval
3. **Caching**: Cache embeddings and query results
4. **Multiple Codebases**: Support querying across multiple indexed repos

---

**Next**: [Lab 05 - Multi-Agent Orchestration](../lab05-multi-agent/)
