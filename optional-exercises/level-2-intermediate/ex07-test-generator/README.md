# Exercise 07: Intelligent Test Generator

## Description
Generate unit tests automatically by analyzing functions and their edge cases.

## Objectives
- Analyze function to identify test cases
- Generate comprehensive tests
- Automatically detect edge cases
- Follow testing best practices

## Implementation

```python
class TestGenerator:
    def generate_tests(self, function_code: str, language: str = "python"):
        prompt = f"""
Analyze this {language} function and generate comprehensive unit tests:

{function_code}

Generate tests for:
1. Happy path
2. Edge cases (empty input, null, boundaries)
3. Error conditions
4. Type validation

Use pytest format. Include fixtures if needed.
"""

        tests = self.llm.complete(prompt)
        return self.validate_tests(tests)

    def validate_tests(self, test_code: str) -> str:
        # Parse and validate test syntax
        # Run tests to ensure they execute
        # Check coverage
        pass
```

## Features
- [ ] Multiple test frameworks (pytest, jest, junit)
- [ ] Mocking suggestions
- [ ] Coverage analysis
- [ ] Fixture generation
- [ ] Integration test scaffolding

## Example Output

```python
# Input function
def divide(a: float, b: float) -> float:
    return a / b

# Generated tests
import pytest

def test_divide_positive_numbers():
    assert divide(10, 2) == 5.0

def test_divide_negative_numbers():
    assert divide(-10, 2) == -5.0

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_divide_float_precision():
    result = divide(1, 3)
    assert abs(result - 0.333333) < 0.0001
```

## Challenges
1. Property-based testing generation
2. Mutation testing
3. Test quality scoring
4. Auto-fix failing tests

**Time**: 5-6h
