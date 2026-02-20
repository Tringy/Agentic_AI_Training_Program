# Capstone Option C: Tech Debt Analyzer

## Project Overview

Build a RAG-powered system that indexes codebases, detects technical debt patterns using semantic search, and generates prioritized reports with actionable recommendations.

**Complexity**: Medium-High
**Estimated Time**: 2-2.5 hours

---

## Requirements

### Must Have (Core - 70%)
- [ ] Index codebase into vector store (ChromaDB or in-memory)
- [ ] Detect at least 5 technical debt patterns:
  - TODO/FIXME/HACK comments
  - Duplicate code blocks
  - Long functions (>50 lines)
  - High cyclomatic complexity
  - Outdated patterns or imports
- [ ] Score each issue by severity (critical/high/medium/low)
- [ ] Generate JSON report with file paths and line numbers
- [ ] POST `/analyze` API endpoint accepting directory path

### Should Have (Polish - 20%)
- [ ] Prioritize by impact (frequently changed files = higher priority)
- [ ] Use semantic search to find similar problematic patterns
- [ ] Generate HTML report with code snippets
- [ ] Filter results by tech debt category

### Nice to Have (Bonus - 10%)
- [ ] Historical tracking (compare with previous scans)
- [ ] GitHub integration (auto-post issues)
- [ ] Customizable tech debt rules via config
- [ ] Refactoring suggestions with code examples

---

## API Specification

### POST /analyze

**Request:**
```json
{
  "directory": "./src",
  "threshold": "medium",
  "categories": ["todos", "complexity", "duplication"]
}
```

**Response:**
```json
{
  "summary": {
    "total_issues": 47,
    "critical": 3,
    "high": 12,
    "medium": 20,
    "low": 12,
    "scan_time_seconds": 8.5
  },
  "issues": [
    {
      "severity": "high",
      "category": "complexity",
      "file": "src/utils/parser.py",
      "line": 145,
      "description": "Function has cyclomatic complexity of 23 (threshold: 10)",
      "code_snippet": "def parse_complex_structure(data):\n    if data.type == 'A':\n        ...",
      "recommendation": "Refactor into smaller functions with single responsibilities",
      "similar_issues": [
        "src/handlers/request.py:89",
        "src/processors/batch.py:234"
      ]
    },
    {
      "severity": "medium",
      "category": "todos",
      "file": "src/api/routes.py",
      "line": 67,
      "description": "TODO comment indicates incomplete feature",
      "code_snippet": "# TODO: Add authentication check",
      "recommendation": "Complete authentication implementation or remove TODO",
      "similar_issues": []
    }
  ],
  "recommendations": [
    "Address 3 critical issues in src/utils/ before next release",
    "15 TODO comments suggest incomplete features - consider sprint to resolve",
    "High complexity in parser.py affects maintainability - refactor recommended"
  ]
}
```

---

## Starter Code

### main.py
```python
"""Tech Debt Analyzer - Capstone Option C"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path

from analyzer import TechDebtAnalyzer
from llm_client import LLMClient

app = FastAPI(title="Tech Debt Analyzer")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    directory: str
    threshold: str = "medium"  # "low", "medium", "high"
    categories: Optional[List[str]] = None  # Filter by category

class Issue(BaseModel):
    severity: str
    category: str
    file: str
    line: int
    description: str
    code_snippet: str
    recommendation: str
    similar_issues: List[str]

class AnalyzeResponse(BaseModel):
    summary: dict
    issues: List[Issue]
    recommendations: List[str]

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_tech_debt(request: AnalyzeRequest):
    """Analyze codebase for technical debt.

    Args:
        request: Analysis request with directory and options

    Returns:
        Structured report with issues and recommendations
    """
    # Validate directory exists
    dir_path = Path(request.directory)
    if not dir_path.exists() or not dir_path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid directory path")

    # TODO: Implement analysis
    try:
        llm = LLMClient()
        analyzer = TechDebtAnalyzer(llm)

        result = analyzer.analyze(
            directory=dir_path,
            threshold=request.threshold,
            categories=request.categories
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "tech-debt-analyzer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### analyzer.py
```python
"""Tech debt analysis using RAG and pattern detection."""
from typing import List, Dict, Optional
from pathlib import Path
import time

from rag_pipeline import TechDebtRAG
from detectors import (
    TodoDetector,
    ComplexityDetector,
    DuplicationDetector,
    LongFunctionDetector
)

class TechDebtAnalyzer:
    """RAG-based technical debt analyzer."""

    def __init__(self, llm_client):
        """Initialize analyzer with LLM client.

        Args:
            llm_client: LLM client for analysis
        """
        self.llm = llm_client
        self.rag = TechDebtRAG(llm_client)

        # Initialize detectors
        self.detectors = {
            "todos": TodoDetector(),
            "complexity": ComplexityDetector(),
            "duplication": DuplicationDetector(llm_client),
            "long_functions": LongFunctionDetector()
        }

    def analyze(
        self,
        directory: Path,
        threshold: str = "medium",
        categories: Optional[List[str]] = None
    ) -> Dict:
        """Analyze directory for technical debt.

        Args:
            directory: Directory to analyze
            threshold: Severity threshold (low/medium/high)
            categories: Filter by categories (None = all)

        Returns:
            Analysis results with issues and recommendations
        """
        start_time = time.time()

        # Step 1: Index codebase with RAG
        print(f"Indexing codebase: {directory}")
        self.rag.index_directory(str(directory))

        # Step 2: Run detectors
        all_issues = []
        selected_detectors = self._select_detectors(categories)

        for name, detector in selected_detectors.items():
            print(f"Running {name} detector...")
            detected = detector.detect(directory)
            all_issues.extend(detected)

        # Step 3: Use RAG to find similar patterns
        print("Finding similar patterns with RAG...")
        for issue in all_issues:
            similar = self._find_similar_issues(issue)
            issue['similar_issues'] = similar

        # Step 4: Score and prioritize
        scored_issues = self._score_issues(all_issues, directory)

        # Step 5: Filter by threshold
        filtered_issues = self._filter_by_threshold(scored_issues, threshold)

        # Step 6: Generate recommendations using LLM
        recommendations = self._generate_recommendations(filtered_issues)

        scan_time = time.time() - start_time

        return {
            "summary": self._build_summary(filtered_issues, scan_time),
            "issues": filtered_issues,
            "recommendations": recommendations
        }

    def _select_detectors(self, categories: Optional[List[str]]) -> Dict:
        """Select detectors based on requested categories."""
        if categories is None:
            return self.detectors

        return {
            name: detector
            for name, detector in self.detectors.items()
            if name in categories
        }

    def _find_similar_issues(self, issue: Dict) -> List[str]:
        """Use RAG to find similar problematic code patterns.

        Args:
            issue: Issue to find similar patterns for

        Returns:
            List of file:line references to similar issues
        """
        # TODO: Implement similarity search
        # Query RAG with code snippet, find similar code
        query = f"Code pattern similar to: {issue['code_snippet'][:200]}"

        try:
            results = self.rag.query(query, n_results=3)

            similar = []
            for source in results.get('sources', []):
                # Don't include the same file
                if source['file'] != issue['file']:
                    similar.append(f"{source['file']}:{source['line']}")

            return similar[:3]  # Max 3 similar issues

        except Exception as e:
            print(f"Warning: Similarity search failed: {e}")
            return []

    def _score_issues(self, issues: List[Dict], directory: Path) -> List[Dict]:
        """Score issues by severity and impact.

        Args:
            issues: Raw issues from detectors
            directory: Project directory

        Returns:
            Issues with scores
        """
        # TODO: Implement scoring logic
        # Consider:
        # - Base severity from detector
        # - File change frequency (git log)
        # - Number of similar issues
        # - Location criticality (core vs util)

        scored = []
        for issue in issues:
            # Base score from severity
            severity_scores = {
                "critical": 10,
                "high": 7,
                "medium": 4,
                "low": 2
            }
            score = severity_scores.get(issue['severity'], 2)

            # Boost score if many similar issues
            if len(issue.get('similar_issues', [])) > 2:
                score += 2

            # Update severity based on final score
            if score >= 9:
                issue['severity'] = "critical"
            elif score >= 6:
                issue['severity'] = "high"
            elif score >= 3:
                issue['severity'] = "medium"
            else:
                issue['severity'] = "low"

            scored.append(issue)

        # Sort by score (highest first)
        scored.sort(key=lambda x: severity_scores.get(x['severity'], 0), reverse=True)

        return scored

    def _filter_by_threshold(self, issues: List[Dict], threshold: str) -> List[Dict]:
        """Filter issues by severity threshold."""
        severity_levels = {
            "low": ["low", "medium", "high", "critical"],
            "medium": ["medium", "high", "critical"],
            "high": ["high", "critical"]
        }

        allowed = severity_levels.get(threshold, ["medium", "high", "critical"])
        return [issue for issue in issues if issue['severity'] in allowed]

    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate actionable recommendations using LLM.

        Args:
            issues: Filtered and scored issues

        Returns:
            List of recommendations
        """
        # TODO: Use LLM to synthesize top recommendations
        # Group issues by category and severity
        # Generate prioritized action items

        if not issues:
            return ["No technical debt detected above threshold."]

        # Group by severity
        by_severity = {}
        for issue in issues:
            severity = issue['severity']
            by_severity[severity] = by_severity.get(severity, 0) + 1

        recommendations = []

        # Critical issues
        if by_severity.get('critical', 0) > 0:
            critical_files = set(i['file'] for i in issues if i['severity'] == 'critical')
            recommendations.append(
                f"Address {by_severity['critical']} critical issues in "
                f"{', '.join(list(critical_files)[:3])} before next release"
            )

        # TODOs
        todos = [i for i in issues if i['category'] == 'todos']
        if len(todos) > 10:
            recommendations.append(
                f"{len(todos)} TODO comments suggest incomplete features - "
                "consider dedicated sprint to resolve"
            )

        # Complexity
        complex_issues = [i for i in issues if i['category'] == 'complexity']
        if complex_issues:
            recommendations.append(
                f"High complexity in {complex_issues[0]['file']} "
                "affects maintainability - refactoring recommended"
            )

        return recommendations

    def _build_summary(self, issues: List[Dict], scan_time: float) -> Dict:
        """Build summary statistics."""
        summary = {
            "total_issues": len(issues),
            "critical": sum(1 for i in issues if i['severity'] == 'critical'),
            "high": sum(1 for i in issues if i['severity'] == 'high'),
            "medium": sum(1 for i in issues if i['severity'] == 'medium'),
            "low": sum(1 for i in issues if i['severity'] == 'low'),
            "scan_time_seconds": round(scan_time, 2)
        }

        # Group by category
        by_category = {}
        for issue in issues:
            cat = issue['category']
            by_category[cat] = by_category.get(cat, 0) + 1

        summary['by_category'] = by_category

        return summary
```

### detectors.py
```python
"""Technical debt pattern detectors."""
import re
import ast
from typing import List, Dict
from pathlib import Path

class TodoDetector:
    """Detect TODO/FIXME/HACK comments indicating incomplete work."""

    def detect(self, directory: Path) -> List[Dict]:
        """Scan for TODO comments.

        Args:
            directory: Directory to scan

        Returns:
            List of TODO issues found
        """
        issues = []

        # Scan Python files
        for file in directory.rglob("*.py"):
            content = file.read_text(errors='ignore')
            for i, line in enumerate(content.split('\n'), 1):
                match = re.search(r'#\s*(TODO|FIXME|HACK|XXX|BUG)[:|\s]', line, re.I)
                if match:
                    issues.append({
                        "severity": "medium" if "TODO" in match.group(1) else "high",
                        "category": "todos",
                        "file": str(file.relative_to(directory)),
                        "line": i,
                        "description": f"{match.group(1)} comment: {line.strip()}",
                        "code_snippet": line.strip(),
                        "recommendation": f"Complete the {match.group(1)} or convert to tracked issue"
                    })

        # Scan JavaScript/TypeScript files
        for pattern in ["*.js", "*.ts", "*.jsx", "*.tsx"]:
            for file in directory.rglob(pattern):
                content = file.read_text(errors='ignore')
                for i, line in enumerate(content.split('\n'), 1):
                    match = re.search(r'//\s*(TODO|FIXME|HACK|XXX|BUG)[:|\s]', line, re.I)
                    if match:
                        issues.append({
                            "severity": "medium",
                            "category": "todos",
                            "file": str(file.relative_to(directory)),
                            "line": i,
                            "description": f"{match.group(1)} comment: {line.strip()}",
                            "code_snippet": line.strip(),
                            "recommendation": f"Complete the {match.group(1)} or remove comment"
                        })

        return issues


class ComplexityDetector:
    """Detect functions with high cyclomatic complexity."""

    def detect(self, directory: Path) -> List[Dict]:
        """Detect high complexity functions.

        Args:
            directory: Directory to scan

        Returns:
            List of complexity issues
        """
        issues = []

        # TODO: Implement cyclomatic complexity detection
        # Option 1: Use radon library (pip install radon)
        # Option 2: Count if/elif/else/for/while statements in AST

        for file in directory.rglob("*.py"):
            try:
                content = file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        complexity = self._calculate_complexity(node)

                        if complexity > 10:  # Threshold
                            issues.append({
                                "severity": "high" if complexity > 15 else "medium",
                                "category": "complexity",
                                "file": str(file.relative_to(directory)),
                                "line": node.lineno,
                                "description": f"Function '{node.name}' has cyclomatic complexity of {complexity} (threshold: 10)",
                                "code_snippet": f"def {node.name}(...):",
                                "recommendation": "Refactor into smaller functions with single responsibilities"
                            })

            except Exception as e:
                print(f"Warning: Could not analyze {file}: {e}")

        return issues

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of function.

        Args:
            node: Function AST node

        Returns:
            Complexity score (number of decision points + 1)
        """
        complexity = 1  # Base complexity

        # Count decision points
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity


class LongFunctionDetector:
    """Detect functions that are too long."""

    def detect(self, directory: Path) -> List[Dict]:
        """Detect long functions (>50 lines).

        Args:
            directory: Directory to scan

        Returns:
            List of long function issues
        """
        issues = []

        for file in directory.rglob("*.py"):
            try:
                content = file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Get function body line count
                        if hasattr(node, 'end_lineno'):
                            length = node.end_lineno - node.lineno + 1

                            if length > 50:
                                issues.append({
                                    "severity": "medium" if length < 100 else "high",
                                    "category": "maintainability",
                                    "file": str(file.relative_to(directory)),
                                    "line": node.lineno,
                                    "description": f"Function '{node.name}' is {length} lines (threshold: 50)",
                                    "code_snippet": f"def {node.name}(...): # {length} lines",
                                    "recommendation": "Consider breaking into smaller, focused functions"
                                })

            except Exception as e:
                print(f"Warning: Could not analyze {file}: {e}")

        return issues


class DuplicationDetector:
    """Detect duplicate code blocks using RAG similarity."""

    def __init__(self, llm_client):
        """Initialize with LLM client for semantic comparison."""
        self.llm = llm_client

    def detect(self, directory: Path) -> List[Dict]:
        """Detect duplicate code blocks.

        Args:
            directory: Directory to scan

        Returns:
            List of duplication issues
        """
        # TODO: Implement duplication detection
        # Option 1: Hash-based (exact duplicates)
        # Option 2: RAG-based (semantic duplicates)

        # Simplified implementation: Look for exact duplicates
        issues = []

        # This is a simplified placeholder
        # Full implementation would use RAG similarity search

        return issues
```

### rag_pipeline.py
```python
"""RAG pipeline for tech debt analysis."""
import os
from pathlib import Path
from typing import List, Dict, Optional

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False
    print("Warning: chromadb not installed. Using in-memory fallback.")

class TechDebtRAG:
    """RAG pipeline for semantic code search."""

    def __init__(self, llm_client):
        """Initialize RAG pipeline.

        Args:
            llm_client: LLM client for embeddings and analysis
        """
        self.llm = llm_client
        self.collection_name = "tech_debt_codebase"

        # Initialize vector store
        if HAS_CHROMA:
            self.client = chromadb.Client(Settings(anonymized_telemetry=False))
            try:
                self.client.delete_collection(self.collection_name)
            except:
                pass
            self.collection = self.client.create_collection(self.collection_name)
        else:
            # In-memory fallback
            self.documents = []

    def index_directory(self, directory: str) -> int:
        """Index all code files in directory.

        Args:
            directory: Directory path to index

        Returns:
            Number of files indexed
        """
        dir_path = Path(directory)
        code_extensions = [".py", ".js", ".ts", ".jsx", ".tsx"]

        documents = []
        metadatas = []
        ids = []

        file_count = 0

        for ext in code_extensions:
            for file in dir_path.rglob(f"*{ext}"):
                try:
                    content = file.read_text(encoding='utf-8')

                    # Simple chunking: split by function/class
                    chunks = self._chunk_code(content, ext)

                    for i, chunk in enumerate(chunks):
                        documents.append(chunk)
                        metadatas.append({
                            "file": str(file.relative_to(dir_path)),
                            "language": ext[1:],  # Remove dot
                            "chunk_id": i
                        })
                        ids.append(f"{file.name}_{i}")

                    file_count += 1

                except Exception as e:
                    print(f"Warning: Could not index {file}: {e}")

        # Add to vector store
        if HAS_CHROMA and documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        else:
            self.documents = list(zip(documents, metadatas))

        return file_count

    def query(self, question: str, n_results: int = 5) -> Dict:
        """Query indexed codebase.

        Args:
            question: Search query
            n_results: Number of results to return

        Returns:
            Query results with sources
        """
        if HAS_CHROMA:
            results = self.collection.query(
                query_texts=[question],
                n_results=n_results
            )

            sources = []
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                sources.append({
                    "content": doc,
                    "file": metadata['file'],
                    "line": 0,  # Approximate
                    "language": metadata['language']
                })

            return {"sources": sources}
        else:
            # Fallback: simple text matching
            return {"sources": []}

    def _chunk_code(self, content: str, extension: str) -> List[str]:
        """Simple code chunking strategy.

        Args:
            content: File content
            extension: File extension

        Returns:
            List of code chunks
        """
        # Simple line-based chunking
        lines = content.split('\n')
        chunk_size = 50
        chunks = []

        for i in range(0, len(lines), chunk_size):
            chunk = '\n'.join(lines[i:i+chunk_size])
            if chunk.strip():
                chunks.append(chunk)

        return chunks
```

### prompts.py
```python
"""Prompts for tech debt analysis."""

TECH_DEBT_SYSTEM_PROMPT = """You are an expert software engineer specializing in code quality and technical debt analysis.

Analyze code for:
1. Outdated patterns or deprecated APIs
2. Security vulnerabilities
3. Performance bottlenecks
4. Maintainability issues
5. Code smells and anti-patterns

Provide specific, actionable recommendations."""

RECOMMENDATION_PROMPT = """Based on these technical debt issues found in a codebase, generate 3-5 prioritized, actionable recommendations:

Issues summary:
- Critical: {critical}
- High: {high}
- Medium: {medium}
- Low: {low}

Top issues:
{top_issues}

Provide concrete next steps that would have the highest impact on code quality."""
```

### llm_client.py
```python
"""LLM client abstraction."""
import os
from anthropic import Anthropic

class LLMClient:
    """Simple LLM client for tech debt analysis."""

    def __init__(self):
        """Initialize LLM client with API key from environment."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment. "
                "Set it in .env or export it."
            )

        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def chat(self, system: str, user: str) -> str:
        """Send messages to LLM and get response.

        Args:
            system: System prompt
            user: User message

        Returns:
            LLM response text
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user}]
        )

        return response.content[0].text
```

### requirements.txt
```
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
anthropic==0.18.0
chromadb==0.4.22
sentence-transformers==2.3.0
python-dotenv==1.0.0
```

---

## Implementation Steps

1. **Setup** (10 min)
   - Copy starter files
   - Install dependencies: `pip install -r requirements.txt`
   - Set ANTHROPIC_API_KEY
   - Test: `uvicorn main:app --reload`

2. **Basic Detectors** (40 min)
   - Complete TodoDetector (regex-based)
   - Complete ComplexityDetector (AST-based)
   - Complete LongFunctionDetector
   - Test on sample codebase
   - Verify issues are found correctly

3. **RAG Indexing** (30 min)
   - Complete `index_directory()` in rag_pipeline.py
   - Test indexing with ChromaDB
   - Verify vector store contains code
   - Test query() method

4. **Similarity Search** (25 min)
   - Complete `_find_similar_issues()` in analyzer.py
   - Use RAG to find similar code patterns
   - Test that related issues are linked
   - Verify semantic search works

5. **Scoring & Prioritization** (20 min)
   - Complete `_score_issues()` logic
   - Implement severity calculation
   - Sort by priority
   - Test that critical issues appear first

6. **Report Generation** (15 min)
   - Test complete `/analyze` endpoint
   - Verify JSON response format
   - Test with various thresholds and categories
   - Generate sample HTML report (nice-to-have)

7. **Deploy & Demo** (10 min)
   - Deploy to Railway: `railway init && railway up`
   - Set environment variables
   - Test deployed endpoint
   - Prepare demo with real codebase

---

## Testing

### Test on sample codebase

```bash
# Start server
uvicorn main:app --reload

# In another terminal, test analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "./sample_project",
    "threshold": "medium"
  }'

# Expected: JSON report with detected issues
```

### Test category filtering

```bash
# Only check for TODOs and complexity
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "./src",
    "threshold": "low",
    "categories": ["todos", "complexity"]
  }'

# Expected: Only TODO and complexity issues in response
```

### Test on large codebase

```bash
# Test performance with large project
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "./large_project",
    "threshold": "high"
  }'

# Expected: Completes in <30 seconds, returns only high/critical issues
```

---

## Evaluation Checklist

- [ ] Indexes codebase into vector store
- [ ] Detects TODO/FIXME comments
- [ ] Detects high complexity functions
- [ ] Detects long functions
- [ ] Scores issues by severity
- [ ] Uses RAG to find similar patterns
- [ ] Generates prioritized recommendations
- [ ] API endpoint works correctly
- [ ] Deployed and accessible
- [ ] Demo ready with real codebase

---

## TypeScript Version (Optional)

For students who prefer TypeScript, equivalent implementation available in `typescript/` directory.

Key differences:
- Uses Hono instead of FastAPI
- Zod for validation instead of Pydantic
- Async/await patterns
- Same core logic and prompts

---

## Extension Ideas

If you finish early:
- Add support for more languages (Go, Rust, Java)
- Implement DuplicationDetector with RAG similarity
- Add git history analysis (files changed frequently = higher priority)
- Generate HTML report with interactive filtering
- Add trend tracking (compare scans over time)
- GitHub integration to auto-create issues
