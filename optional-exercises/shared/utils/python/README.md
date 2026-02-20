# Shared Utilities - Python

Consolidated utilities for the AI Training Program. Eliminates code duplication across labs and exercises.

## Installation

```bash
# From this directory
pip install -e .

# Now importable from anywhere
from shared_utils import UnifiedLLMClient, extract_json
```

## Quick Start

```python
from shared_utils import UnifiedLLMClient, extract_json

# Create client (auto-selects free provider)
client = UnifiedLLMClient()

# Chat
response = client.chat([
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Explain LLMs in one sentence"}
])

# Parse JSON if needed
data = extract_json(response)
```

## Available Utilities

### LLM Client (`llm_client.py`)
- `UnifiedLLMClient()` - Auto-selecting client
- `get_llm_client(provider)` - Get specific provider
- `get_free_llm_client(provider)` - Free providers only
- Supports: Google, Groq, Ollama (free), Anthropic, OpenAI (paid)

### Response Parsing (`parsing.py`)
- `extract_json(response)` - Extract JSON from markdown
- `extract_code_block(response, language)` - Extract code
- `extract_all_code_blocks(response)` - Get all code blocks
- `clean_response(response)` - Remove LLM artifacts
- `validate_json_schema(data, required_keys)` - Validate structure

## Examples

See individual module files for comprehensive examples and tests.

## Usage in Labs

```python
# In any lab exercise
import sys
sys.path.append('../../../optional-exercises/shared/utils/python')

from shared_utils import get_llm_client, extract_json

client = get_llm_client("google")
# Use client...
```

Or install package:
```bash
cd optional-exercises/shared/utils/python
pip install -e .

# Now works everywhere without sys.path
from shared_utils import UnifiedLLMClient
```

## Testing

```bash
# Test LLM client
python -m shared_utils.llm_client

# Test parsing
python -m shared_utils.parsing
```
