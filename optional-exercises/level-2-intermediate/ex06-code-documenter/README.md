# Exercise 06: Auto Code Documenter

## Description
Generate automatic documentation (docstrings, comments, README) by analyzing code with LLMs.

## Objectives
- Parse code (AST) to extract functions/classes
- Generate contextually relevant docstrings
- Create README based on codebase
- Maintain style consistency

## Quick Start

```python
from ast import parse, FunctionDef, ClassDef
import anthropic

class CodeDocumenter:
    def document_function(self, function_code: str) -> str:
        prompt = f"""
Generate a comprehensive docstring for this function:

{function_code}

Include:
- Brief description
- Parameters with types
- Return value
- Example usage
"""
        return client.messages.create(
            model="claude-sonnet-4",
            messages=[{"role": "user", "content": prompt}]
        ).content[0].text

# Usage
documenter = CodeDocumenter()
docstring = documenter.document_function("""
def calculate_total(items, tax_rate=0.1):
    subtotal = sum(item['price'] for item in items)
    return subtotal * (1 + tax_rate)
""")
```

## Features
- [ ] Auto-detect programming language
- [ ] Generate Google/NumPy style docstrings
- [ ] Type hints inference
- [ ] Example generation
- [ ] Batch processing

## Advanced
- Multi-language support (Python, TS, Go)
- Integration with pre-commit hooks
- Docstring quality scoring
- Auto-update stale documentation

**Time**: 4-5h
