"""
Response Parsing Utilities
===========================

Utilities for extracting structured data from LLM responses.

LLMs often wrap JSON in markdown code blocks or include extra text.
These utilities handle common parsing patterns found across all labs.

Consolidates 3+ duplicated implementations from:
    - lab02-code-analyzer-agent/python/analyzer.py
    - lab03-migration-workflow/python/agent.py
    - lab05-multi-agent/python/ (various)

Usage:
    from shared_utils.parsing import extract_json, extract_code_block

    # Extract JSON from LLM response
    response = client.chat(messages)
    data = extract_json(response)

    # Extract code from markdown
    code = extract_code_block(response, language="python")
"""

import json
import re
from typing import Any, Dict, Optional, List


def extract_json(response: str, strict: bool = False) -> Dict[str, Any]:
    """
    Extract JSON from LLM response, handling markdown code blocks.

    LLMs often wrap JSON in markdown like:
        ```json
        {"key": "value"}
        ```

    This function extracts the JSON regardless of wrapping.

    Args:
        response: Raw LLM response text
        strict: If True, raise error on invalid JSON. If False, return empty dict.

    Returns:
        Parsed JSON object as dictionary

    Raises:
        ValueError: If strict=True and no valid JSON found

    Examples:
        >>> response = '''Here's the data:
        ... ```json
        ... {"name": "test", "value": 42}
        ... ```'''
        >>> data = extract_json(response)
        >>> print(data)
        {'name': 'test', 'value': 42}

        >>> # Without code blocks
        >>> response = '{"simple": "json"}'
        >>> data = extract_json(response)
        >>> print(data)
        {'simple': 'json'}
    """
    # Step 1: Remove markdown code blocks
    cleaned = response

    if "```json" in cleaned:
        # Extract from ```json ... ``` block
        cleaned = cleaned.split("```json")[1].split("```")[0]
    elif "```" in cleaned:
        # Try to find JSON in any code block
        cleaned = cleaned.split("```")[1].split("```")[0]

    # Step 2: Strip whitespace
    cleaned = cleaned.strip()

    # Step 3: Try direct parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Step 4: Try to find JSON object/array with regex
    # Look for {...} or [...]
    json_match = re.search(r'(\{.*\}|\[.*\])', cleaned, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Step 5: Handle failure
    if strict:
        raise ValueError(
            f"Could not extract valid JSON from response. "
            f"First 200 chars: {response[:200]}..."
        )

    # Return empty dict if not strict
    return {}


def extract_json_array(response: str, strict: bool = False) -> List[Dict[str, Any]]:
    """
    Extract JSON array from LLM response.

    Similar to extract_json but ensures result is a list.

    Args:
        response: Raw LLM response
        strict: Raise error if not valid JSON array

    Returns:
        List of dictionaries

    Examples:
        >>> response = '''[
        ... {"id": 1, "name": "item1"},
        ... {"id": 2, "name": "item2"}
        ... ]'''
        >>> items = extract_json_array(response)
        >>> len(items)
        2
    """
    result = extract_json(response, strict=strict)

    if isinstance(result, list):
        return result
    elif isinstance(result, dict):
        # Single object, wrap in list
        return [result]
    else:
        return [] if not strict else []


def extract_code_block(
    response: str,
    language: Optional[str] = None,
    fallback_to_full: bool = True
) -> str:
    """
    Extract code block from markdown response.

    LLMs often return code in markdown format like:
        ```python
        def hello():
            return "world"
        ```

    Args:
        response: Raw LLM response
        language: Specific language to extract (None = any code block)
        fallback_to_full: If no code block found, return full response

    Returns:
        Extracted code as string

    Examples:
        >>> response = '''Here's the code:
        ... ```python
        ... def add(a, b):
        ...     return a + b
        ... ```'''
        >>> code = extract_code_block(response, language="python")
        >>> print(code)
        def add(a, b):
            return a + b

        >>> # Extract any code block
        >>> code = extract_code_block(response)
    """
    if language:
        # Look for specific language
        pattern = f"```{language}\\n(.*?)```"
    else:
        # Look for any code block
        pattern = r"```(?:\w+)?\n(.*?)```"

    match = re.search(pattern, response, re.DOTALL)
    if match:
        return match.group(1).strip()

    # No code block found
    if fallback_to_full:
        # Return entire response, stripped
        return response.strip()
    else:
        return ""


def extract_all_code_blocks(response: str) -> List[Dict[str, str]]:
    """
    Extract all code blocks from response with language tags.

    Args:
        response: LLM response potentially containing multiple code blocks

    Returns:
        List of dicts with 'language' and 'code' keys

    Examples:
        >>> response = '''
        ... ```python
        ... def hello(): pass
        ... ```
        ... And in JavaScript:
        ... ```javascript
        ... function hello() {}
        ... ```'''
        >>> blocks = extract_all_code_blocks(response)
        >>> len(blocks)
        2
        >>> blocks[0]['language']
        'python'
    """
    blocks = []

    # Find all code blocks
    pattern = r"```(\w+)?\n(.*?)```"

    for match in re.finditer(pattern, response, re.DOTALL):
        language = match.group(1) or "unknown"
        code = match.group(2).strip()

        blocks.append({
            "language": language,
            "code": code
        })

    return blocks


def clean_response(response: str) -> str:
    """
    Clean LLM response by removing common artifacts.

    Removes:
        - Leading/trailing whitespace
        - Markdown formatting characters
        - Common LLM preambles like "Here is..." or "Sure, here's..."

    Args:
        response: Raw LLM response

    Returns:
        Cleaned response text

    Examples:
        >>> response = "Sure, here's the answer:\\n\\nThe result is 42."
        >>> clean = clean_response(response)
        >>> print(clean)
        The result is 42.
    """
    cleaned = response.strip()

    # Remove common preambles
    preambles = [
        r"^Sure,?\s+here(?:'s| is)\s+",
        r"^Here(?:'s| is)\s+",
        r"^Certainly,?\s+",
        r"^Of course,?\s+",
    ]

    for pattern in preambles:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    # Strip again after removal
    cleaned = cleaned.strip()

    return cleaned


def validate_json_schema(data: Dict, required_keys: List[str]) -> bool:
    """
    Validate that JSON has required keys.

    Simple validation helper for checking LLM JSON output has expected structure.

    Args:
        data: Parsed JSON data
        required_keys: List of keys that must exist

    Returns:
        True if all required keys present, False otherwise

    Examples:
        >>> data = {"name": "test", "value": 42}
        >>> validate_json_schema(data, ["name", "value"])
        True
        >>> validate_json_schema(data, ["name", "missing"])
        False
    """
    if not isinstance(data, dict):
        return False

    return all(key in data for key in required_keys)


# ==============================================================================
# QUICK TEST
# ==============================================================================

if __name__ == "__main__":
    print("Testing parsing utilities...")
    print("=" * 60)

    # Test 1: Extract JSON from markdown
    response1 = """Here's the analysis:
```json
{
  "summary": "Code looks good",
  "issues": [],
  "score": 9
}
```
Hope this helps!"""

    data1 = extract_json(response1)
    assert data1["score"] == 9
    print("✅ Test 1: JSON extraction from markdown")

    # Test 2: Extract code block
    response2 = """Here's a Python function:
```python
def hello(name):
    return f"Hello, {name}!"
```
Try it out!"""

    code2 = extract_code_block(response2, language="python")
    assert "def hello" in code2
    print("✅ Test 2: Code block extraction")

    # Test 3: Clean response
    response3 = "Sure, here's the answer:\n\nThe result is 42."
    cleaned3 = clean_response(response3)
    assert cleaned3 == "The result is 42."
    print("✅ Test 3: Response cleaning")

    # Test 4: Validate schema
    data4 = {"name": "test", "value": 42}
    assert validate_json_schema(data4, ["name", "value"])
    assert not validate_json_schema(data4, ["name", "missing"])
    print("✅ Test 4: Schema validation")

    # Test 5: Extract all code blocks
    response5 = """
```python
def py_func(): pass
```
And in JS:
```javascript
function jsFunc() {}
```"""

    blocks5 = extract_all_code_blocks(response5)
    assert len(blocks5) == 2
    assert blocks5[0]["language"] == "python"
    print("✅ Test 5: Multiple code blocks")

    print("")
    print("=" * 60)
    print("All tests passed! ✅")
