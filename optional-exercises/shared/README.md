# Shared Resources

This directory contains shared resources that can be used by multiple exercises.

---

## Structure

```
shared/
├── templates/         # Project templates and boilerplates
├── utils/            # Reusable helper functions
├── datasets/         # Test data and examples
├── docker/           # Docker configurations
└── scripts/          # Setup and deployment scripts
```

---

## Utils

### Python Utilities

#### `llm_client.py`
Unified client for multiple LLM providers:

```python
from shared.utils.llm_client import UnifiedLLMClient

client = UnifiedLLMClient()

# Automatically uses best available provider
response = await client.complete("Hello, world!")
```

#### `token_counter.py`
Multi-provider token counter:

```python
from shared.utils.token_counter import count_tokens

tokens = count_tokens("Your text here", model="gpt-4")
cost = calculate_cost(tokens, model="gpt-4")
```

#### `embeddings.py`
Embedding generation:

```python
from shared.utils.embeddings import get_embeddings

embeddings = await get_embeddings([
    "First text",
    "Second text"
])
```

### TypeScript Utilities

#### `llm-client.ts`
```typescript
import { UnifiedLLMClient } from '@shared/utils/llm-client';

const client = new UnifiedLLMClient();
const response = await client.complete('Hello');
```

#### `token-counter.ts`
```typescript
import { countTokens, calculateCost } from '@shared/utils/token-counter';

const tokens = countTokens('Your text', 'gpt-4');
const cost = calculateCost(tokens, 'gpt-4');
```

---

## Templates

### Python FastAPI Template

```bash
shared/templates/fastapi-template/
├── app/
│   ├── main.py
│   ├── routers/
│   ├── models/
│   └── services/
├── tests/
├── requirements.txt
└── Dockerfile
```

Usage:
```bash
cp -r shared/templates/fastapi-template my-project
cd my-project
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Next.js + TypeScript Template

```bash
shared/templates/nextjs-template/
├── app/
├── components/
├── lib/
├── package.json
└── tsconfig.json
```

Usage:
```bash
cp -r shared/templates/nextjs-template my-project
cd my-project
npm install
npm run dev
```

### Electron + React Template

```bash
shared/templates/electron-template/
├── src/
│   ├── main/       # Electron main process
│   └── renderer/   # React app
├── package.json
└── electron.config.js
```

---

## Datasets

### Code Samples

`datasets/code-samples/` - Collection of code snippets for testing:
- Python functions
- TypeScript/JavaScript
- Go
- Rust
- Various complexity levels

### Test Queries

`datasets/test-queries.json` - Standard test queries for search/RAG systems:

```json
{
  "simple": [
    "What is Python?",
    "How to sort a list?"
  ],
  "complex": [
    "Explain the differences between async and sync programming",
    "Design a rate limiting system"
  ],
  "code": [
    "Write a function to detect palindromes",
    "Implement binary search in Python"
  ]
}
```

### Evaluation Datasets

`datasets/evaluation/` - Datasets for testing:
- `hallucination-test-cases.json` - Known hallucination examples
- `rag-ground-truth.json` - Question-answer pairs with sources
- `code-review-examples.json` - Code with known issues

---

## Docker Configurations

### Vector Database

`docker/qdrant/docker-compose.yml`:

```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_storage:/qdrant/storage
```

Usage:
```bash
cd shared/docker/qdrant
docker-compose up -d
```

### Full Stack

`docker/full-stack/docker-compose.yml`:

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/dbname

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

  db:
    image: postgres:14
    environment:
      - POSTGRES_PASSWORD=pass

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

---

## Scripts

### Setup Script

`scripts/setup.sh`:

```bash
#!/bin/bash
# Setup environment for exercises

# Check Python version
python3 --version || { echo "Python 3.9+ required"; exit 1; }

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install common dependencies
pip install anthropic openai tiktoken python-dotenv

# Setup .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Edit .env with your API keys"
fi

echo "✅ Setup complete!"
```

### Test Runner

`scripts/run-tests.sh`:

```bash
#!/bin/bash
# Run tests for all exercises

for dir in level-*-*/ex*/; do
    if [ -f "$dir/tests" ]; then
        echo "Testing $dir..."
        cd "$dir"
        pytest
        cd -
    fi
done
```

### Deployment Script

`scripts/deploy.sh`:

```bash
#!/bin/bash
# Deploy to Railway/Vercel

PROJECT_NAME=$1

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: ./deploy.sh <project-name>"
    exit 1
fi

# Deploy backend to Railway
railway link $PROJECT_NAME-backend
railway up

# Deploy frontend to Vercel
vercel --prod

echo "✅ Deployed!"
```

---

## Usage Examples

### Using Shared Utils in Your Exercise

Python:
```python
# Add to sys.path if needed
import sys
sys.path.append('../../shared/utils')

from llm_client import UnifiedLLMClient
from token_counter import count_tokens

client = UnifiedLLMClient()
# Use client...
```

TypeScript:
```typescript
// Add to tsconfig.json:
{
  "compilerOptions": {
    "paths": {
      "@shared/*": ["../../shared/utils/*"]
    }
  }
}

// Then import:
import { UnifiedLLMClient } from '@shared/llm-client';
```

### Using Templates

```bash
# Copy template
cp -r shared/templates/fastapi-template exercises/my-exercise

# Customize
cd exercises/my-exercise
# Edit files...

# Run
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Contributing Shared Resources

Found a utility that multiple exercises could use? Contribute it!

1. Create the utility in `shared/utils/`
2. Add documentation to this README
3. Add tests in `shared/utils/tests/`
4. Submit PR

---

## Available Helper Functions

### LLM Operations
- `complete()` - Single completion
- `complete_streaming()` - Streaming response
- `complete_with_retry()` - Auto retry on failure
- `batch_complete()` - Batch processing

### Token Management
- `count_tokens()` - Count tokens for text
- `calculate_cost()` - Estimate API cost
- `truncate_to_tokens()` - Truncate text to limit
- `split_by_tokens()` - Chunk text by tokens

### Embeddings
- `get_embeddings()` - Generate embeddings
- `similarity()` - Cosine similarity
- `semantic_search()` - Search with embeddings

### Caching
- `cache_llm_call()` - Decorator for caching
- `semantic_cache_get()` - Semantic cache lookup
- `semantic_cache_set()` - Store in semantic cache

### Utilities
- `retry_with_backoff()` - Retry with exponential backoff
- `rate_limit()` - Rate limiting decorator
- `measure_time()` - Performance measurement
- `validate_json()` - JSON validation

---

## Shared Dependencies

Common dependencies across exercises:

**Python**:
```txt
anthropic>=0.18.0
openai>=1.0.0
tiktoken>=0.5.0
python-dotenv>=1.0.0
fastapi>=0.104.0
uvicorn>=0.24.0
pytest>=7.4.0
```

**Node.js**:
```json
{
  "@anthropic-ai/sdk": "^0.18.0",
  "openai": "^4.0.0",
  "tiktoken": "^1.0.0",
  "dotenv": "^16.0.0"
}
```

---

**Questions?** Open an issue on GitHub
