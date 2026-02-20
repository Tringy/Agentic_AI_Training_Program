# Challenge 03: Intelligent Codebase Search Engine

## Description

Build an advanced search engine for codebases that understands natural language queries, code, and context.

**Difficulty**: Expert
**Estimated time**: 35-45 hours
**Stack**: Python + FastAPI + Qdrant + React

---

## Objectives

Search engine that supports:
- ✅ Natural language queries ("Find authentication logic")
- ✅ Code search (function signatures, patterns)
- ✅ Semantic understanding (find similar code)
- ✅ Multi-modal (code + docs + issues + PRs)
- ✅ Automatic query expansion
- ✅ Real-time indexing
- ✅ Explain results (why this result?)

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              Frontend (React)                │
│  - Search bar with autocomplete             │
│  - Filters (language, file type, date)      │
│  - Results with context highlighting        │
│  - Visual code graph                         │
└─────────────────────────────────────────────┘
                     │
                     │ REST API
                     ▼
┌─────────────────────────────────────────────┐
│           Backend (FastAPI)                  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │      Query Understanding              │  │
│  │  - Parse natural language             │  │
│  │  - Extract intent                     │  │
│  │  - Query expansion                    │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │      Hybrid Search Engine            │  │
│  │  - Vector search (semantic)          │  │
│  │  - Keyword search (BM25)             │  │
│  │  - Graph search (dependencies)       │  │
│  │  - Fusion ranking                    │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │      Indexing Pipeline               │  │
│  │  - Code parsing (AST)                │  │
│  │  - Embedding generation              │  │
│  │  - Dependency graph                  │  │
│  │  - Real-time updates                 │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│           Storage Layer                      │
│  - Qdrant (vector search)                   │
│  - PostgreSQL (metadata)                    │
│  - Redis (caching)                          │
│  - Neo4j (code graph) - optional            │
└─────────────────────────────────────────────┘
```

---

## Core Features

### 1. Natural Language Query Understanding

```python
class QueryUnderstanding:
    async def parse_query(self, query: str) -> ParsedQuery:
        """Understand user intent"""

        # Detect query type
        query_type = await self._detect_type(query)

        # Extract entities
        entities = await self._extract_entities(query)

        # Expand query
        expanded = await self._expand_query(query)

        return ParsedQuery(
            original=query,
            type=query_type,
            entities=entities,
            expanded_terms=expanded
        )

    async def _detect_type(self, query: str) -> QueryType:
        """Classify query intent"""
        prompt = f"""
Classify this search query:

"{query}"

Types:
- FUNCTION_SEARCH: Looking for a specific function
- CONCEPT_SEARCH: Looking for how something works
- BUG_SEARCH: Looking for bug-related code
- SIMILAR_CODE: Looking for similar implementations
- DEFINITION: Looking for where something is defined

Output just the type.
"""

        response = await llm.complete(prompt)
        return QueryType(response.strip())

    async def _expand_query(self, query: str) -> List[str]:
        """Generate related search terms"""
        prompt = f"""
Given this search query: "{query}"

Generate 5 related search terms that would help find relevant code.

Examples:
Query: "authentication"
Related: ["auth", "login", "jwt", "session", "user verification"]
"""

        response = await llm.complete(prompt)
        return self._parse_terms(response)
```

### 2. Hybrid Search Engine

```python
class HybridSearchEngine:
    def __init__(self):
        self.vector_search = QdrantSearch()
        self.keyword_search = BM25Search()
        self.graph_search = GraphSearch()

    async def search(
        self,
        query: ParsedQuery,
        filters: SearchFilters
    ) -> List[SearchResult]:
        # Run searches in parallel
        vector_results, keyword_results, graph_results = await asyncio.gather(
            self.vector_search.search(query.expanded_terms, filters),
            self.keyword_search.search(query.original, filters),
            self.graph_search.search(query.entities, filters)
        )

        # Reciprocal Rank Fusion
        fused = self._reciprocal_rank_fusion([
            vector_results,
            keyword_results,
            graph_results
        ])

        # Rerank with LLM
        reranked = await self._rerank(query, fused)

        return reranked

    def _reciprocal_rank_fusion(
        self,
        result_lists: List[List[SearchResult]],
        k: int = 60
    ) -> List[SearchResult]:
        """Combine multiple ranked lists"""
        scores = {}

        for results in result_lists:
            for rank, result in enumerate(results):
                if result.id not in scores:
                    scores[result.id] = 0

                scores[result.id] += 1 / (rank + k)

        # Sort by fused score
        sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Return results in fused order
        return [self._get_result_by_id(id) for id, _ in sorted_ids]

    async def _rerank(
        self,
        query: ParsedQuery,
        results: List[SearchResult]
    ) -> List[SearchResult]:
        """LLM-based reranking"""
        # Take top 20 for reranking
        candidates = results[:20]

        prompt = f"""
Query: "{query.original}"

Rank these search results by relevance (1 = most relevant):

{self._format_candidates(candidates)}

Output: comma-separated IDs in order
"""

        response = await llm.complete(prompt)
        reranked_ids = response.strip().split(',')

        # Reorder results
        id_to_result = {r.id: r for r in candidates}
        return [id_to_result[id] for id in reranked_ids if id in id_to_result]
```

### 3. Advanced Indexing

```python
class CodeIndexer:
    async def index_repository(self, repo_path: str):
        """Index entire repository"""
        print(f"📚 Indexing {repo_path}...")

        # 1. Scan files
        files = self._scan_code_files(repo_path)
        print(f"Found {len(files)} files")

        # 2. Parse code structure
        parsed = await self._parse_files(files)

        # 3. Extract functions/classes
        entities = self._extract_entities(parsed)

        # 4. Build dependency graph
        graph = self._build_dependency_graph(entities)

        # 5. Generate embeddings
        embeddings = await self._generate_embeddings(entities)

        # 6. Store in vector DB
        await self._store_vectors(embeddings)

        # 7. Index metadata
        await self._store_metadata(entities, graph)

        print("✅ Indexing complete")

    def _extract_entities(self, parsed_files):
        """Extract functions, classes, variables"""
        entities = []

        for file in parsed_files:
            tree = ast.parse(file.content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    entities.append(FunctionEntity(
                        name=node.name,
                        file=file.path,
                        line_start=node.lineno,
                        line_end=node.end_lineno,
                        signature=self._get_signature(node),
                        docstring=ast.get_docstring(node),
                        code=ast.unparse(node)
                    ))

                elif isinstance(node, ast.ClassDef):
                    entities.append(ClassEntity(
                        name=node.name,
                        file=file.path,
                        line_start=node.lineno,
                        methods=self._extract_methods(node),
                        code=ast.unparse(node)
                    ))

        return entities

    async def _generate_embeddings(self, entities):
        """Generate embeddings for code entities"""
        embeddings = []

        for entity in entities:
            # Combine code + docstring + context
            text = f"""
{entity.docstring or ''}

{entity.code}
"""

            embedding = await self.embed_model.embed(text)

            embeddings.append({
                "id": entity.id,
                "vector": embedding,
                "payload": {
                    "file": entity.file,
                    "name": entity.name,
                    "type": entity.type,
                    "code": entity.code
                }
            })

        return embeddings
```

### 4. Real-Time Indexing

```python
class RealtimeIndexer:
    """Watch for file changes and reindex"""

    def __init__(self):
        self.observer = Observer()
        self.indexer = CodeIndexer()

    def start_watching(self, repo_path: str):
        event_handler = CodeChangeHandler(self.indexer)

        self.observer.schedule(
            event_handler,
            repo_path,
            recursive=True
        )

        self.observer.start()

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self, indexer):
        self.indexer = indexer
        self.debounce_timer = {}

    def on_modified(self, event):
        if event.is_directory:
            return

        # Debounce rapid changes
        file_path = event.src_path
        if file_path in self.debounce_timer:
            self.debounce_timer[file_path].cancel()

        timer = Timer(2.0, lambda: self._reindex_file(file_path))
        self.debounce_timer[file_path] = timer
        timer.start()

    async def _reindex_file(self, file_path: str):
        print(f"🔄 Reindexing {file_path}")
        await self.indexer.index_file(file_path)
```

### 5. Query Explanation

```python
class ResultExplainer:
    """Explain why results were returned"""

    async def explain(
        self,
        query: str,
        result: SearchResult
    ) -> Explanation:
        prompt = f"""
Explain why this search result matches the query:

Query: "{query}"

Result:
File: {result.file}
Code:
{result.code}

Provide:
1. Relevance reason
2. Key matching concepts
3. Confidence score (0-1)
"""

        response = await llm.complete(prompt)

        return Explanation(
            reason=self._extract_reason(response),
            concepts=self._extract_concepts(response),
            confidence=self._extract_confidence(response)
        )
```

---

## Advanced Features

### 1. Code Graph Navigation

```python
# Find all functions that call this function
def find_callers(function_name: str):
    query = """
    MATCH (caller:Function)-[:CALLS]->(callee:Function {name: $name})
    RETURN caller
    """
    return graph.query(query, name=function_name)

# Find dependency chain
def find_dependency_chain(start: str, end: str):
    query = """
    MATCH path = shortestPath(
        (start:Module {name: $start})-[:IMPORTS*]->(end:Module {name: $end})
    )
    RETURN path
    """
    return graph.query(query, start=start, end=end)
```

### 2. Semantic Code Similarity

```python
async def find_similar_code(code_snippet: str, top_k: int = 10):
    """Find semantically similar code"""

    # Generate embedding
    embedding = await embed_model.embed(code_snippet)

    # Search
    results = await vector_db.search(
        collection="code_chunks",
        query_vector=embedding,
        limit=top_k,
        score_threshold=0.7
    )

    return [
        SimilarCode(
            code=r.payload["code"],
            file=r.payload["file"],
            similarity=r.score
        )
        for r in results
    ]
```

### 3. Multi-Repository Search

```python
class MultiRepoSearch:
    def __init__(self):
        self.indexes = {}  # repo_id -> Index

    async def search_across_repos(
        self,
        query: str,
        repos: List[str]
    ):
        # Search each repo
        results_by_repo = await asyncio.gather(*[
            self.indexes[repo].search(query)
            for repo in repos
        ])

        # Merge and rank
        all_results = []
        for repo, results in zip(repos, results_by_repo):
            for r in results:
                r.repo = repo
                all_results.append(r)

        return sorted(all_results, key=lambda r: r.score, reverse=True)
```

---

## Testing

```python
async def test_natural_language_search():
    results = await search_engine.search(
        "Find authentication logic"
    )

    assert len(results) > 0
    assert any('auth' in r.file.lower() for r in results)

async def test_semantic_search():
    results = await search_engine.search(
        "Calculate fibonacci sequence"
    )

    # Should find fibonacci implementations
    assert any('fibonacci' in r.code.lower() for r in results)

async def test_hybrid_search():
    # Should combine keyword + semantic
    results = await search_engine.search(
        "fast sorting algorithm"
    )

    assert len(results) > 0
```

---

## Evaluation

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Search Quality** | 40% | Relevant results for diverse queries |
| **Performance** | 20% | < 200ms query latency |
| **Indexing** | 15% | Handles large codebases |
| **UX** | 15% | Intuitive interface |
| **Innovation** | 10% | Unique features |

---

## Bonus Features

- 🔥 Code navigation (go to definition)
- 🔥 Search history & suggestions
- 🔥 Saved searches
- 🔥 Search analytics
- 🔥 API for IDE integration
- 🔥 Export search results

---

**¡Busca código como nunca antes! 🔍**
