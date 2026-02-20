# Evaluation Datasets

This directory contains datasets for testing and evaluating AI systems, particularly for RAG (Retrieval-Augmented Generation), code analysis, and hallucination detection.

## Overview

These datasets provide ground truth data for systematic evaluation of AI system performance across various dimensions:

- Query understanding and response quality
- Code comprehension and security analysis
- Factual accuracy and hallucination detection
- Retrieval effectiveness in RAG systems

## Files

### 1. test-queries.json

Collection of test queries organized by type and complexity.

**Structure**:
```json
{
  "simple": ["basic questions..."],
  "complex": ["advanced questions..."],
  "code": ["programming tasks..."],
  "debugging": ["debugging questions..."],
  "architecture": ["system design..."],
  "best_practices": ["best practice questions..."],
  "tools": ["tooling questions..."]
}
```

**Categories**:

- **simple** (15 queries): Basic programming concepts, ideal for baseline testing
- **complex** (20 queries): Advanced topics requiring deeper understanding
- **code** (23 queries): Specific coding tasks and implementations
- **debugging** (10 queries): Problem diagnosis and troubleshooting
- **architecture** (10 queries): System design and architecture patterns
- **best_practices** (10 queries): Code quality and development standards
- **tools** (10 queries): Development tools and environment setup

**Total**: 98 test queries

**Use Cases**:
- Benchmark response quality across difficulty levels
- Test query understanding and categorization
- Evaluate code generation capabilities
- Assess debugging and troubleshooting abilities

**Example Usage**:
```python
import json

with open('test-queries.json') as f:
    queries = json.load(f)

# Test simple queries
for query in queries['simple']:
    response = ai_system.query(query)
    evaluate_response(response)

# Test code generation
for query in queries['code']:
    code = ai_system.generate_code(query)
    test_code_correctness(code)
```

### 2. rag-ground-truth.json

Question-answer pairs with metadata for evaluating RAG systems.

**Structure**:
```json
[
  {
    "question": "...",
    "expected_answer": "...",
    "relevant_files": ["file paths..."],
    "difficulty": "easy|medium|hard",
    "tags": ["topic", "tags"]
  }
]
```

**Statistics**:
- Total entries: 27 Q&A pairs
- Difficulty breakdown:
  - Easy: 6 entries
  - Medium: 16 entries
  - Hard: 5 entries

**Fields**:
- `question`: The query to test
- `expected_answer`: What a correct response should contain
- `relevant_files`: Which code samples are relevant (for RAG testing)
- `difficulty`: Complexity level
- `tags`: Topic categorization

**Use Cases**:
1. **Retrieval Testing**: Check if RAG system retrieves correct files
2. **Answer Quality**: Compare generated answers with expected answers
3. **Semantic Similarity**: Measure similarity between generated and expected answers
4. **Coverage Testing**: Ensure answers address all key points

**Example Usage**:
```python
import json

with open('rag-ground-truth.json') as f:
    ground_truth = json.load(f)

for item in ground_truth:
    # Test retrieval
    retrieved_docs = rag_system.retrieve(item['question'])
    assert any(doc in retrieved_docs for doc in item['relevant_files'])

    # Test answer quality
    answer = rag_system.answer(item['question'])
    similarity = compute_similarity(answer, item['expected_answer'])
    assert similarity > 0.7  # 70% similarity threshold
```

**Topics Covered**:
- Python programming (sorting, classes, async, OOP)
- JavaScript (async/await, promises, React)
- Security vulnerabilities and prevention
- Documentation best practices
- Type systems and error handling
- Performance optimization
- Code patterns and anti-patterns

### 3. hallucination-cases.json

Known hallucination examples for testing factual accuracy.

**Structure**:
```json
[
  {
    "id": 1,
    "category": "...",
    "query": "...",
    "hallucinated_response": "...",
    "correct_response": "...",
    "severity": "low|medium|high|critical",
    "explanation": "..."
  }
]
```

**Statistics**:
- Total cases: 25 hallucination examples
- Severity breakdown:
  - Critical: 3 cases
  - High: 7 cases
  - Medium: 12 cases
  - Low: 3 cases

**Categories**:
1. **fabricated_api**: Non-existent APIs or methods
2. **false_documentation**: Incorrect parameter information
3. **invented_library**: Made-up library names
4. **false_syntax**: Wrong language syntax
5. **fabricated_feature**: Non-existent language features
6. **wrong_defaults**: Incorrect default values
7. **false_version_info**: Wrong version history
8. **invented_method**: Non-existent methods
9. **false_security_claim**: Dangerous security misinformation
10. **fabricated_behavior**: Wrong language behavior
11. **wrong_best_practice**: Incorrect security advice
12. **invented_configuration**: Non-existent config options
13. **false_compatibility**: Wrong compatibility information
14. **fabricated_error**: Incorrect error explanations
15. **wrong_package_name**: Incorrect package names
16. **invented_pattern**: Non-existent design patterns
17. **false_performance_claim**: Incorrect performance statements
18. **fabricated_hook**: Non-existent React hooks
19. **wrong_sql_syntax**: Incorrect SQL syntax
20. **false_deprecation**: Incorrect deprecation claims
21. **invented_command**: Non-existent CLI commands
22. **false_limitation**: Incorrect capability limits
23. **wrong_regex**: Incorrect regex patterns
24. **fabricated_attribute**: Non-existent HTML attributes
25. **wrong_scope_rule**: Incorrect scoping rules

**Use Cases**:
- Test hallucination detection systems
- Train validators to catch false information
- Benchmark factual accuracy
- Create adversarial test sets

**Example Usage**:
```python
import json

with open('hallucination-cases.json') as f:
    cases = json.load(f)

# Test for hallucinations
for case in cases:
    response = ai_system.query(case['query'])

    # Check if response contains hallucinated content
    if similar_to(response, case['hallucinated_response']):
        print(f"FAIL: Hallucination detected in case {case['id']}")
        print(f"Category: {case['category']}")
        print(f"Severity: {case['severity']}")

    # Check if response matches correct answer
    if similar_to(response, case['correct_response']):
        print(f"PASS: Correct response for case {case['id']}")
```

**Severity Guidelines**:
- **Critical**: Could lead to security vulnerabilities or data loss
- **High**: Incorrect information that would break code
- **Medium**: Misleading but not immediately harmful
- **Low**: Minor inaccuracies or naming issues

### 4. code-review-examples.json

Code samples with identified issues for testing code analysis capabilities.

**Structure**:
```json
[
  {
    "id": 1,
    "code": "...",
    "language": "python|javascript|sql",
    "issues": [
      {
        "type": "bug|security|style|performance|bad_practice",
        "severity": "low|medium|high|critical",
        "description": "...",
        "line": 1,
        "suggestion": "..."
      }
    ],
    "fixed_code": "..."
  }
]
```

**Statistics**:
- Total examples: 15 code samples
- Languages: Python (7), JavaScript (7), SQL (1)
- Issue types:
  - Security: 8 issues (53%)
  - Bugs: 6 issues (40%)
  - Bad practices: 4 issues (27%)
  - Style: 2 issues (13%)
  - Performance: 1 issue (7%)

**Issue Types**:

1. **Security** (Critical/High):
   - SQL injection
   - XSS vulnerabilities
   - Command injection
   - Hardcoded credentials
   - Insecure data storage
   - Path traversal

2. **Bugs** (High/Medium):
   - Division by zero
   - Infinite loops
   - State management issues
   - Closure problems
   - Missing parameters

3. **Bad Practices** (Medium):
   - Bare except clauses
   - Silencing errors
   - Missing error handling
   - Incomplete response handling

4. **Style** (Low):
   - Non-idiomatic code
   - Type coercion issues
   - Can be simplified

5. **Performance** (Low):
   - Unnecessary recalculation
   - Missing memoization

**Use Cases**:
1. **Code Review Training**: Train AI to identify common issues
2. **Security Analysis**: Test vulnerability detection
3. **Bug Detection**: Evaluate bug-finding capabilities
4. **Fix Suggestions**: Compare AI suggestions with known fixes
5. **Multi-language Testing**: Test across Python, JavaScript, SQL

**Example Usage**:
```python
import json

with open('code-review-examples.json') as f:
    examples = json.load(f)

for example in examples:
    # Test issue detection
    detected_issues = ai_system.analyze_code(example['code'], example['language'])

    # Compare with known issues
    expected_issues = example['issues']

    for expected in expected_issues:
        found = any(
            issue['type'] == expected['type'] and
            issue['severity'] == expected['severity']
            for issue in detected_issues
        )

        if found:
            print(f"✓ Detected {expected['type']} issue in example {example['id']}")
        else:
            print(f"✗ Missed {expected['type']} issue in example {example['id']}")

    # Test fix generation
    suggested_fix = ai_system.fix_code(example['code'])
    if similar_to(suggested_fix, example['fixed_code']):
        print(f"✓ Generated correct fix for example {example['id']}")
```

**Severity Distribution**:
- Critical: 4 issues (injection attacks, exposed credentials)
- High: 9 issues (bugs, security flaws)
- Medium: 8 issues (bad practices, moderate bugs)
- Low: 3 issues (style, minor optimizations)

## Evaluation Metrics

### For RAG Systems

1. **Retrieval Metrics**:
   - Precision: % of retrieved documents that are relevant
   - Recall: % of relevant documents that are retrieved
   - MRR (Mean Reciprocal Rank): Ranking quality

2. **Answer Quality Metrics**:
   - Semantic similarity to ground truth
   - Factual accuracy
   - Completeness (covers all key points)
   - Conciseness

3. **Hallucination Metrics**:
   - False positive rate (hallucinated content)
   - True negative rate (avoided hallucinations)
   - Confidence calibration

### For Code Analysis

1. **Detection Metrics**:
   - Issue detection rate (recall)
   - False positive rate (precision)
   - Severity accuracy

2. **Fix Quality**:
   - Correctness of suggested fixes
   - Code quality improvement
   - Preservation of functionality

## Usage Examples

### Complete Evaluation Pipeline

```python
import json
from typing import Dict, List

class AISystemEvaluator:
    def __init__(self, ai_system):
        self.ai_system = ai_system
        self.load_datasets()

    def load_datasets(self):
        with open('test-queries.json') as f:
            self.queries = json.load(f)
        with open('rag-ground-truth.json') as f:
            self.rag_data = json.load(f)
        with open('hallucination-cases.json') as f:
            self.hallucination_cases = json.load(f)
        with open('code-review-examples.json') as f:
            self.code_examples = json.load(f)

    def evaluate_query_understanding(self):
        """Test basic query comprehension."""
        results = {'simple': [], 'complex': [], 'code': []}

        for category in ['simple', 'complex', 'code']:
            for query in self.queries[category]:
                response = self.ai_system.query(query)
                score = self.score_response(response, query)
                results[category].append(score)

        return results

    def evaluate_rag_accuracy(self):
        """Test RAG system performance."""
        retrieval_scores = []
        answer_scores = []

        for item in self.rag_data:
            # Test retrieval
            retrieved = self.ai_system.retrieve(item['question'])
            retrieval_score = self.score_retrieval(
                retrieved,
                item['relevant_files']
            )
            retrieval_scores.append(retrieval_score)

            # Test answer quality
            answer = self.ai_system.answer(item['question'])
            answer_score = self.score_answer(
                answer,
                item['expected_answer']
            )
            answer_scores.append(answer_score)

        return {
            'retrieval': sum(retrieval_scores) / len(retrieval_scores),
            'answer_quality': sum(answer_scores) / len(answer_scores)
        }

    def evaluate_hallucination_detection(self):
        """Test for hallucinations."""
        correct = 0
        total = len(self.hallucination_cases)

        for case in self.hallucination_cases:
            response = self.ai_system.query(case['query'])

            # Check if response avoids hallucination
            if not self.contains_hallucination(response, case):
                correct += 1

        return correct / total

    def evaluate_code_analysis(self):
        """Test code analysis capabilities."""
        detection_rate = []
        fix_quality = []

        for example in self.code_examples:
            # Test issue detection
            detected = self.ai_system.analyze_code(
                example['code'],
                example['language']
            )
            detection_score = self.score_detection(
                detected,
                example['issues']
            )
            detection_rate.append(detection_score)

            # Test fix quality
            fix = self.ai_system.fix_code(example['code'])
            fix_score = self.score_fix(fix, example['fixed_code'])
            fix_quality.append(fix_score)

        return {
            'detection_rate': sum(detection_rate) / len(detection_rate),
            'fix_quality': sum(fix_quality) / len(fix_quality)
        }

    def run_full_evaluation(self):
        """Run complete evaluation suite."""
        return {
            'query_understanding': self.evaluate_query_understanding(),
            'rag_accuracy': self.evaluate_rag_accuracy(),
            'hallucination_rate': self.evaluate_hallucination_detection(),
            'code_analysis': self.evaluate_code_analysis()
        }

# Usage
evaluator = AISystemEvaluator(my_ai_system)
results = evaluator.run_full_evaluation()
print(json.dumps(results, indent=2))
```

## Integration with Code Samples

These evaluation datasets are designed to work with the code samples in `../code-samples/`:

- `rag-ground-truth.json` references specific code sample files
- `code-review-examples.json` includes similar patterns to code samples
- `test-queries.json` includes questions about concepts in code samples

## Best Practices

### When Using These Datasets

1. **Baseline Testing**: Start with simple queries to establish baseline
2. **Progressive Complexity**: Move to complex queries and code analysis
3. **Hallucination Testing**: Always test for factual accuracy
4. **Security Focus**: Pay special attention to security-related cases
5. **Regular Updates**: Update datasets as your AI system improves

### When Adding New Data

1. **Diverse Coverage**: Include various programming concepts
2. **Real-world Relevance**: Use realistic scenarios
3. **Clear Ground Truth**: Ensure expected answers are accurate
4. **Severity Classification**: Accurately classify issue severity
5. **Documentation**: Explain why each case is important

## Contributing

To add new evaluation data:

1. Follow the existing JSON structure
2. Include all required fields
3. Verify ground truth is accurate
4. Add documentation for new categories
5. Test with existing evaluation code

## Related Resources

- `../code-samples/` - Code samples referenced in evaluations
- `../code-samples/README.md` - Documentation for code samples

## Questions or Issues?

If you find incorrect ground truth data or have suggestions for additional test cases, please open an issue or submit a pull request.
