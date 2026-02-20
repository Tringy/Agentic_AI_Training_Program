# Day 4: RAG (Retrieval-Augmented Generation) & Evaluation

## Learning Objectives

By the end of Day 4, you will be able to:
- Explain how RAG systems work and when to use them
- Implement effective chunking and embedding strategies
- Identify and avoid common RAG pitfalls
- Build evaluation frameworks for AI systems
- Implement comprehensive testing strategies for AI systems
- Debug and observe AI system behavior
- Deploy a complete RAG system with evaluation

---

## Table of Contents

1. [RAG Fundamentals](#rag-fundamentals)
2. [Chunking Strategies](#chunking)
3. [RAG Pitfalls & Advanced Patterns](#pitfalls)
4. [Exercise 1: RAG Architecture Design](#exercise-1)
5. [Evaluation Fundamentals](#evaluation)
6. [Debugging & Observability](#observability)
7. [Lab 04: Build & Evaluate RAG System](#lab-04)

---

<a name="rag-fundamentals"></a>
## 1. RAG Fundamentals (1 hour)

### 1.1 What is RAG?

**Retrieval-Augmented Generation (RAG)** combines information retrieval with LLM generation to ground responses in specific data. It's the most important pattern for building practical AI applications.

**The core problem RAG solves:**
LLMs are trained on general internet data up to a cutoff date. They don't know about:
- Your company's internal documents
- Recent events after their training cutoff
- Your specific product documentation
- Customer data in your database
- Proprietary information

**Without RAG:**
- User: "What's our return policy?"
- LLM: "I don't have access to your specific return policy..." (hallucination risk high)

**With RAG:**
- System retrieves: Your actual return policy document from database
- System combines: Retrieved policy + user question in prompt
- LLM: "Based on your return policy, customers can return items within 30 days..." (grounded in your data)

**Real-world business value:**
- **Customer support**: Answer questions using your knowledge base instead of generic responses
- **Internal documentation**: Employees get accurate answers from company docs
- **Compliance**: Legal/medical systems that must cite sources
- **Product recommendations**: Match products to customer needs using your catalog

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAG Pipeline                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INDEXING PHASE (Offline)                                       │
│  ─────────────────────────                                      │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌───────────┐     │
│  │Documents │──▶│  Chunk   │──▶│  Embed   │──▶│  Store    │     │
│  │          │   │          │   │          │   │(Vector DB)│     │
│  └──────────┘   └──────────┘   └──────────┘   └───────────┘     │
│                                                                 │
│  QUERY PHASE (Online)                                           │
│  ────────────────────                                           │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐      │
│  │  Query   │──▶│  Embed   │──▶│ Retrieve │──▶│   LLM    │      │
│  │          │   │  Query   │   │ Similar  │   │ Generate │      │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘      │
│                                     │                           │
│                                     ▼                           │
│                              Top-K Documents                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Why RAG?

| Problem | Without RAG | With RAG |
|---------|-------------|----------|
| **Knowledge Cutoff** | LLM knows only training data | Access to current/custom data |
| **Hallucinations** | Makes up facts | Grounded in source documents |
| **Domain Specificity** | Generic knowledge | Your company's data |
| **Updatability** | Retrain entire model | Update index only |
| **Traceability** | Can't cite sources | Can point to exact source |

### 1.3 When to Use RAG

```markdown
## RAG Decision Guide

Use RAG when:
✅ Need access to private/proprietary data
✅ Data changes frequently
✅ Need to cite sources
✅ Domain-specific knowledge required
✅ Want to reduce hallucinations with factual grounding

Don't use RAG when:
❌ General knowledge questions (use base LLM)
❌ Data fits entirely in context window
❌ Real-time data needed (use function calling)
❌ Reasoning over structured data (use SQL/code)
❌ Simple classification tasks
```

### 1.4 Embeddings Explained

Embeddings convert text to dense vectors (lists of numbers) that capture semantic meaning. This is the "magic" that makes RAG work.

**What embeddings actually mean:**

Think of embeddings as coordinates in "meaning space." Similar meanings = nearby coordinates.

- "dog" might be at coordinates [0.2, 0.8, 0.1, ...]
- "puppy" might be at coordinates [0.22, 0.79, 0.09, ...] (very close!)
- "car" might be at coordinates [0.9, 0.1, 0.7, ...] (far away)

**Why this matters for search:**
Traditional search: "reset password" won't find documents about "changing your login credentials" (different words)
Embedding search: Understands these mean the same thing, finds the right document

**Real example:**
```
User query: "How do I change my login?"

Traditional keyword search:
❌ Misses: "Reset your password" (no matching words)
❌ Misses: "Update credentials" (no matching words)

Embedding search:
✅ Finds: "Reset your password" (semantically similar)
✅ Finds: "Update credentials" (semantically similar)
✅ Finds: "Forgot password recovery" (semantically similar)
```

**How it works in RAG:**
1. Convert all your documents to embeddings (do once, store in vector database)
2. Convert user's question to an embedding (do every query)
3. Find documents whose embeddings are "close" to the question embedding
4. Send those documents + question to LLM

**The math (simplified):**
Embeddings are typically 1000-3000 dimensional vectors. "Closeness" is measured by cosine similarity:
- 1.0 = identical meaning
- 0.7-0.9 = very similar
- 0.3-0.6 = somewhat related
- 0.0-0.2 = unrelated

<details>
<summary><b>Python</b></summary>

```python
# embeddings/basics.py
"""Understanding embeddings."""
import numpy as np
from typing import List

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Example: Similar sentences have similar embeddings
sentences = [
    "How do I reset my password?",
    "I forgot my password and need to change it",
    "What are your business hours?",
    "When is the store open?",
]

# After embedding, similarities would be:
# "reset password" ↔ "forgot password": ~0.92 (very similar)
# "reset password" ↔ "business hours": ~0.23 (not similar)
# "business hours" ↔ "store open": ~0.88 (very similar)
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// embeddings/basics.ts
/**
 * Calculate cosine similarity between two vectors.
 */
function cosineSimilarity(a: number[], b: number[]): number {
  const dotProduct = a.reduce((sum, val, i) => sum + val * b[i], 0);
  const magnitudeA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
  const magnitudeB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0));
  return dotProduct / (magnitudeA * magnitudeB);
}

// Example: Similar sentences have similar embeddings
const sentences = [
  'How do I reset my password?',
  'I forgot my password and need to change it',
  'What are your business hours?',
  'When is the store open?',
];

// After embedding, similarities would be:
// "reset password" ↔ "forgot password": ~0.92 (very similar)
// "reset password" ↔ "business hours": ~0.23 (not similar)
// "business hours" ↔ "store open": ~0.88 (very similar)
```

</details>

**Embedding Models Comparison:**

| Model | Dimensions | Speed | Quality | Cost |
|-------|------------|-------|---------|------|
| OpenAI text-embedding-3-small | 1536 | Fast | Good | $0.02/1M tokens |
| OpenAI text-embedding-3-large | 3072 | Medium | Excellent | $0.13/1M tokens |
| Voyage-3 | 1024 | Fast | Excellent | $0.06/1M tokens |
| Cohere embed-v3 | 1024 | Fast | Excellent | $0.10/1M tokens |
| BGE-large (local) | 1024 | Varies | Good | Free |

### 1.5 Vector Databases Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Vector Database Options                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  LIGHTWEIGHT (Good for getting started)                         │
│  • ChromaDB - Simple, local, great for prototyping              │
│  • LanceDB - Local, integrated with pandas/arrow                │
│  • SQLite + extension - Minimal infrastructure                  │
│                                                                 │
│  PRODUCTION SCALE                                               │
│  • Pinecone - Managed, fast, scales well                        │
│  • Weaviate - Open source, feature-rich                         │
│  • Qdrant - Open source, fast, Rust-based                       │
│  • Milvus - Open source, very scalable                          │
│                                                                 │
│  EXISTING INFRASTRUCTURE                                        │
│  • PostgreSQL + pgvector - If you already use Postgres          │
│  • Elasticsearch - If you already use ES                        │
│  • Redis - If you already use Redis                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.6 Basic RAG Implementation

<details>
<summary><b>Python</b></summary>

```python
# rag/basic_rag.py
"""Simple RAG implementation."""
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions

class SimpleRAG:
    """Basic RAG system using ChromaDB."""

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_model: str = "text-embedding-3-small"
    ):
        # Initialize ChromaDB
        self.client = chromadb.Client()

        # Use OpenAI embeddings
        self.ef = embedding_functions.OpenAIEmbeddingFunction(
            model_name=embedding_model
        )

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.ef
        )

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict] = None,
        ids: List[str] = None
    ):
        """Add documents to the index."""
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Query the index and return relevant documents."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        # Format results
        formatted = []
        for i in range(len(results['documents'][0])):
            formatted.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if results['distances'] else None,
                'id': results['ids'][0][i]
            })

        return formatted

    def generate_response(self, query: str, llm_client, n_results: int = 5) -> str:
        """Full RAG pipeline: retrieve + generate."""
        relevant_docs = self.query(query, n_results)

        context = "\n\n---\n\n".join([
            f"Source: {doc['metadata'].get('source', 'Unknown')}\n{doc['content']}"
            for doc in relevant_docs
        ])

        prompt = f"""Answer the question based on the provided context.
If the context doesn't contain the answer, say so.

Context:
{context}

Question: {query}

Answer:"""

        response = llm_client.chat([
            {"role": "system", "content": "You answer questions based on provided context."},
            {"role": "user", "content": prompt}
        ])

        return response
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// rag/basic-rag.ts
import OpenAI from 'openai';

interface Document {
  content: string;
  metadata: Record<string, any>;
  id: string;
}

interface SearchResult extends Document {
  similarity: number;
}

/**
 * Simple RAG system using in-memory vector store + OpenAI embeddings.
 * For production, use Pinecone, Weaviate, or similar.
 */
class SimpleRAG {
  private documents: Map<string, { content: string; embedding: number[]; metadata: Record<string, any> }> = new Map();
  private openai: OpenAI;

  constructor(private embeddingModel: string = 'text-embedding-3-small') {
    this.openai = new OpenAI();
  }

  async addDocuments(
    documents: string[],
    metadatas: Record<string, any>[] = [],
    ids?: string[]
  ): Promise<void> {
    const docIds = ids || documents.map((_, i) => `doc_${i}`);

    // Get embeddings for all documents
    const response = await this.openai.embeddings.create({
      model: this.embeddingModel,
      input: documents,
    });

    // Store documents with embeddings
    for (let i = 0; i < documents.length; i++) {
      this.documents.set(docIds[i], {
        content: documents[i],
        embedding: response.data[i].embedding,
        metadata: metadatas[i] || {},
      });
    }
  }

  async query(query: string, nResults: number = 5): Promise<SearchResult[]> {
    // Embed query
    const response = await this.openai.embeddings.create({
      model: this.embeddingModel,
      input: [query],
    });
    const queryEmbedding = response.data[0].embedding;

    // Calculate similarities
    const results: SearchResult[] = [];
    for (const [id, doc] of this.documents) {
      const similarity = this.cosineSimilarity(queryEmbedding, doc.embedding);
      results.push({
        id,
        content: doc.content,
        metadata: doc.metadata,
        similarity,
      });
    }

    // Sort by similarity and return top N
    return results.sort((a, b) => b.similarity - a.similarity).slice(0, nResults);
  }

  async generateResponse(
    query: string,
    llmClient: { chat: (msgs: any[]) => Promise<string> },
    nResults: number = 5
  ): Promise<string> {
    const relevantDocs = await this.query(query, nResults);

    const context = relevantDocs
      .map((doc) => `Source: ${doc.metadata.source || 'Unknown'}\n${doc.content}`)
      .join('\n\n---\n\n');

    const prompt = `Answer the question based on the provided context.
If the context doesn't contain the answer, say so.

Context:
${context}

Question: ${query}

Answer:`;

    return llmClient.chat([
      { role: 'system', content: 'You answer questions based on provided context.' },
      { role: 'user', content: prompt },
    ]);
  }

  private cosineSimilarity(a: number[], b: number[]): number {
    const dotProduct = a.reduce((sum, val, i) => sum + val * b[i], 0);
    const magnitudeA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
    const magnitudeB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0));
    return dotProduct / (magnitudeA * magnitudeB);
  }
}
```

</details>

---

<a name="chunking"></a>
## 2. Chunking Strategies (1 hour)

### 2.1 Why Chunking Matters

**Chunking is how you split documents into pieces for embeddings.** Getting this wrong is the #1 reason RAG systems fail.

**The Goldilocks problem:** Chunks must be "just right"—not too small, not too large.

**Real-world example to understand the problem:**

Imagine you're building a customer support RAG system for a software product. Your documentation has this information:

```
Full document (2,000 words):
"Our product supports integration with Slack, GitHub, and Jira.
The Slack integration allows you to receive notifications when builds complete.
To set up Slack integration, go to Settings > Integrations > Slack.
Click 'Connect to Slack' and authorize our app.
Once connected, you can configure which events trigger notifications.
... [1,950 more words about other features]"
```

**Scenario: User asks "How do I set up Slack notifications?"**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Chunking Impact                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TOO SMALL (50 char chunks)                                     │
│  ────────────────────────────                                   │
│  ┌──────────────────┐                                           │
│  │ "Our product     │  ← Missing context                        │
│  │ supports"        │                                           │
│  └──────────────────┘                                           │
│  ┌──────────────────┐                                           │
│  │ "integration with│  ← Fragments meaning                      │
│  │ Slack, GitHub"   │                                           │
│  └──────────────────┘                                           │
│  ┌──────────────────┐                                           │
│  │ "and Jira. The"  │  ← Incomplete sentences                   │
│  └──────────────────┘                                           │
│                                                                 │
│  Problems:                                                      │
│  ❌ No chunk contains complete answer                           │
│  ❌ "Slack" appears in many chunks → many irrelevant matches    │
│  ❌ Context is fragmented → LLM can't understand                │
│                                                                 │
│  JUST RIGHT (200-500 char chunks)                               │
│  ─────────────────────────────                                  │
│  ┌───────────────────────────────────┐                          │
│  │ "The Slack integration allows you │                          │
│  │ to receive notifications when     │                          │
│  │ builds complete. To set up Slack  │                          │
│  │ integration, go to Settings >     │                          │
│  │ Integrations > Slack. Click       │                          │
│  │ 'Connect to Slack' and authorize  │                          │
│  │ our app. Once connected, you can  │                          │
│  │ configure which events trigger    │                          │
│  │ notifications."                   │                          │
│  └───────────────────────────────────┘                          │
│                                                                 │
│  Benefits:                                                      │
│  ✅ Complete, self-contained answer                             │
│  ✅ Embeddings capture full semantic meaning                    │
│  ✅ LLM can use this directly to answer                         │
│                                                                 │
│  TOO LARGE (entire 2,000-word document)                         │
│  ───────────────────────────────────                            │
│  ┌─────────────────────────────────────────────────┐            │
│  │ [Entire documentation including:                │            │
│  │  - Company history                              │            │
│  │  - Product overview                             │            │
│  │  - Slack integration (buried in middle)         │            │
│  │  - GitHub integration                           │            │
│  │  - Jira integration                             │            │
│  │  - Pricing                                      │            │
│  │  - Legal terms                                  │            │
│  │  - FAQs...]                                     │            │
│  └─────────────────────────────────────────────────┘            │
│                                                                 │
│  Problems:                                                      │
│  ❌ Exceeds context window (can't fit multiple chunks)          │
│  ❌ Relevant info is diluted by irrelevant content              │
│  ❌ Higher costs (more tokens to process)                       │
│  ❌ "Lost in the middle" problem (LLM misses key info)          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Key takeaway:** Chunk size should be **one complete thought** or **one self-contained piece of information**—typically 200-1000 tokens (150-750 words).

### 2.2 Chunking Strategies

**Strategy 1: Fixed-Size Chunking**

<details>
<summary><b>Python</b></summary>

```python
# chunking/fixed_size.py
from typing import List

def fixed_size_chunks(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """Split text into fixed-size chunks with overlap."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Find a good break point (sentence boundary)
        if end < len(text):
            for sep in ['. ', '.\n', '\n\n']:
                last_sep = text[start:end].rfind(sep)
                if last_sep > chunk_size * 0.5:
                    end = start + last_sep + len(sep)
                    break

        chunks.append(text[start:end].strip())
        start = end - overlap

    return chunks
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// chunking/fixed-size.ts

function fixedSizeChunks(
  text: string,
  chunkSize: number = 500,
  overlap: number = 50
): string[] {
  const chunks: string[] = [];
  let start = 0;

  while (start < text.length) {
    let end = start + chunkSize;

    // Find a good break point (sentence boundary)
    if (end < text.length) {
      for (const sep of ['. ', '.\n', '\n\n']) {
        const lastSep = text.slice(start, end).lastIndexOf(sep);
        if (lastSep > chunkSize * 0.5) {
          end = start + lastSep + sep.length;
          break;
        }
      }
    }

    chunks.push(text.slice(start, end).trim());
    start = end - overlap;
  }

  return chunks;
}
```

</details>

**Strategy 2: Semantic Chunking**

<details>
<summary><b>Python</b></summary>

```python
# chunking/semantic.py
from typing import List
import numpy as np

def semantic_chunks(
    text: str,
    embedding_func,
    similarity_threshold: float = 0.8,
    min_chunk_size: int = 100
) -> List[str]:
    """Split text based on semantic similarity between sentences."""
    import re

    sentences = re.split(r'(?<=[.!?])\s+', text)
    if not sentences:
        return [text]

    embeddings = [embedding_func(s) for s in sentences]

    chunks = []
    current_chunk = [sentences[0]]
    current_embedding = embeddings[0]

    for i in range(1, len(sentences)):
        similarity = cosine_similarity(current_embedding, embeddings[i])

        if similarity > similarity_threshold:
            current_chunk.append(sentences[i])
            current_embedding = np.mean([current_embedding, embeddings[i]], axis=0)
        else:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text) >= min_chunk_size:
                chunks.append(chunk_text)
            current_chunk = [sentences[i]]
            current_embedding = embeddings[i]

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// chunking/semantic.ts

function cosineSimilarity(a: number[], b: number[]): number {
  const dot = a.reduce((sum, val, i) => sum + val * b[i], 0);
  const magA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
  const magB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0));
  return dot / (magA * magB);
}

async function semanticChunks(
  text: string,
  embeddingFunc: (text: string) => Promise<number[]>,
  similarityThreshold: number = 0.8,
  minChunkSize: number = 100
): Promise<string[]> {
  const sentences = text.split(/(?<=[.!?])\s+/);
  if (sentences.length === 0) return [text];

  const embeddings = await Promise.all(sentences.map(s => embeddingFunc(s)));

  const chunks: string[] = [];
  let currentChunk = [sentences[0]];
  let currentEmbedding = embeddings[0];

  for (let i = 1; i < sentences.length; i++) {
    const similarity = cosineSimilarity(currentEmbedding, embeddings[i]);

    if (similarity > similarityThreshold) {
      currentChunk.push(sentences[i]);
      // Average embeddings
      currentEmbedding = currentEmbedding.map(
        (val, idx) => (val + embeddings[i][idx]) / 2
      );
    } else {
      const chunkText = currentChunk.join(' ');
      if (chunkText.length >= minChunkSize) {
        chunks.push(chunkText);
      }
      currentChunk = [sentences[i]];
      currentEmbedding = embeddings[i];
    }
  }

  if (currentChunk.length > 0) {
    chunks.push(currentChunk.join(' '));
  }

  return chunks;
}
```

</details>

**Strategy 3: Structure-Aware Chunking (for Code)**

<details>
<summary><b>Python</b></summary>

```python
# chunking/code_aware.py
from typing import List, Dict
import ast
import re

def chunk_python_code(code: str) -> List[Dict[str, str]]:
    """Chunk Python code by logical units (classes, functions)."""
    chunks = []

    try:
        tree = ast.parse(code)
    except SyntaxError:
        # Fall back to regex-based chunking
        return chunk_code_regex(code)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            chunk = {
                'type': 'function',
                'name': node.name,
                'content': ast.get_source_segment(code, node),
                'line_start': node.lineno,
                'line_end': node.end_lineno
            }
            chunks.append(chunk)

        elif isinstance(node, ast.ClassDef):
            chunk = {
                'type': 'class',
                'name': node.name,
                'content': ast.get_source_segment(code, node),
                'line_start': node.lineno,
                'line_end': node.end_lineno
            }
            chunks.append(chunk)

    # Handle module-level code
    # ... (implementation details)

    return chunks

def chunk_code_regex(code: str) -> List[Dict[str, str]]:
    """Fallback: chunk code using regex patterns."""
    patterns = {
        'python_func': r'(def \w+\([^)]*\):.*?)(?=\ndef |\nclass |\Z)',
        'python_class': r'(class \w+.*?:.*?)(?=\nclass |\Z)',
        'js_func': r'(function \w+\([^)]*\)\s*{.*?})',
    }
    # ... implementation
    pass
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// chunking/code-aware.ts
import * as ts from 'typescript';

interface CodeChunk {
  type: 'function' | 'class' | 'interface' | 'module';
  name: string;
  content: string;
  lineStart: number;
  lineEnd: number;
}

function chunkTypeScriptCode(code: string): CodeChunk[] {
  const chunks: CodeChunk[] = [];
  const sourceFile = ts.createSourceFile(
    'temp.ts',
    code,
    ts.ScriptTarget.Latest,
    true
  );

  function visit(node: ts.Node) {
    if (ts.isFunctionDeclaration(node) && node.name) {
      const { line: startLine } = sourceFile.getLineAndCharacterOfPosition(node.getStart());
      const { line: endLine } = sourceFile.getLineAndCharacterOfPosition(node.getEnd());
      chunks.push({
        type: 'function',
        name: node.name.text,
        content: node.getText(sourceFile),
        lineStart: startLine + 1,
        lineEnd: endLine + 1,
      });
    } else if (ts.isClassDeclaration(node) && node.name) {
      const { line: startLine } = sourceFile.getLineAndCharacterOfPosition(node.getStart());
      const { line: endLine } = sourceFile.getLineAndCharacterOfPosition(node.getEnd());
      chunks.push({
        type: 'class',
        name: node.name.text,
        content: node.getText(sourceFile),
        lineStart: startLine + 1,
        lineEnd: endLine + 1,
      });
    } else if (ts.isInterfaceDeclaration(node)) {
      const { line: startLine } = sourceFile.getLineAndCharacterOfPosition(node.getStart());
      const { line: endLine } = sourceFile.getLineAndCharacterOfPosition(node.getEnd());
      chunks.push({
        type: 'interface',
        name: node.name.text,
        content: node.getText(sourceFile),
        lineStart: startLine + 1,
        lineEnd: endLine + 1,
      });
    }
    ts.forEachChild(node, visit);
  }

  visit(sourceFile);
  return chunks;
}

// Fallback: Regex-based chunking for any language
function chunkCodeRegex(code: string, language: 'typescript' | 'python'): CodeChunk[] {
  const patterns: Record<string, RegExp> = {
    typescript_func: /(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)[^{]*\{[\s\S]*?\n\}/gm,
    typescript_class: /(?:export\s+)?class\s+(\w+)[\s\S]*?\n\}/gm,
    python_func: /def\s+(\w+)\s*\([^)]*\):[\s\S]*?(?=\ndef|\nclass|\n\S|\Z)/gm,
    python_class: /class\s+(\w+)[\s\S]*?(?=\nclass|\n\S|\Z)/gm,
  };

  const chunks: CodeChunk[] = [];
  const funcPattern = patterns[`${language}_func`];
  const classPattern = patterns[`${language}_class`];

  let match;
  while ((match = funcPattern.exec(code)) !== null) {
    chunks.push({
      type: 'function',
      name: match[1],
      content: match[0],
      lineStart: code.slice(0, match.index).split('\n').length,
      lineEnd: code.slice(0, match.index + match[0].length).split('\n').length,
    });
  }

  while ((match = classPattern.exec(code)) !== null) {
    chunks.push({
      type: 'class',
      name: match[1],
      content: match[0],
      lineStart: code.slice(0, match.index).split('\n').length,
      lineEnd: code.slice(0, match.index + match[0].length).split('\n').length,
    });
  }

  return chunks;
}
```

</details>

### 2.3 Chunking Best Practices

```markdown
## Chunking Checklist

### General Guidelines
- [ ] Chunk size: 200-1000 tokens (depends on embedding model)
- [ ] Overlap: 10-20% to maintain context
- [ ] Preserve sentence/paragraph boundaries
- [ ] Include relevant metadata with each chunk

### For Code
- [ ] Chunk by logical units (functions, classes)
- [ ] Include function signatures in metadata
- [ ] Preserve import statements context
- [ ] Consider including docstrings as separate chunks

### For Documentation
- [ ] Respect heading hierarchy
- [ ] Keep related sections together
- [ ] Include heading context in each chunk
- [ ] Handle tables and lists carefully

### For Conversations/Logs
- [ ] Group by conversation turns
- [ ] Include timestamp metadata
- [ ] Consider speaker/role information
```

### 2.4 Adding Metadata

<details>
<summary><b>Python</b></summary>

```python
# chunking/metadata.py
from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime

@dataclass
class ChunkMetadata:
    """Metadata to store with each chunk."""
    source: str                    # File path or document ID
    chunk_index: int               # Position in original document
    total_chunks: int              # Total chunks from this source
    created_at: datetime
    doc_type: str                  # 'code', 'docs', 'conversation'

    # For code
    language: Optional[str] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None
    file_path: Optional[str] = None

    # For documents
    heading: Optional[str] = None
    section: Optional[str] = None

    # Custom fields
    custom: Dict = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        result = {
            'source': self.source,
            'chunk_index': self.chunk_index,
            'total_chunks': self.total_chunks,
            'created_at': self.created_at.isoformat(),
            'doc_type': self.doc_type,
        }
        # Add optional fields if set
        for field in ['language', 'function_name', 'class_name',
                      'file_path', 'heading', 'section']:
            value = getattr(self, field)
            if value:
                result[field] = value
        if self.custom:
            result.update(self.custom)
        return result

def enrich_chunks_with_metadata(
    chunks: List[str],
    source: str,
    doc_type: str,
    **kwargs
) -> List[tuple[str, Dict]]:
    """Add metadata to chunks."""
    enriched = []
    total = len(chunks)

    for i, chunk in enumerate(chunks):
        metadata = ChunkMetadata(
            source=source,
            chunk_index=i,
            total_chunks=total,
            created_at=datetime.now(),
            doc_type=doc_type,
            **kwargs
        )
        enriched.append((chunk, metadata.to_dict()))

    return enriched
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// chunking/metadata.ts
import { z } from 'zod';

// Schema for chunk metadata
const ChunkMetadataSchema = z.object({
  source: z.string(),           // File path or document ID
  chunkIndex: z.number(),       // Position in original document
  totalChunks: z.number(),      // Total chunks from this source
  createdAt: z.string(),        // ISO date string
  docType: z.enum(['code', 'docs', 'conversation']),

  // For code
  language: z.string().optional(),
  functionName: z.string().optional(),
  className: z.string().optional(),
  filePath: z.string().optional(),

  // For documents
  heading: z.string().optional(),
  section: z.string().optional(),

  // Custom fields
  custom: z.record(z.any()).optional(),
});

type ChunkMetadata = z.infer<typeof ChunkMetadataSchema>;

interface EnrichedChunk {
  content: string;
  metadata: ChunkMetadata;
}

function createChunkMetadata(
  source: string,
  chunkIndex: number,
  totalChunks: number,
  docType: 'code' | 'docs' | 'conversation',
  options: Partial<Omit<ChunkMetadata, 'source' | 'chunkIndex' | 'totalChunks' | 'createdAt' | 'docType'>> = {}
): ChunkMetadata {
  return {
    source,
    chunkIndex,
    totalChunks,
    createdAt: new Date().toISOString(),
    docType,
    ...options,
  };
}

function enrichChunksWithMetadata(
  chunks: string[],
  source: string,
  docType: 'code' | 'docs' | 'conversation',
  options: Partial<ChunkMetadata> = {}
): EnrichedChunk[] {
  const total = chunks.length;

  return chunks.map((content, index) => ({
    content,
    metadata: createChunkMetadata(source, index, total, docType, options),
  }));
}

// Usage example
const chunks = ['chunk 1 content', 'chunk 2 content'];
const enriched = enrichChunksWithMetadata(
  chunks,
  'src/utils/helpers.ts',
  'code',
  { language: 'typescript', functionName: 'processData' }
);
```

</details>

---

<a name="pitfalls"></a>
## 3. RAG Pitfalls & Advanced Patterns (45 min)

### 3.1 Common RAG Failures

```
┌─────────────────────────────────────────────────────────────────┐
│                    Common RAG Failures                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. RETRIEVAL FAILURES                                          │
│     ├── Wrong documents retrieved                               │
│     ├── Relevant documents missed                               │
│     ├── Too many irrelevant results dilute context              │
│     └── Semantic gap between query and documents                │
│                                                                 │
│  2. GENERATION FAILURES                                         │
│     ├── LLM ignores retrieved context                           │
│     ├── LLM contradicts retrieved context                       │
│     ├── LLM extrapolates beyond context                         │
│     └── Answer format doesn't match query intent                │
│                                                                 │
│  3. SYSTEM FAILURES                                             │
│     ├── Stale/outdated index                                    │
│     ├── Chunking destroys important context                     │
│     ├── Embedding quality issues                                │
│     └── Latency too high for use case                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 RAG Failure Checklist

```markdown
## RAG Debugging Checklist

### If Answers Are Wrong
1. [ ] Check retrieved documents - are they relevant?
2. [ ] Check if answer is in retrieved docs at all
3. [ ] Try different number of retrieved docs (k)
4. [ ] Examine embedding similarity scores
5. [ ] Test query reformulation

### If Retrieval Is Poor
1. [ ] Check chunk sizes - too small/large?
2. [ ] Verify embeddings are working correctly
3. [ ] Test with exact phrase from document
4. [ ] Check for vocabulary mismatch
5. [ ] Consider hybrid search (vector + keyword)

### If Generation Is Poor
1. [ ] Check context window usage
2. [ ] Verify prompt template
3. [ ] Test with context in different positions
4. [ ] Check for conflicting information in context
5. [ ] Try explicit instruction to use only context
```

### 3.3 Advanced Pattern: Hybrid Search

<details>
<summary><b>Python</b></summary>

```python
# rag/hybrid_search.py
"""Combine vector search with keyword search."""
from typing import List, Dict, Any
import re
from rank_bm25 import BM25Okapi

class HybridSearch:
    """Combines semantic (vector) and lexical (BM25) search."""

    def __init__(self, vector_store, documents: List[str]):
        self.vector_store = vector_store
        self.documents = documents

        # Build BM25 index
        tokenized = [self._tokenize(doc) for doc in documents]
        self.bm25 = BM25Okapi(tokenized)

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        return re.findall(r'\w+', text.lower())

    def search(
        self,
        query: str,
        k: int = 10,
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Hybrid search combining vector and BM25 scores."""
        # Vector search
        vector_results = self.vector_store.query(query, n_results=k*2)

        # BM25 search
        tokenized_query = self._tokenize(query)
        bm25_scores = self.bm25.get_scores(tokenized_query)

        # Combine scores
        combined = {}
        for i, result in enumerate(vector_results):
            doc_id = result['id']
            # Normalize vector score (distance to similarity)
            vector_score = 1 / (1 + result['distance'])
            combined[doc_id] = {
                'content': result['content'],
                'vector_score': vector_score,
                'bm25_score': 0,
                'combined': 0
            }

        # Add BM25 scores
        for i, score in enumerate(bm25_scores):
            doc_id = f"doc_{i}"
            if doc_id in combined:
                combined[doc_id]['bm25_score'] = score
            elif score > 0:
                combined[doc_id] = {
                    'content': self.documents[i],
                    'vector_score': 0,
                    'bm25_score': score,
                    'combined': 0
                }

        # Normalize and combine
        max_vector = max(r['vector_score'] for r in combined.values()) or 1
        max_bm25 = max(r['bm25_score'] for r in combined.values()) or 1

        for doc_id in combined:
            combined[doc_id]['vector_score'] /= max_vector
            combined[doc_id]['bm25_score'] /= max_bm25
            combined[doc_id]['combined'] = (
                vector_weight * combined[doc_id]['vector_score'] +
                bm25_weight * combined[doc_id]['bm25_score']
            )

        # Sort by combined score
        sorted_results = sorted(
            combined.items(),
            key=lambda x: x[1]['combined'],
            reverse=True
        )

        return [
            {'id': doc_id, **data}
            for doc_id, data in sorted_results[:k]
        ]
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// rag/hybrid-search.ts

interface Document {
  id: string;
  content: string;
}

interface SearchResult {
  id: string;
  content: string;
  vectorScore: number;
  bm25Score: number;
  combined: number;
}

interface VectorStore {
  query(query: string, nResults: number): Promise<{ id: string; content: string; distance: number }[]>;
}

/**
 * Simple BM25 implementation for keyword search.
 */
class BM25 {
  private documents: string[][];
  private avgDocLength: number;
  private docFreq: Map<string, number> = new Map();
  private k1 = 1.5;
  private b = 0.75;

  constructor(documents: string[]) {
    this.documents = documents.map(doc => this.tokenize(doc));
    this.avgDocLength = this.documents.reduce((sum, doc) => sum + doc.length, 0) / this.documents.length;

    // Calculate document frequencies
    for (const doc of this.documents) {
      const uniqueTerms = new Set(doc);
      for (const term of uniqueTerms) {
        this.docFreq.set(term, (this.docFreq.get(term) || 0) + 1);
      }
    }
  }

  private tokenize(text: string): string[] {
    return text.toLowerCase().match(/\w+/g) || [];
  }

  getScores(query: string): number[] {
    const queryTerms = this.tokenize(query);
    const N = this.documents.length;

    return this.documents.map(doc => {
      let score = 0;
      const docLength = doc.length;
      const termFreq = new Map<string, number>();

      for (const term of doc) {
        termFreq.set(term, (termFreq.get(term) || 0) + 1);
      }

      for (const term of queryTerms) {
        const tf = termFreq.get(term) || 0;
        const df = this.docFreq.get(term) || 0;

        if (tf > 0 && df > 0) {
          const idf = Math.log((N - df + 0.5) / (df + 0.5) + 1);
          const tfNorm = (tf * (this.k1 + 1)) /
            (tf + this.k1 * (1 - this.b + this.b * docLength / this.avgDocLength));
          score += idf * tfNorm;
        }
      }

      return score;
    });
  }
}

/**
 * Hybrid search combining vector and BM25 search.
 */
class HybridSearch {
  private bm25: BM25;

  constructor(
    private vectorStore: VectorStore,
    private documents: Document[]
  ) {
    this.bm25 = new BM25(documents.map(d => d.content));
  }

  async search(
    query: string,
    k: number = 10,
    vectorWeight: number = 0.7,
    bm25Weight: number = 0.3
  ): Promise<SearchResult[]> {
    // Vector search
    const vectorResults = await this.vectorStore.query(query, k * 2);

    // BM25 search
    const bm25Scores = this.bm25.getScores(query);

    // Combine scores
    const combined = new Map<string, SearchResult>();

    for (const result of vectorResults) {
      const vectorScore = 1 / (1 + result.distance);
      combined.set(result.id, {
        id: result.id,
        content: result.content,
        vectorScore,
        bm25Score: 0,
        combined: 0,
      });
    }

    // Add BM25 scores
    for (let i = 0; i < bm25Scores.length; i++) {
      const doc = this.documents[i];
      const score = bm25Scores[i];

      if (combined.has(doc.id)) {
        combined.get(doc.id)!.bm25Score = score;
      } else if (score > 0) {
        combined.set(doc.id, {
          id: doc.id,
          content: doc.content,
          vectorScore: 0,
          bm25Score: score,
          combined: 0,
        });
      }
    }

    // Normalize and combine
    const results = Array.from(combined.values());
    const maxVector = Math.max(...results.map(r => r.vectorScore)) || 1;
    const maxBm25 = Math.max(...results.map(r => r.bm25Score)) || 1;

    for (const result of results) {
      result.vectorScore /= maxVector;
      result.bm25Score /= maxBm25;
      result.combined = vectorWeight * result.vectorScore + bm25Weight * result.bm25Score;
    }

    // Sort by combined score and return top k
    return results.sort((a, b) => b.combined - a.combined).slice(0, k);
  }
}
```

</details>

### 3.4 Advanced Pattern: Query Transformation

<details>
<summary><b>Python</b></summary>

```python
# rag/query_transform.py
"""Transform queries to improve retrieval."""

QUERY_EXPANSION_PROMPT = """Given a user query, generate 3 alternative phrasings
that might help find relevant documents.

Original query: {query}

Alternative phrasings (one per line):"""

HYPOTHETICAL_DOCUMENT_PROMPT = """Given a question, write a short paragraph
that would be a perfect answer to this question. This will be used to find
similar content.

Question: {query}

Hypothetical perfect answer:"""

class QueryTransformer:
    """Transforms queries to improve retrieval."""

    def __init__(self, llm_client):
        self.llm = llm_client

    def expand_query(self, query: str) -> List[str]:
        """Generate alternative query phrasings."""
        prompt = QUERY_EXPANSION_PROMPT.format(query=query)
        response = self.llm.chat([
            {"role": "user", "content": prompt}
        ])

        alternatives = [q.strip() for q in response.split('\n') if q.strip()]
        return [query] + alternatives[:3]  # Original + 3 alternatives

    def hyde(self, query: str) -> str:
        """
        Hypothetical Document Embedding (HyDE).
        Generate a hypothetical answer and use that for retrieval.
        """
        prompt = HYPOTHETICAL_DOCUMENT_PROMPT.format(query=query)
        response = self.llm.chat([
            {"role": "user", "content": prompt}
        ])
        return response

    def step_back(self, query: str) -> str:
        """Generate a more general 'step-back' question."""
        prompt = f"""Given this specific question, generate a more general
question that would help understand the broader context.

Specific question: {query}

More general question:"""

        response = self.llm.chat([
            {"role": "user", "content": prompt}
        ])
        return response.strip()
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// rag/query-transform.ts

const QUERY_EXPANSION_PROMPT = `Given a user query, generate 3 alternative phrasings
that might help find relevant documents.

Original query: {query}

Alternative phrasings (one per line):`;

const HYPOTHETICAL_DOCUMENT_PROMPT = `Given a question, write a short paragraph
that would be a perfect answer to this question. This will be used to find
similar content.

Question: {query}

Hypothetical perfect answer:`;

interface LLMClient {
  chat(messages: { role: string; content: string }[]): Promise<string>;
}

/**
 * Transforms queries to improve retrieval.
 */
class QueryTransformer {
  constructor(private llm: LLMClient) {}

  /**
   * Generate alternative query phrasings.
   */
  async expandQuery(query: string): Promise<string[]> {
    const prompt = QUERY_EXPANSION_PROMPT.replace('{query}', query);
    const response = await this.llm.chat([{ role: 'user', content: prompt }]);

    const alternatives = response
      .split('\n')
      .map(q => q.trim())
      .filter(q => q.length > 0);

    return [query, ...alternatives.slice(0, 3)]; // Original + 3 alternatives
  }

  /**
   * Hypothetical Document Embedding (HyDE).
   * Generate a hypothetical answer and use that for retrieval.
   */
  async hyde(query: string): Promise<string> {
    const prompt = HYPOTHETICAL_DOCUMENT_PROMPT.replace('{query}', query);
    const response = await this.llm.chat([{ role: 'user', content: prompt }]);
    return response;
  }

  /**
   * Generate a more general 'step-back' question.
   */
  async stepBack(query: string): Promise<string> {
    const prompt = `Given this specific question, generate a more general
question that would help understand the broader context.

Specific question: ${query}

More general question:`;

    const response = await this.llm.chat([{ role: 'user', content: prompt }]);
    return response.trim();
  }
}

// Usage example
async function enhancedRetrieval(
  query: string,
  transformer: QueryTransformer,
  vectorStore: { query: (q: string, k: number) => Promise<any[]> }
) {
  // Strategy 1: Query expansion
  const expandedQueries = await transformer.expandQuery(query);

  // Search with all query variants
  const allResults = await Promise.all(
    expandedQueries.map(q => vectorStore.query(q, 5))
  );

  // Deduplicate and merge results
  const seen = new Set<string>();
  const mergedResults = allResults.flat().filter(result => {
    if (seen.has(result.id)) return false;
    seen.add(result.id);
    return true;
  });

  return mergedResults;
}
```

</details>

### 3.5 Advanced Pattern: Reranking

<details>
<summary><b>Python</b></summary>

```python
# rag/reranking.py
"""Rerank retrieved documents for better relevance."""
from typing import List, Dict

RERANK_PROMPT = """Given a question and a list of documents, rank them by relevance.
Return document numbers in order of relevance (most relevant first).

Question: {query}

Documents:
{documents}

Ranking (comma-separated document numbers, e.g., "3,1,4,2"):"""

class LLMReranker:
    """Use LLM to rerank retrieved documents."""

    def __init__(self, llm_client):
        self.llm = llm_client

    def rerank(
        self,
        query: str,
        documents: List[Dict],
        top_k: int = 5
    ) -> List[Dict]:
        """Rerank documents using LLM."""
        # Format documents for prompt
        doc_text = "\n\n".join([
            f"Document {i+1}:\n{doc['content'][:500]}..."
            for i, doc in enumerate(documents)
        ])

        prompt = RERANK_PROMPT.format(query=query, documents=doc_text)

        response = self.llm.chat([
            {"role": "user", "content": prompt}
        ])

        # Parse ranking
        try:
            ranking = [int(x.strip())-1 for x in response.split(',')]
            reranked = [documents[i] for i in ranking if i < len(documents)]
            return reranked[:top_k]
        except (ValueError, IndexError):
            # Fallback to original order
            return documents[:top_k]


# Alternative: Cross-encoder reranking (faster, more accurate)
def cross_encoder_rerank(query: str, documents: List[str], model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
    """Rerank using a cross-encoder model."""
    from sentence_transformers import CrossEncoder

    model = CrossEncoder(model_name)

    # Score each query-document pair
    pairs = [[query, doc] for doc in documents]
    scores = model.predict(pairs)

    # Sort by score
    scored_docs = list(zip(documents, scores))
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    return [doc for doc, score in scored_docs]
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// rag/reranking.ts

const RERANK_PROMPT = `Given a question and a list of documents, rank them by relevance.
Return document numbers in order of relevance (most relevant first).

Question: {query}

Documents:
{documents}

Ranking (comma-separated document numbers, e.g., "3,1,4,2"):`;

interface Document {
  id: string;
  content: string;
  [key: string]: any;
}

interface LLMClient {
  chat(messages: { role: string; content: string }[]): Promise<string>;
}

/**
 * Use LLM to rerank retrieved documents.
 */
class LLMReranker {
  constructor(private llm: LLMClient) {}

  async rerank(query: string, documents: Document[], topK: number = 5): Promise<Document[]> {
    // Format documents for prompt
    const docText = documents
      .map((doc, i) => `Document ${i + 1}:\n${doc.content.slice(0, 500)}...`)
      .join('\n\n');

    const prompt = RERANK_PROMPT
      .replace('{query}', query)
      .replace('{documents}', docText);

    const response = await this.llm.chat([{ role: 'user', content: prompt }]);

    // Parse ranking
    try {
      const ranking = response
        .split(',')
        .map(x => parseInt(x.trim(), 10) - 1)
        .filter(i => !isNaN(i) && i >= 0 && i < documents.length);

      const reranked = ranking.map(i => documents[i]);
      return reranked.slice(0, topK);
    } catch {
      // Fallback to original order
      return documents.slice(0, topK);
    }
  }
}

/**
 * Alternative: Cohere reranking (faster, more accurate).
 * Requires Cohere API key.
 */
class CohereReranker {
  private baseUrl = 'https://api.cohere.ai/v1/rerank';

  constructor(private apiKey: string) {}

  async rerank(
    query: string,
    documents: string[],
    topK: number = 5,
    model: string = 'rerank-english-v3.0'
  ): Promise<{ document: string; relevanceScore: number }[]> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        documents,
        top_n: topK,
        model,
      }),
    });

    if (!response.ok) {
      throw new Error(`Cohere rerank failed: ${response.statusText}`);
    }

    const data = await response.json();

    return data.results.map((result: any) => ({
      document: documents[result.index],
      relevanceScore: result.relevance_score,
    }));
  }
}

// Usage example
async function rerankedSearch(
  query: string,
  vectorStore: { query: (q: string, k: number) => Promise<Document[]> },
  reranker: LLMReranker
): Promise<Document[]> {
  // Get initial results (fetch more than needed)
  const initialResults = await vectorStore.query(query, 20);

  // Rerank to get best results
  const reranked = await reranker.rerank(query, initialResults, 5);

  return reranked;
}
```

</details>

---

<a name="exercise-1"></a>
## 4. Exercise 1: RAG Architecture Design (30 min)

### Task
Design a RAG system for a codebase Q&A assistant.

### Scenario
You're building a system that lets developers ask questions about a large codebase:
- 500+ source files
- Mixed Python and TypeScript
- Includes documentation and READMEs
- Need to answer questions like:
  - "How does authentication work?"
  - "Where is the database connection configured?"
  - "What does the processOrder function do?"

### Template

```markdown
## Codebase RAG Architecture

### Document Types to Index
1. Type:
   - Chunking strategy:
   - Chunk size:
   - Metadata to include:

2. Type:
   - Chunking strategy:
   - Chunk size:
   - Metadata to include:

### Query Handling
- How will you handle:
  - Code-specific queries (function names, etc.):
  - Conceptual queries (how does X work):
  - Multi-file queries (how do A and B interact):

### Retrieval Strategy
- Vector search configuration:
- Will you use hybrid search? Why/why not:
- Reranking approach:

### Generation
- System prompt considerations:
- How will you format code in responses:
- How will you cite sources:

### Architecture Diagram
```
[Draw your RAG pipeline]
```

### Potential Issues
1.
2.
3.

### Metrics to Track
1.
2.
3.
```

---

<a name="evaluation"></a>
## 5. Evaluation Fundamentals (45 min)

### 5.1 Why Evaluation Matters

```
┌─────────────────────────────────────────────────────────────────┐
│                    Evaluation Importance                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Without Evaluation:                                            │
│  ───────────────────                                            │
│  "It seems to work" → Ship it → Users complain → Firefighting   │
│                                                                 │
│  With Evaluation:                                               │
│  ────────────────                                               │
│  Measure → Understand → Improve → Measure → Ship with confidence│
│                                                                 │
│  What to Evaluate:                                              │
│  ─────────────────                                              │
│  1. RETRIEVAL QUALITY                                           │
│     • Are we finding the right documents?                       │
│     • Are we ranking them correctly?                            │
│                                                                 │
│  2. GENERATION QUALITY                                          │
│     • Is the answer correct?                                    │
│     • Is it relevant to the question?                           │
│     • Is it well-formatted?                                     │
│                                                                 │
│  3. END-TO-END QUALITY                                          │
│     • Does the system solve user problems?                      │
│     • Would users trust these answers?                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Retrieval Metrics

<details>
<summary><b>Python</b></summary>

```python
# evaluation/retrieval_metrics.py
"""Metrics for evaluating retrieval quality."""
from typing import List, Set

def precision_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """Precision@K: What fraction of retrieved docs are relevant?"""
    retrieved_k = retrieved[:k]
    relevant_retrieved = len(set(retrieved_k) & relevant)
    return relevant_retrieved / k if k > 0 else 0.0

def recall_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    """Recall@K: What fraction of relevant docs did we retrieve?"""
    retrieved_k = retrieved[:k]
    relevant_retrieved = len(set(retrieved_k) & relevant)
    return relevant_retrieved / len(relevant) if relevant else 0.0

def mean_reciprocal_rank(retrieved: List[str], relevant: Set[str]) -> float:
    """MRR: How high is the first relevant result?"""
    for i, doc in enumerate(retrieved):
        if doc in relevant:
            return 1.0 / (i + 1)
    return 0.0

def ndcg_at_k(retrieved: List[str], relevance_scores: dict, k: int) -> float:
    """NDCG@K: Normalized Discounted Cumulative Gain."""
    import math

    def dcg(scores):
        return sum(score / math.log2(i + 2) for i, score in enumerate(scores))

    retrieved_scores = [relevance_scores.get(doc, 0) for doc in retrieved[:k]]
    ideal_scores = sorted(relevance_scores.values(), reverse=True)[:k]

    dcg_score = dcg(retrieved_scores)
    idcg_score = dcg(ideal_scores)

    return dcg_score / idcg_score if idcg_score > 0 else 0.0

def evaluate_retrieval(queries, ground_truth, retriever, k=5):
    """Run retrieval evaluation."""
    metrics = {'precision': [], 'recall': [], 'mrr': []}

    for query, relevant in zip(queries, ground_truth):
        retrieved = retriever.query(query, n_results=k)
        retrieved_ids = [r['id'] for r in retrieved]

        metrics['precision'].append(precision_at_k(retrieved_ids, relevant, k))
        metrics['recall'].append(recall_at_k(retrieved_ids, relevant, k))
        metrics['mrr'].append(mean_reciprocal_rank(retrieved_ids, relevant))

    return {name: sum(values) / len(values) for name, values in metrics.items()}
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// evaluation/retrieval-metrics.ts

/**
 * Precision@K: What fraction of retrieved docs are relevant?
 */
function precisionAtK(retrieved: string[], relevant: Set<string>, k: number): number {
  const retrievedK = retrieved.slice(0, k);
  const relevantRetrieved = retrievedK.filter((doc) => relevant.has(doc)).length;
  return k > 0 ? relevantRetrieved / k : 0;
}

/**
 * Recall@K: What fraction of relevant docs did we retrieve?
 */
function recallAtK(retrieved: string[], relevant: Set<string>, k: number): number {
  const retrievedK = retrieved.slice(0, k);
  const relevantRetrieved = retrievedK.filter((doc) => relevant.has(doc)).length;
  return relevant.size > 0 ? relevantRetrieved / relevant.size : 0;
}

/**
 * MRR: How high is the first relevant result?
 */
function meanReciprocalRank(retrieved: string[], relevant: Set<string>): number {
  for (let i = 0; i < retrieved.length; i++) {
    if (relevant.has(retrieved[i])) {
      return 1 / (i + 1);
    }
  }
  return 0;
}

/**
 * NDCG@K: Normalized Discounted Cumulative Gain.
 */
function ndcgAtK(retrieved: string[], relevanceScores: Map<string, number>, k: number): number {
  const dcg = (scores: number[]) =>
    scores.reduce((sum, score, i) => sum + score / Math.log2(i + 2), 0);

  const retrievedScores = retrieved.slice(0, k).map((doc) => relevanceScores.get(doc) || 0);
  const idealScores = Array.from(relevanceScores.values())
    .sort((a, b) => b - a)
    .slice(0, k);

  const dcgScore = dcg(retrievedScores);
  const idcgScore = dcg(idealScores);

  return idcgScore > 0 ? dcgScore / idcgScore : 0;
}

interface RetrievalMetrics {
  precision: number;
  recall: number;
  mrr: number;
}

async function evaluateRetrieval(
  queries: string[],
  groundTruth: Set<string>[],
  retriever: { query: (q: string, n: number) => Promise<{ id: string }[]> },
  k: number = 5
): Promise<RetrievalMetrics> {
  const metrics = { precision: [] as number[], recall: [] as number[], mrr: [] as number[] };

  for (let i = 0; i < queries.length; i++) {
    const query = queries[i];
    const relevant = groundTruth[i];

    const retrieved = await retriever.query(query, k);
    const retrievedIds = retrieved.map((r) => r.id);

    metrics.precision.push(precisionAtK(retrievedIds, relevant, k));
    metrics.recall.push(recallAtK(retrievedIds, relevant, k));
    metrics.mrr.push(meanReciprocalRank(retrievedIds, relevant));
  }

  const avg = (arr: number[]) => arr.reduce((a, b) => a + b, 0) / arr.length;

  return {
    precision: avg(metrics.precision),
    recall: avg(metrics.recall),
    mrr: avg(metrics.mrr),
  };
}
```

</details>

### 5.3 LLM-as-Judge Evaluation

<details>
<summary><b>Python</b></summary>

```python
# evaluation/llm_judge.py
"""Use LLM to evaluate response quality."""

JUDGE_PROMPT_RELEVANCE = """Rate how relevant this answer is to the question.

Question: {question}
Answer: {answer}

Rate from 1-5:
1 = Completely irrelevant
2 = Slightly relevant
3 = Moderately relevant
4 = Very relevant
5 = Perfectly relevant

Provide your rating as a single number followed by a brief explanation.
Rating:"""

JUDGE_PROMPT_FAITHFULNESS = """Check if the answer is faithful to the provided context.

Context:
{context}

Question: {question}
Answer: {answer}

Does the answer contain any claims not supported by the context?
Rate from 1-5:
1 = Many unsupported claims
2 = Some unsupported claims
3 = Minor unsupported details
4 = Mostly faithful
5 = Completely faithful to context

Rating:"""

JUDGE_PROMPT_CORRECTNESS = """Given the ground truth answer, rate how correct this answer is.

Question: {question}
Ground Truth: {ground_truth}
Generated Answer: {answer}

Rate from 1-5:
1 = Completely wrong
2 = Mostly wrong with some correct elements
3 = Partially correct
4 = Mostly correct with minor errors
5 = Completely correct

Rating:"""

class LLMJudge:
    """Use an LLM to judge response quality."""

    def __init__(self, llm_client, model: str = None):
        self.llm = llm_client
        self.model = model

    def evaluate_relevance(self, question: str, answer: str) -> dict:
        """Evaluate answer relevance to question."""
        prompt = JUDGE_PROMPT_RELEVANCE.format(
            question=question,
            answer=answer
        )
        response = self.llm.chat([{"role": "user", "content": prompt}])
        return self._parse_rating(response)

    def evaluate_faithfulness(
        self,
        context: str,
        question: str,
        answer: str
    ) -> dict:
        """Evaluate if answer is faithful to context."""
        prompt = JUDGE_PROMPT_FAITHFULNESS.format(
            context=context,
            question=question,
            answer=answer
        )
        response = self.llm.chat([{"role": "user", "content": prompt}])
        return self._parse_rating(response)

    def evaluate_correctness(
        self,
        question: str,
        ground_truth: str,
        answer: str
    ) -> dict:
        """Evaluate answer correctness against ground truth."""
        prompt = JUDGE_PROMPT_CORRECTNESS.format(
            question=question,
            ground_truth=ground_truth,
            answer=answer
        )
        response = self.llm.chat([{"role": "user", "content": prompt}])
        return self._parse_rating(response)

    def _parse_rating(self, response: str) -> dict:
        """Parse rating from LLM response."""
        import re
        # Find first number 1-5
        match = re.search(r'\b([1-5])\b', response)
        rating = int(match.group(1)) if match else None
        return {
            'rating': rating,
            'explanation': response
        }
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// evaluation/llm-judge.ts

const JUDGE_PROMPT_RELEVANCE = `Rate how relevant this answer is to the question.

Question: {question}
Answer: {answer}

Rate from 1-5:
1 = Completely irrelevant
2 = Slightly relevant
3 = Moderately relevant
4 = Very relevant
5 = Perfectly relevant

Provide your rating as a single number followed by a brief explanation.
Rating:`;

const JUDGE_PROMPT_FAITHFULNESS = `Check if the answer is faithful to the provided context.

Context:
{context}

Question: {question}
Answer: {answer}

Does the answer contain any claims not supported by the context?
Rate from 1-5:
1 = Many unsupported claims
2 = Some unsupported claims
3 = Minor unsupported details
4 = Mostly faithful
5 = Completely faithful to context

Rating:`;

const JUDGE_PROMPT_CORRECTNESS = `Given the ground truth answer, rate how correct this answer is.

Question: {question}
Ground Truth: {ground_truth}
Generated Answer: {answer}

Rate from 1-5:
1 = Completely wrong
2 = Mostly wrong with some correct elements
3 = Partially correct
4 = Mostly correct with minor errors
5 = Completely correct

Rating:`;

interface LLMClient {
  chat(messages: { role: string; content: string }[]): Promise<string>;
}

interface JudgeResult {
  rating: number | null;
  explanation: string;
}

/**
 * Use an LLM to judge response quality.
 */
class LLMJudge {
  constructor(private llm: LLMClient) {}

  async evaluateRelevance(question: string, answer: string): Promise<JudgeResult> {
    const prompt = JUDGE_PROMPT_RELEVANCE
      .replace('{question}', question)
      .replace('{answer}', answer);

    const response = await this.llm.chat([{ role: 'user', content: prompt }]);
    return this.parseRating(response);
  }

  async evaluateFaithfulness(
    context: string,
    question: string,
    answer: string
  ): Promise<JudgeResult> {
    const prompt = JUDGE_PROMPT_FAITHFULNESS
      .replace('{context}', context)
      .replace('{question}', question)
      .replace('{answer}', answer);

    const response = await this.llm.chat([{ role: 'user', content: prompt }]);
    return this.parseRating(response);
  }

  async evaluateCorrectness(
    question: string,
    groundTruth: string,
    answer: string
  ): Promise<JudgeResult> {
    const prompt = JUDGE_PROMPT_CORRECTNESS
      .replace('{question}', question)
      .replace('{ground_truth}', groundTruth)
      .replace('{answer}', answer);

    const response = await this.llm.chat([{ role: 'user', content: prompt }]);
    return this.parseRating(response);
  }

  private parseRating(response: string): JudgeResult {
    // Find first number 1-5
    const match = response.match(/\b([1-5])\b/);
    const rating = match ? parseInt(match[1], 10) : null;

    return {
      rating,
      explanation: response,
    };
  }
}

// Usage example
async function evaluateRAGResponse(
  judge: LLMJudge,
  question: string,
  context: string,
  generatedAnswer: string,
  expectedAnswer: string
) {
  const [relevance, faithfulness, correctness] = await Promise.all([
    judge.evaluateRelevance(question, generatedAnswer),
    judge.evaluateFaithfulness(context, question, generatedAnswer),
    judge.evaluateCorrectness(question, expectedAnswer, generatedAnswer),
  ]);

  return {
    relevance: relevance.rating,
    faithfulness: faithfulness.rating,
    correctness: correctness.rating,
    details: { relevance, faithfulness, correctness },
  };
}
```

</details>

### 5.4 Building Evaluation Datasets

<details>
<summary><b>Python</b></summary>

```python
# evaluation/dataset.py
"""Building and managing evaluation datasets."""
from dataclasses import dataclass
from typing import List, Optional, Dict
import json

@dataclass
class EvalExample:
    """Single evaluation example."""
    id: str
    question: str
    expected_answer: str
    relevant_docs: List[str]  # IDs of relevant documents
    context: Optional[str] = None  # For faithfulness evaluation
    metadata: Dict = None

class EvalDataset:
    """Evaluation dataset management."""

    def __init__(self, examples: List[EvalExample] = None):
        self.examples = examples or []

    def add_example(self, example: EvalExample):
        """Add an example to the dataset."""
        self.examples.append(example)

    def add_from_production(
        self,
        question: str,
        answer: str,
        rating: int,
        relevant_docs: List[str]
    ):
        """Add example from production feedback."""
        # Only add high-quality examples
        if rating >= 4:
            example = EvalExample(
                id=f"prod_{len(self.examples)}",
                question=question,
                expected_answer=answer,
                relevant_docs=relevant_docs
            )
            self.examples.append(example)

    def save(self, path: str):
        """Save dataset to JSON."""
        data = [
            {
                'id': ex.id,
                'question': ex.question,
                'expected_answer': ex.expected_answer,
                'relevant_docs': ex.relevant_docs,
                'context': ex.context,
                'metadata': ex.metadata
            }
            for ex in self.examples
        ]
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: str) -> 'EvalDataset':
        """Load dataset from JSON."""
        with open(path) as f:
            data = json.load(f)

        examples = [
            EvalExample(
                id=ex['id'],
                question=ex['question'],
                expected_answer=ex['expected_answer'],
                relevant_docs=ex['relevant_docs'],
                context=ex.get('context'),
                metadata=ex.get('metadata')
            )
            for ex in data
        ]
        return cls(examples)

# Example: Creating an evaluation dataset
def create_sample_eval_dataset() -> EvalDataset:
    """Create a sample evaluation dataset."""
    dataset = EvalDataset()

    # Add examples
    dataset.add_example(EvalExample(
        id="q1",
        question="What integrations does TaskFlow support?",
        expected_answer="TaskFlow supports integrations with Slack, GitHub, and Jira.",
        relevant_docs=["doc_integrations", "doc_features"]
    ))

    dataset.add_example(EvalExample(
        id="q2",
        question="How much does the basic plan cost?",
        expected_answer="The basic plan costs $10 per user per month.",
        relevant_docs=["doc_pricing"]
    ))

    return dataset
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// evaluation/dataset.ts
import { z } from 'zod';
import * as fs from 'fs/promises';

// Schema for evaluation examples
const EvalExampleSchema = z.object({
  id: z.string(),
  question: z.string(),
  expectedAnswer: z.string(),
  relevantDocs: z.array(z.string()),
  context: z.string().optional(),
  metadata: z.record(z.any()).optional(),
});

type EvalExample = z.infer<typeof EvalExampleSchema>;

/**
 * Evaluation dataset management.
 */
class EvalDataset {
  private examples: EvalExample[] = [];

  constructor(examples: EvalExample[] = []) {
    this.examples = examples;
  }

  addExample(example: EvalExample): void {
    this.examples.push(example);
  }

  addFromProduction(
    question: string,
    answer: string,
    rating: number,
    relevantDocs: string[]
  ): void {
    // Only add high-quality examples
    if (rating >= 4) {
      this.examples.push({
        id: `prod_${this.examples.length}`,
        question,
        expectedAnswer: answer,
        relevantDocs,
      });
    }
  }

  getExamples(): EvalExample[] {
    return this.examples;
  }

  size(): number {
    return this.examples.length;
  }

  async save(path: string): Promise<void> {
    const data = this.examples.map(ex => ({
      id: ex.id,
      question: ex.question,
      expected_answer: ex.expectedAnswer,
      relevant_docs: ex.relevantDocs,
      context: ex.context,
      metadata: ex.metadata,
    }));

    await fs.writeFile(path, JSON.stringify(data, null, 2));
  }

  static async load(path: string): Promise<EvalDataset> {
    const content = await fs.readFile(path, 'utf-8');
    const data = JSON.parse(content);

    const examples: EvalExample[] = data.map((ex: any) => ({
      id: ex.id,
      question: ex.question,
      expectedAnswer: ex.expected_answer,
      relevantDocs: ex.relevant_docs,
      context: ex.context,
      metadata: ex.metadata,
    }));

    return new EvalDataset(examples);
  }
}

// Example: Creating an evaluation dataset
function createSampleEvalDataset(): EvalDataset {
  const dataset = new EvalDataset();

  dataset.addExample({
    id: 'q1',
    question: 'What integrations does TaskFlow support?',
    expectedAnswer: 'TaskFlow supports integrations with Slack, GitHub, and Jira.',
    relevantDocs: ['doc_integrations', 'doc_features'],
  });

  dataset.addExample({
    id: 'q2',
    question: 'How much does the basic plan cost?',
    expectedAnswer: 'The basic plan costs $10 per user per month.',
    relevantDocs: ['doc_pricing'],
  });

  return dataset;
}

// Usage
async function main() {
  const dataset = createSampleEvalDataset();
  console.log(`Dataset size: ${dataset.size()}`);

  // Save to file
  await dataset.save('eval_dataset.json');

  // Load from file
  const loaded = await EvalDataset.load('eval_dataset.json');
  console.log(`Loaded ${loaded.size()} examples`);
}
```

</details>

### 5.5 Evaluation Pipeline

<details>
<summary><b>Python</b></summary>

```python
# evaluation/pipeline.py
"""Complete evaluation pipeline."""
from dataclasses import dataclass
from typing import Dict, List, Any
import time

@dataclass
class EvalResult:
    """Result of a single evaluation."""
    example_id: str
    retrieval_metrics: Dict[str, float]
    generation_metrics: Dict[str, float]
    latency_ms: float
    retrieved_docs: List[str]
    generated_answer: str

class RAGEvaluator:
    """Complete RAG evaluation pipeline."""

    def __init__(self, rag_system, judge: LLMJudge):
        self.rag = rag_system
        self.judge = judge

    def evaluate(self, dataset: EvalDataset) -> Dict[str, Any]:
        """Run full evaluation on dataset."""
        results = []

        for example in dataset.examples:
            start = time.time()

            # Run RAG
            retrieved = self.rag.query(example.question, n_results=5)
            answer = self.rag.generate_response(example.question)

            latency = (time.time() - start) * 1000

            # Evaluate retrieval
            retrieved_ids = [r['id'] for r in retrieved]
            relevant_set = set(example.relevant_docs)

            retrieval_metrics = {
                'precision@5': precision_at_k(retrieved_ids, relevant_set, 5),
                'recall@5': recall_at_k(retrieved_ids, relevant_set, 5),
                'mrr': mean_reciprocal_rank(retrieved_ids, relevant_set)
            }

            # Evaluate generation
            relevance = self.judge.evaluate_relevance(example.question, answer)
            correctness = self.judge.evaluate_correctness(
                example.question,
                example.expected_answer,
                answer
            )

            generation_metrics = {
                'relevance': relevance['rating'],
                'correctness': correctness['rating']
            }

            results.append(EvalResult(
                example_id=example.id,
                retrieval_metrics=retrieval_metrics,
                generation_metrics=generation_metrics,
                latency_ms=latency,
                retrieved_docs=retrieved_ids,
                generated_answer=answer
            ))

        # Aggregate results
        return self._aggregate_results(results)

    def _aggregate_results(self, results: List[EvalResult]) -> Dict[str, Any]:
        """Aggregate individual results into summary."""
        summary = {
            'retrieval': {},
            'generation': {},
            'latency': {
                'mean_ms': sum(r.latency_ms for r in results) / len(results),
                'p50_ms': sorted([r.latency_ms for r in results])[len(results)//2],
                'p95_ms': sorted([r.latency_ms for r in results])[int(len(results)*0.95)]
            },
            'n_examples': len(results)
        }

        # Average retrieval metrics
        for metric in ['precision@5', 'recall@5', 'mrr']:
            values = [r.retrieval_metrics[metric] for r in results]
            summary['retrieval'][metric] = sum(values) / len(values)

        # Average generation metrics
        for metric in ['relevance', 'correctness']:
            values = [r.generation_metrics[metric] for r in results if r.generation_metrics[metric]]
            summary['generation'][metric] = sum(values) / len(values) if values else None

        return summary
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// evaluation/pipeline.ts

interface EvalResult {
  exampleId: string;
  retrievalMetrics: {
    'precision@5': number;
    'recall@5': number;
    mrr: number;
  };
  generationMetrics: {
    relevance: number | null;
    correctness: number | null;
  };
  latencyMs: number;
  retrievedDocs: string[];
  generatedAnswer: string;
}

interface EvalSummary {
  retrieval: {
    'precision@5': number;
    'recall@5': number;
    mrr: number;
  };
  generation: {
    relevance: number | null;
    correctness: number | null;
  };
  latency: {
    meanMs: number;
    p50Ms: number;
    p95Ms: number;
  };
  nExamples: number;
}

interface RAGSystem {
  query(question: string, nResults: number): Promise<{ id: string; content: string }[]>;
  generateResponse(question: string): Promise<string>;
}

/**
 * Complete RAG evaluation pipeline.
 */
class RAGEvaluator {
  constructor(
    private rag: RAGSystem,
    private judge: LLMJudge
  ) {}

  async evaluate(dataset: EvalDataset): Promise<EvalSummary> {
    const results: EvalResult[] = [];
    const examples = dataset.getExamples();

    for (const example of examples) {
      const start = performance.now();

      // Run RAG
      const retrieved = await this.rag.query(example.question, 5);
      const answer = await this.rag.generateResponse(example.question);

      const latencyMs = performance.now() - start;

      // Evaluate retrieval
      const retrievedIds = retrieved.map(r => r.id);
      const relevantSet = new Set(example.relevantDocs);

      const retrievalMetrics = {
        'precision@5': precisionAtK(retrievedIds, relevantSet, 5),
        'recall@5': recallAtK(retrievedIds, relevantSet, 5),
        mrr: meanReciprocalRank(retrievedIds, relevantSet),
      };

      // Evaluate generation
      const [relevance, correctness] = await Promise.all([
        this.judge.evaluateRelevance(example.question, answer),
        this.judge.evaluateCorrectness(example.question, example.expectedAnswer, answer),
      ]);

      const generationMetrics = {
        relevance: relevance.rating,
        correctness: correctness.rating,
      };

      results.push({
        exampleId: example.id,
        retrievalMetrics,
        generationMetrics,
        latencyMs,
        retrievedDocs: retrievedIds,
        generatedAnswer: answer,
      });
    }

    return this.aggregateResults(results);
  }

  private aggregateResults(results: EvalResult[]): EvalSummary {
    const latencies = results.map(r => r.latencyMs).sort((a, b) => a - b);

    const avg = (arr: number[]) =>
      arr.length > 0 ? arr.reduce((a, b) => a + b, 0) / arr.length : 0;

    const percentile = (arr: number[], p: number) =>
      arr[Math.floor(arr.length * p)] || 0;

    // Average retrieval metrics
    const retrievalPrecision = avg(results.map(r => r.retrievalMetrics['precision@5']));
    const retrievalRecall = avg(results.map(r => r.retrievalMetrics['recall@5']));
    const retrievalMrr = avg(results.map(r => r.retrievalMetrics.mrr));

    // Average generation metrics (filter out nulls)
    const relevanceValues = results
      .map(r => r.generationMetrics.relevance)
      .filter((v): v is number => v !== null);
    const correctnessValues = results
      .map(r => r.generationMetrics.correctness)
      .filter((v): v is number => v !== null);

    return {
      retrieval: {
        'precision@5': retrievalPrecision,
        'recall@5': retrievalRecall,
        mrr: retrievalMrr,
      },
      generation: {
        relevance: relevanceValues.length > 0 ? avg(relevanceValues) : null,
        correctness: correctnessValues.length > 0 ? avg(correctnessValues) : null,
      },
      latency: {
        meanMs: avg(latencies),
        p50Ms: percentile(latencies, 0.5),
        p95Ms: percentile(latencies, 0.95),
      },
      nExamples: results.length,
    };
  }
}

// Usage example
async function runEvaluation(rag: RAGSystem, judge: LLMJudge) {
  const dataset = await EvalDataset.load('eval_dataset.json');
  const evaluator = new RAGEvaluator(rag, judge);

  const summary = await evaluator.evaluate(dataset);

  console.log('Evaluation Results:');
  console.log(`  Examples: ${summary.nExamples}`);
  console.log(`  Retrieval P@5: ${(summary.retrieval['precision@5'] * 100).toFixed(1)}%`);
  console.log(`  Retrieval R@5: ${(summary.retrieval['recall@5'] * 100).toFixed(1)}%`);
  console.log(`  Generation Relevance: ${summary.generation.relevance?.toFixed(2)}/5`);
  console.log(`  Mean Latency: ${summary.latency.meanMs.toFixed(0)}ms`);

  return summary;
}
```

</details>

### 5.5 Testing Strategies for AI Systems (45 min)

Testing AI systems requires different approaches than traditional software. This section covers practical testing strategies for production AI applications.

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Testing Pyramid                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                      ┌─────────────┐                            │
│                      │   E2E Tests │  Few, expensive            │
│                      │   (Manual)  │                            │
│                      └─────────────┘                            │
│                    ┌───────────────────┐                        │
│                    │  Integration Tests│  Some, moderate cost   │
│                    │  (With real LLMs) │                        │
│                    └───────────────────┘                        │
│              ┌─────────────────────────────────┐                │
│              │    Component Tests              │  Many, fast    │
│              │    (Mocked LLM responses)       │                │
│              └─────────────────────────────────┘                │
│        ┌───────────────────────────────────────────────┐        │
│        │          Unit Tests                           │        │
│        │  (Business logic, parsing, validation)        │        │
│        └───────────────────────────────────────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Level 1: Unit Tests (Test Everything Non-AI)**

<details>
<summary><b>Python with pytest</b></summary>

```python
# tests/test_prompt_builder.py
"""Unit tests for prompt building logic."""
import pytest
from app.prompts import build_analysis_prompt, extract_code_blocks

def test_build_analysis_prompt_includes_code():
    """Prompt should include the provided code."""
    code = "def hello(): pass"
    prompt = build_analysis_prompt(code, analysis_type="security")

    assert code in prompt
    assert "security" in prompt.lower()

def test_extract_code_blocks_single_block():
    """Should extract code from markdown blocks."""
    text = "Here's code:\n```python\nprint('hi')\n```"
    blocks = extract_code_blocks(text)

    assert len(blocks) == 1
    assert blocks[0] == "print('hi')"

def test_extract_code_blocks_multiple_blocks():
    """Should extract multiple code blocks."""
    text = """
    First:
    ```python
    x = 1
    ```
    Second:
    ```python
    y = 2
    ```
    """
    blocks = extract_code_blocks(text)

    assert len(blocks) == 2
    assert "x = 1" in blocks[0]
    assert "y = 2" in blocks[1]

def test_extract_code_blocks_no_blocks():
    """Should return empty list when no code blocks."""
    text = "Just text, no code"
    blocks = extract_code_blocks(text)

    assert blocks == []

# tests/test_chunking.py
"""Unit tests for document chunking."""
from app.rag import chunk_text, chunk_by_sentences

def test_chunk_text_respects_max_size():
    """Chunks should not exceed max size."""
    text = "word " * 1000  # 1000 words
    chunks = chunk_text(text, max_tokens=100)

    for chunk in chunks:
        # Rough estimate: 1 word ≈ 1.3 tokens
        assert len(chunk.split()) <= 130

def test_chunk_text_preserves_content():
    """All content should appear in some chunk."""
    text = "The quick brown fox jumps over the lazy dog"
    chunks = chunk_text(text, max_tokens=5)

    reconstructed = " ".join(chunks)
    assert all(word in reconstructed for word in text.split())

def test_chunk_by_sentences_splits_correctly():
    """Should split on sentence boundaries."""
    text = "First sentence. Second sentence. Third sentence."
    chunks = chunk_by_sentences(text, max_sentences=1)

    assert len(chunks) == 3
    assert "First sentence." in chunks[0]
```

</details>

**Level 2: Component Tests with Mocked LLM**

<details>
<summary><b>Python</b></summary>

```python
# tests/test_agent_with_mock.py
"""Component tests with mocked LLM responses."""
import pytest
from unittest.mock import Mock, MagicMock
from app.agent import CodeAnalyzerAgent

@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    llm = Mock()
    # Mock the messages.create method
    llm.messages.create = Mock()
    return llm

def test_agent_extracts_issues_from_response(mock_llm):
    """Agent should parse issues from LLM response."""
    # Arrange: Define what LLM should return
    mock_response = Mock()
    mock_response.content = [Mock(text="""
    {
        "issues": ["SQL injection vulnerability", "Missing error handling"],
        "severity": "high",
        "recommendations": ["Use parameterized queries", "Add try-catch"]
    }
    """)]
    mock_llm.messages.create.return_value = mock_response

    agent = CodeAnalyzerAgent(llm=mock_llm)

    # Act
    result = agent.analyze("def query(id): return f'SELECT * FROM users WHERE id={id}'")

    # Assert
    assert len(result.issues) == 2
    assert "SQL injection" in result.issues[0]
    assert result.severity == "high"

    # Verify LLM was called
    mock_llm.messages.create.assert_called_once()

def test_agent_retries_on_invalid_json(mock_llm):
    """Agent should retry when LLM returns invalid JSON."""
    # First call returns invalid JSON, second call succeeds
    invalid_response = Mock()
    invalid_response.content = [Mock(text="Not JSON")]

    valid_response = Mock()
    valid_response.content = [Mock(text='{"issues": [], "severity": "low", "recommendations": []}')]

    mock_llm.messages.create.side_effect = [invalid_response, valid_response]

    agent = CodeAnalyzerAgent(llm=mock_llm, max_retries=2)

    # Should succeed on second try
    result = agent.analyze("def safe_function(): pass")

    assert result.severity == "low"
    assert mock_llm.messages.create.call_count == 2

def test_agent_handles_tool_use(mock_llm):
    """Agent should execute tools when LLM requests them."""
    # Mock LLM requesting a tool
    tool_request = Mock()
    tool_request.content = []
    tool_request.stop_reason = "tool_use"
    tool_request.content = [Mock(
        type="tool_use",
        id="tool_1",
        name="read_file",
        input={"path": "test.py"}
    )]

    final_response = Mock()
    final_response.content = [Mock(text="Analysis complete")]
    final_response.stop_reason = "end_turn"

    mock_llm.messages.create.side_effect = [tool_request, final_response]

    # Mock file system tool
    mock_fs_tool = Mock()
    mock_fs_tool.name = "read_file"
    mock_fs_tool.execute.return_value = "print('test')"

    agent = CodeAnalyzerAgent(llm=mock_llm, tools=[mock_fs_tool])

    result = agent.analyze("Analyze test.py")

    # Tool should have been executed
    mock_fs_tool.execute.assert_called_once_with(path="test.py")
```

</details>

**Level 3: Integration Tests with Real LLMs**

<details>
<summary><b>Python</b></summary>

```python
# tests/integration/test_real_llm.py
"""Integration tests with real LLM calls."""
import pytest
import os
from app.agent import CodeAnalyzerAgent
from anthropic import Anthropic

# Skip if no API key (for CI/CD)
pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="No API key available"
)

@pytest.fixture
def real_agent():
    """Create agent with real LLM."""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return CodeAnalyzerAgent(llm=client)

def test_detects_sql_injection(real_agent):
    """Should detect SQL injection vulnerabilities."""
    code = """
    def get_user(user_id):
        query = f"SELECT * FROM users WHERE id = {user_id}"
        return db.execute(query)
    """

    result = real_agent.analyze(code)

    # Check that SQL injection was detected
    issues_text = " ".join(result.issues).lower()
    assert "sql injection" in issues_text or "sql" in issues_text
    assert result.severity in ["high", "critical"]

def test_handles_safe_code(real_agent):
    """Should recognize safe code."""
    code = """
    def add(a: int, b: int) -> int:
        return a + b
    """

    result = real_agent.analyze(code)

    # Should find no critical issues
    assert result.severity in ["low", "none"]

@pytest.mark.slow  # Mark as slow test
def test_end_to_end_rag_system():
    """Test complete RAG pipeline."""
    from app.rag import RAGSystem

    # Initialize RAG with small test dataset
    rag = RAGSystem()
    rag.index_documents([
        "Python uses indentation for code blocks.",
        "JavaScript uses curly braces for code blocks.",
        "Both languages support functions and classes."
    ])

    # Query
    result = rag.query("How does Python structure code?")

    # Should mention indentation
    assert "indentation" in result.lower() or "indent" in result.lower()

    # Should retrieve relevant doc
    assert any("indentation" in doc.lower() for doc in result.source_documents)
```

</details>

**Level 4: Regression Testing for Prompts**

<details>
<summary><b>Python</b></summary>

```python
# tests/regression/test_prompt_regression.py
"""Regression tests to catch prompt changes breaking functionality."""
import pytest
import json
from pathlib import Path

# Load baseline results (generated from known-good prompts)
BASELINE_PATH = Path("tests/regression/baselines.json")

def load_baselines():
    """Load baseline test results."""
    if BASELINE_PATH.exists():
        with open(BASELINE_PATH) as f:
            return json.load(f)
    return {}

def save_baselines(baselines):
    """Save baseline test results."""
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BASELINE_PATH, "w") as f:
        json.dump(baselines, f, indent=2)

@pytest.fixture
def baselines():
    """Fixture providing baseline results."""
    return load_baselines()

def test_security_analysis_regression(real_agent, baselines):
    """Security analysis should be consistent with baseline."""
    test_id = "security_sql_injection"
    code = """
    def login(username, password):
        query = f"SELECT * FROM users WHERE user='{username}' AND pass='{password}'"
        return db.execute(query).fetchone()
    """

    result = real_agent.analyze(code)

    current = {
        "found_sql_injection": any("sql" in issue.lower() for issue in result.issues),
        "severity": result.severity
    }

    if test_id not in baselines:
        # First run: save baseline
        baselines[test_id] = current
        save_baselines(baselines)
        pytest.skip("Baseline established")

    baseline = baselines[test_id]

    # Compare with baseline
    assert current["found_sql_injection"] == baseline["found_sql_injection"], \
        "Regression: SQL injection detection changed"

    # Severity should be same or better
    severity_order = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    assert severity_order[current["severity"]] >= severity_order[baseline["severity"]], \
        f"Regression: Severity decreased from {baseline['severity']} to {current['severity']}"

# Regenerate baselines:
# pytest tests/regression --regenerate-baselines
```

</details>

**Testing Best Practices for AI Systems:**

| Practice | Why | How |
|----------|-----|-----|
| **Test deterministic parts** | Reliable, fast | Unit test parsing, validation, business logic |
| **Mock LLM for component tests** | Fast, cheap, consistent | Use fixtures with predefined responses |
| **Sample real LLM calls** | Catch real issues | Run subset in CI, full suite nightly |
| **Use regression tests** | Prevent prompt drift | Baseline important test cases |
| **Test error handling** | AI outputs fail often | Mock malformed JSON, timeouts, errors |
| **Version your prompts** | Track changes | Git version system prompts |
| **Log all LLM calls in tests** | Debug failures | Save request/response for failed tests |

**CI/CD Integration:**

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: pytest tests/ -m "not integration and not slow"
        # Fast, no API calls

  integration-tests:
    runs-on: ubuntu-latest
    # Only run on main branch (expensive)
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Run integration tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: pytest tests/integration/
        # Sample of real LLM calls

  regression-tests:
    runs-on: ubuntu-latest
    # Nightly only
    if: github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v3
      - name: Run regression suite
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: pytest tests/regression/
        # Full test against baselines
```

**Cost-Effective Testing Strategy:**

1. **Local Development**: Mock all LLM calls
2. **PR Validation**: Run 5-10 critical integration tests
3. **Main Branch**: Run full integration suite (30-50 tests)
4. **Nightly**: Run regression suite + regenerate baselines
5. **Pre-Release**: Manual E2E testing

**Example Test Suite Structure:**

```
tests/
├── unit/                    # Fast, no external calls (100+ tests)
│   ├── test_prompts.py
│   ├── test_parsing.py
│   └── test_chunking.py
├── component/               # Mocked LLM (50+ tests)
│   ├── test_agent.py
│   ├── test_rag.py
│   └── fixtures/
│       └── mock_responses.json
├── integration/             # Real LLM, subset (10-20 tests)
│   ├── test_critical_paths.py
│   └── test_security_detection.py
├── regression/              # Baseline comparison (20+ tests)
│   ├── test_regression.py
│   └── baselines.json
└── conftest.py             # Shared fixtures
```

---

<a name="observability"></a>
## 6. Debugging & Observability (45 min)

### 6.1 Tracing AI Systems

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Request Trace                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Request ID: req_abc123                                         │
│  Timestamp: 2024-01-15T10:30:00Z                                │
│  Duration: 1,234ms                                              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 1. Query Processing (50ms)                              │    │
│  │    Input: "How do I configure auth?"                    │    │
│  │    Transformed: "authentication configuration setup"    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 2. Embedding (120ms)                                    │    │
│  │    Model: text-embedding-3-small                        │    │
│  │    Tokens: 8                                            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 3. Retrieval (80ms)                                     │    │
│  │    Retrieved: 5 documents                               │    │
│  │    Top score: 0.89, Lowest: 0.71                        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ 4. Generation (980ms)                                   │    │
│  │    Model: claude-3-5-sonnet                             │    │
│  │    Input tokens: 2,400                                  │    │
│  │    Output tokens: 350                                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Logging Implementation

<details>
<summary><b>Python</b></summary>

```python
# observability/logging.py
"""Structured logging for RAG systems."""
import logging
import json
import time
from contextlib import contextmanager
from typing import Any, Dict
from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class RequestContext:
    """Context for a single request."""
    request_id: str = field(default_factory=lambda: str(uuid4()))
    spans: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)

class RAGLogger:
    """Structured logger for RAG systems."""

    def __init__(self, service_name: str = "rag"):
        self.service = service_name
        self.logger = logging.getLogger(service_name)
        self._context = None

    def start_request(self, query: str, metadata: Dict = None) -> RequestContext:
        """Start tracking a new request."""
        self._context = RequestContext(
            metadata=metadata or {}
        )
        self.log_event("request_start", {"query": query})
        return self._context

    def end_request(self, result: Any = None, error: str = None):
        """End request tracking."""
        duration = time.time() - self._context.start_time
        self.log_event("request_end", {
            "duration_ms": duration * 1000,
            "success": error is None,
            "error": error
        })
        self._context = None

    @contextmanager
    def span(self, name: str):
        """Track a span within a request."""
        start = time.time()
        span_data = {"name": name, "start": start}

        try:
            yield span_data
            span_data["success"] = True
        except Exception as e:
            span_data["success"] = False
            span_data["error"] = str(e)
            raise
        finally:
            span_data["duration_ms"] = (time.time() - start) * 1000
            self._context.spans.append(span_data)
            self.log_event("span_complete", span_data)

    def log_event(self, event_type: str, data: Dict):
        """Log a structured event."""
        log_data = {
            "service": self.service,
            "event": event_type,
            "request_id": self._context.request_id if self._context else None,
            "timestamp": time.time(),
            **data
        }
        self.logger.info(json.dumps(log_data))

    def log_retrieval(self, query: str, results: list, scores: list):
        """Log retrieval results."""
        self.log_event("retrieval", {
            "query": query,
            "num_results": len(results),
            "top_score": max(scores) if scores else None,
            "min_score": min(scores) if scores else None,
            "result_ids": [r.get('id') for r in results]
        })

    def log_generation(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float
    ):
        """Log generation details."""
        self.log_event("generation", {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": latency_ms
        })

# Usage
logger = RAGLogger()

def process_rag_query(query: str):
    ctx = logger.start_request(query)

    try:
        with logger.span("embedding"):
            embedding = get_embedding(query)

        with logger.span("retrieval"):
            results = vector_store.query(embedding, k=5)
            logger.log_retrieval(query, results, [r['score'] for r in results])

        with logger.span("generation"):
            response = llm.generate(query, results)
            logger.log_generation("claude-3-5-sonnet", 2400, 350, 980)

        logger.end_request(result=response)
        return response

    except Exception as e:
        logger.end_request(error=str(e))
        raise
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// observability/logging.ts
import { randomUUID } from 'crypto';

interface SpanData {
  name: string;
  start: number;
  durationMs?: number;
  success?: boolean;
  error?: string;
}

interface RequestContext {
  requestId: string;
  spans: SpanData[];
  metadata: Record<string, any>;
  startTime: number;
}

interface LogEvent {
  service: string;
  event: string;
  requestId: string | null;
  timestamp: number;
  [key: string]: any;
}

/**
 * Structured logger for RAG systems.
 */
class RAGLogger {
  private context: RequestContext | null = null;

  constructor(private service: string = 'rag') {}

  startRequest(query: string, metadata: Record<string, any> = {}): RequestContext {
    this.context = {
      requestId: randomUUID(),
      spans: [],
      metadata,
      startTime: performance.now(),
    };
    this.logEvent('request_start', { query });
    return this.context;
  }

  endRequest(result?: any, error?: string): void {
    if (!this.context) return;

    const durationMs = performance.now() - this.context.startTime;
    this.logEvent('request_end', {
      durationMs,
      success: error === undefined,
      error,
    });
    this.context = null;
  }

  async span<T>(name: string, fn: () => Promise<T>): Promise<T> {
    const start = performance.now();
    const spanData: SpanData = { name, start };

    try {
      const result = await fn();
      spanData.success = true;
      return result;
    } catch (e) {
      spanData.success = false;
      spanData.error = e instanceof Error ? e.message : String(e);
      throw e;
    } finally {
      spanData.durationMs = performance.now() - start;
      this.context?.spans.push(spanData);
      this.logEvent('span_complete', spanData);
    }
  }

  logEvent(eventType: string, data: Record<string, any>): void {
    const logData: LogEvent = {
      service: this.service,
      event: eventType,
      requestId: this.context?.requestId || null,
      timestamp: Date.now(),
      ...data,
    };
    console.log(JSON.stringify(logData));
  }

  logRetrieval(query: string, results: { id: string; score?: number }[]): void {
    const scores = results.map(r => r.score).filter((s): s is number => s !== undefined);
    this.logEvent('retrieval', {
      query,
      numResults: results.length,
      topScore: scores.length > 0 ? Math.max(...scores) : null,
      minScore: scores.length > 0 ? Math.min(...scores) : null,
      resultIds: results.map(r => r.id),
    });
  }

  logGeneration(model: string, inputTokens: number, outputTokens: number, latencyMs: number): void {
    this.logEvent('generation', {
      model,
      inputTokens,
      outputTokens,
      latencyMs,
    });
  }
}

// Usage example
const logger = new RAGLogger();

async function processRAGQuery(
  query: string,
  getEmbedding: (q: string) => Promise<number[]>,
  vectorStore: { query: (emb: number[], k: number) => Promise<{ id: string; score: number }[]> },
  llm: { generate: (q: string, ctx: any[]) => Promise<string> }
): Promise<string> {
  logger.startRequest(query);

  try {
    const embedding = await logger.span('embedding', () => getEmbedding(query));

    const results = await logger.span('retrieval', async () => {
      const docs = await vectorStore.query(embedding, 5);
      logger.logRetrieval(query, docs);
      return docs;
    });

    const response = await logger.span('generation', async () => {
      const start = performance.now();
      const result = await llm.generate(query, results);
      logger.logGeneration('claude-3-5-sonnet', 2400, 350, performance.now() - start);
      return result;
    });

    logger.endRequest(response);
    return response;
  } catch (e) {
    logger.endRequest(undefined, e instanceof Error ? e.message : String(e));
    throw e;
  }
}
```

</details>

### 6.3 Cost Monitoring

<details>
<summary><b>Python</b></summary>

```python
# observability/cost.py
"""Track and monitor LLM costs."""
from dataclasses import dataclass
from typing import Dict
from datetime import datetime, timedelta

# Pricing per 1M tokens (as of 2024)
PRICING = {
    "gpt-4o": {"input": 5.0, "output": 15.0},
    "gpt-4-turbo": {"input": 10.0, "output": 30.0},
    "claude-3-5-sonnet": {"input": 3.0, "output": 15.0},
    "claude-3-opus": {"input": 15.0, "output": 75.0},
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
    "text-embedding-3-large": {"input": 0.13, "output": 0.0},
}

@dataclass
class Usage:
    """Token usage record."""
    model: str
    input_tokens: int
    output_tokens: int
    timestamp: datetime
    request_id: str = None

class CostTracker:
    """Track and monitor LLM costs."""

    def __init__(self):
        self.usage_history: list[Usage] = []
        self.daily_budget: float = 100.0  # Default daily budget

    def record_usage(self, usage: Usage):
        """Record token usage."""
        self.usage_history.append(usage)

    def calculate_cost(self, usage: Usage) -> float:
        """Calculate cost for a usage record."""
        if usage.model not in PRICING:
            return 0.0

        pricing = PRICING[usage.model]
        input_cost = (usage.input_tokens / 1_000_000) * pricing["input"]
        output_cost = (usage.output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def get_daily_cost(self, date: datetime = None) -> float:
        """Get total cost for a specific day."""
        if date is None:
            date = datetime.now()

        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        return sum(
            self.calculate_cost(u)
            for u in self.usage_history
            if day_start <= u.timestamp < day_end
        )

    def get_budget_status(self) -> Dict:
        """Get current budget status."""
        daily_cost = self.get_daily_cost()
        return {
            "daily_budget": self.daily_budget,
            "daily_spent": daily_cost,
            "daily_remaining": self.daily_budget - daily_cost,
            "percentage_used": (daily_cost / self.daily_budget) * 100,
            "alert": daily_cost > self.daily_budget * 0.8
        }

    def get_cost_breakdown(self, days: int = 7) -> Dict:
        """Get cost breakdown by model over time."""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [u for u in self.usage_history if u.timestamp > cutoff]

        breakdown = {}
        for usage in recent:
            if usage.model not in breakdown:
                breakdown[usage.model] = {
                    "total_cost": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "request_count": 0
                }
            breakdown[usage.model]["total_cost"] += self.calculate_cost(usage)
            breakdown[usage.model]["input_tokens"] += usage.input_tokens
            breakdown[usage.model]["output_tokens"] += usage.output_tokens
            breakdown[usage.model]["request_count"] += 1

        return breakdown
```

</details>

<details>
<summary><b>TypeScript</b></summary>

```typescript
// observability/cost.ts

// Pricing per 1M tokens (as of 2024)
const PRICING: Record<string, { input: number; output: number }> = {
  'gpt-4o': { input: 5.0, output: 15.0 },
  'gpt-4-turbo': { input: 10.0, output: 30.0 },
  'claude-3-5-sonnet': { input: 3.0, output: 15.0 },
  'claude-3-opus': { input: 15.0, output: 75.0 },
  'text-embedding-3-small': { input: 0.02, output: 0.0 },
  'text-embedding-3-large': { input: 0.13, output: 0.0 },
};

interface Usage {
  model: string;
  inputTokens: number;
  outputTokens: number;
  timestamp: Date;
  requestId?: string;
}

interface BudgetStatus {
  dailyBudget: number;
  dailySpent: number;
  dailyRemaining: number;
  percentageUsed: number;
  alert: boolean;
}

interface ModelBreakdown {
  totalCost: number;
  inputTokens: number;
  outputTokens: number;
  requestCount: number;
}

/**
 * Track and monitor LLM costs.
 */
class CostTracker {
  private usageHistory: Usage[] = [];
  private dailyBudget: number = 100.0;

  recordUsage(usage: Usage): void {
    this.usageHistory.push(usage);
  }

  calculateCost(usage: Usage): number {
    const pricing = PRICING[usage.model];
    if (!pricing) return 0;

    const inputCost = (usage.inputTokens / 1_000_000) * pricing.input;
    const outputCost = (usage.outputTokens / 1_000_000) * pricing.output;
    return inputCost + outputCost;
  }

  getDailyCost(date: Date = new Date()): number {
    const dayStart = new Date(date);
    dayStart.setHours(0, 0, 0, 0);

    const dayEnd = new Date(dayStart);
    dayEnd.setDate(dayEnd.getDate() + 1);

    return this.usageHistory
      .filter(u => u.timestamp >= dayStart && u.timestamp < dayEnd)
      .reduce((sum, u) => sum + this.calculateCost(u), 0);
  }

  getBudgetStatus(): BudgetStatus {
    const dailySpent = this.getDailyCost();
    return {
      dailyBudget: this.dailyBudget,
      dailySpent,
      dailyRemaining: this.dailyBudget - dailySpent,
      percentageUsed: (dailySpent / this.dailyBudget) * 100,
      alert: dailySpent > this.dailyBudget * 0.8,
    };
  }

  getCostBreakdown(days: number = 7): Record<string, ModelBreakdown> {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);

    const recent = this.usageHistory.filter(u => u.timestamp > cutoff);

    const breakdown: Record<string, ModelBreakdown> = {};

    for (const usage of recent) {
      if (!breakdown[usage.model]) {
        breakdown[usage.model] = {
          totalCost: 0,
          inputTokens: 0,
          outputTokens: 0,
          requestCount: 0,
        };
      }

      breakdown[usage.model].totalCost += this.calculateCost(usage);
      breakdown[usage.model].inputTokens += usage.inputTokens;
      breakdown[usage.model].outputTokens += usage.outputTokens;
      breakdown[usage.model].requestCount += 1;
    }

    return breakdown;
  }

  setDailyBudget(budget: number): void {
    this.dailyBudget = budget;
  }
}

// Usage example
const costTracker = new CostTracker();

// Record usage after each LLM call
costTracker.recordUsage({
  model: 'claude-3-5-sonnet',
  inputTokens: 2400,
  outputTokens: 350,
  timestamp: new Date(),
  requestId: 'req_123',
});

// Check budget status
const status = costTracker.getBudgetStatus();
console.log(`Daily spend: $${status.dailySpent.toFixed(4)}`);
console.log(`Budget used: ${status.percentageUsed.toFixed(1)}%`);

if (status.alert) {
  console.warn('Warning: Approaching daily budget limit!');
}

// Get breakdown by model
const breakdown = costTracker.getCostBreakdown(7);
for (const [model, data] of Object.entries(breakdown)) {
  console.log(`${model}: $${data.totalCost.toFixed(4)} (${data.requestCount} requests)`);
}
```

</details>

### 6.4 Common Debugging Patterns

```markdown
## RAG Debugging Playbook

### Symptom: Wrong answers
1. Check retrieved documents
   - Are relevant docs being retrieved?
   - What are the similarity scores?
2. Check if answer is in retrieved docs
3. Examine prompt construction
4. Test with fewer/more retrieved docs

### Symptom: "I don't know" when answer exists
1. Check embeddings
   - Is query being embedded correctly?
   - Test with exact phrase from document
2. Check chunk boundaries
   - Is answer split across chunks?
3. Try query reformulation
4. Check similarity threshold

### Symptom: Slow responses
1. Profile each stage
   - Embedding time
   - Retrieval time
   - Generation time
2. Check index size and configuration
3. Consider caching strategies
4. Evaluate model choice

### Symptom: High costs
1. Review model selection
   - Using expensive model for simple tasks?
2. Check context sizes
   - Sending too much context?
3. Implement caching
4. Consider local embeddings
```

---

<a name="lab-04"></a>
## 7. Lab 04: Build & Evaluate RAG System (1h 45min)

### Lab Overview

**Goal:** Build a complete RAG system with evaluation for querying a codebase.

**The system will:**
1. Index Python/TypeScript source files
2. Support semantic code search
3. Answer questions about the code
4. Include evaluation metrics

### Lab Instructions

Navigate to `labs/lab04-rag-system/` and follow the README.

**Quick Start:**
```bash
cd labs/lab04-rag-system
cat README.md
# Follow steps to build the RAG system
```

### Expected Outcome

By the end of this lab, you should have:
1. A working code RAG system
2. Evaluation dataset and metrics
3. Observability/logging setup
4. Deployment to Railway

---

## Day 4 Summary

### What We Covered
1. **RAG Fundamentals**: Embeddings, vector stores, retrieval
2. **Chunking Strategies**: Fixed, semantic, code-aware
3. **RAG Pitfalls**: Common failures and solutions
4. **Evaluation**: Retrieval metrics, LLM-as-judge, datasets
5. **Observability**: Logging, tracing, cost monitoring

### Key Takeaways
- RAG grounds LLM responses in specific data
- Chunking strategy significantly impacts quality
- Hybrid search often outperforms pure vector search
- Evaluation is essential—don't ship without it
- Monitor costs and latency in production

### Resources You Should Have
- [ ] RAG architecture diagram
- [ ] Chunking strategy comparison
- [ ] Evaluation dataset (10+ examples)
- [ ] Logging/tracing setup

### Preparation for Day 5
- Think about production concerns (security, scaling)
- Review all labs—capstone builds on everything
- Consider which capstone option interests you

---

**Navigation**: [← Day 3](./day3-agents.md) | [Day 5: Production & Capstone →](./day5-production.md)
