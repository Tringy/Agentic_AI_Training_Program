# Code Samples

This directory contains code samples for testing AI systems, code review tools, and RAG implementations.

## Overview

The samples are organized by programming language and include various complexity levels, patterns, and intentional issues for educational purposes.

## Directory Structure

```
code-samples/
├── python/
│   ├── simple_function.py         # Basic functions (sorting, math)
│   ├── class_example.py           # OOP with classes and inheritance
│   ├── async_example.py           # Async/await patterns
│   ├── error_prone.py             # Security vulnerabilities (educational)
│   └── well_documented.py         # Example of best practices
├── javascript/
│   ├── simple_function.js         # Basic utility functions
│   ├── class_example.js           # ES6 classes
│   ├── async_example.js           # Promises and async/await
│   ├── react_component.jsx        # React components and hooks
│   └── error_prone.js             # Security vulnerabilities (educational)
└── README.md                      # This file
```

## Sample Types

### 1. Simple Functions
**Files**: `python/simple_function.py`, `javascript/simple_function.js`

Basic algorithmic functions for testing:
- Sorting algorithms
- Mathematical calculations
- String manipulation
- Array operations

**Use cases**:
- Testing code comprehension
- Analyzing algorithm efficiency
- Generating test cases
- Code explanation tasks

### 2. Object-Oriented Examples
**Files**: `python/class_example.py`, `javascript/class_example.js`

Class-based code demonstrating OOP principles:
- Class definitions
- Inheritance
- Encapsulation
- Method implementations

**Use cases**:
- Understanding class relationships
- Testing refactoring suggestions
- Analyzing design patterns
- Documentation generation

### 3. Asynchronous Patterns
**Files**: `python/async_example.py`, `javascript/async_example.js`

Async programming examples:
- Async/await syntax
- Promise handling
- Concurrent operations
- Error handling in async code

**Use cases**:
- Understanding concurrency
- Identifying race conditions
- Testing async error handling
- Performance optimization suggestions

### 4. React Components
**File**: `javascript/react_component.jsx`

Modern React patterns:
- Functional components
- React hooks (useState, useEffect, useCallback, useMemo)
- Custom hooks
- Form handling
- Data fetching

**Use cases**:
- React-specific code analysis
- Component refactoring suggestions
- State management patterns
- Hook usage optimization

### 5. Well-Documented Code
**File**: `python/well_documented.py`

Example of excellent documentation:
- Module docstrings
- Function documentation
- Type hints
- Usage examples
- Clear variable names

**Use cases**:
- Documentation quality benchmarking
- Testing doc generation
- Code readability analysis
- Best practices demonstrations

### 6. Vulnerable Code (Educational)
**Files**: `python/error_prone.py`, `javascript/error_prone.js`

**⚠️ WARNING**: These files contain intentional security vulnerabilities for educational purposes only.

Security issues included:
- SQL injection
- Cross-site scripting (XSS)
- Command injection
- Insecure deserialization
- Hardcoded credentials
- Weak cryptography
- Path traversal
- Missing input validation
- CSRF vulnerabilities
- Prototype pollution

Each vulnerability is accompanied by a safe alternative implementation.

**Use cases**:
- Security vulnerability detection
- Code review training
- Testing security analysis tools
- Demonstrating secure coding practices

## Usage Examples

### For Testing Code Comprehension
```python
# Use simple_function.py to test if AI can:
from code_samples.python.simple_function import bubble_sort

# - Explain the algorithm
# - Identify time complexity
# - Suggest optimizations
# - Generate test cases
```

### For Security Analysis
```python
# Use error_prone.py to test if AI can:
from code_samples.python.error_prone import get_user_by_name_unsafe

# - Identify vulnerabilities
# - Explain the security risk
# - Suggest secure alternatives
# - Generate security test cases
```

### For Documentation Testing
```python
# Use well_documented.py as a benchmark:
from code_samples.python.well_documented import TaskManager

# - Assess documentation quality
# - Generate similar documentation
# - Extract API specifications
# - Create usage examples
```

## Testing Guidelines

### Code Comprehension Tests
1. Load a code sample
2. Ask AI to explain what it does
3. Request complexity analysis
4. Ask for improvement suggestions

### Security Analysis Tests
1. Present vulnerable code
2. Ask AI to identify issues
3. Request severity assessment
4. Ask for remediation steps

### Code Generation Tests
1. Describe functionality from a sample
2. Ask AI to implement from scratch
3. Compare with original
4. Evaluate correctness and style

### Refactoring Tests
1. Present code for refactoring
2. Ask for specific improvements
3. Verify refactored code maintains functionality
4. Assess code quality improvements

## Complexity Levels

| Level | Lines | Features | Files |
|-------|-------|----------|-------|
| Simple | 10-30 | Basic functions, no dependencies | simple_function.* |
| Medium | 30-80 | Classes, async, moderate logic | class_example.*, async_example.* |
| Complex | 80-200+ | Multiple patterns, advanced features | react_component.jsx, well_documented.py |

## Best Practices Demonstrated

### Python Samples
- Type hints
- Docstrings
- PEP 8 compliance
- Error handling
- Dataclasses
- Context managers

### JavaScript Samples
- JSDoc comments
- ES6+ features
- Modern async patterns
- React best practices
- Error boundaries
- Custom hooks

## Integration with RAG Systems

These samples can be used to test RAG systems:

1. **Indexing**: Add samples to vector database
2. **Retrieval**: Test if relevant samples are retrieved
3. **Augmentation**: Test if retrieved samples improve responses
4. **Evaluation**: Measure accuracy of code-related queries

## Contributing

When adding new code samples:

1. Follow the existing structure
2. Include comments explaining key concepts
3. Provide both problematic and corrected versions for security issues
4. Add documentation in this README
5. Ensure samples are realistic and useful for testing

## Security Notice

The files marked as "error_prone" contain intentional vulnerabilities:
- **DO NOT** deploy this code to production
- **DO NOT** use as templates for real applications
- **DO** use for security training and testing
- **DO** study the safe alternatives provided

## Related Datasets

See also:
- `../evaluation/code-review-examples.json` - Structured code review test cases
- `../evaluation/test-queries.json` - Sample queries for code-related questions

## Questions?

If you need additional code samples or have suggestions for improvements, please open an issue or submit a pull request.
