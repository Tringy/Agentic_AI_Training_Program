# Challenge 02: AI Code Reviewer

## Description

Build a complete automated code review system that integrates with GitHub, analyzes PRs, detects issues, and learns from human feedback.

**Difficulty**: Advanced-Expert
**Estimated time**: 25-35 hours
**Stack**: Python/Node + GitHub API + LLM + Vector DB

---

## Objectives

System that automatically:
- ✅ Reviews each Pull Request
- ✅ Detects bugs, security issues, performance problems
- ✅ Suggests improvements with diffs
- ✅ Learns from human code reviews
- ✅ Integrates with CI/CD
- ✅ Generates code metrics

---

## Features Core

### 1. GitHub Integration

```python
class GitHubIntegration:
    def __init__(self, token: str):
        self.github = Github(token)

    async def on_pull_request(self, event):
        pr = event.pull_request

        # Get files changed
        files = pr.get_files()

        # Review each file
        reviews = []
        for file in files:
            review = await self.review_file(file)
            reviews.append(review)

        # Post review
        await self.post_review(pr, reviews)

    async def review_file(self, file) -> FileReview:
        # Get diff
        diff = file.patch

        # Analyze with LLM
        issues = await self.analyzer.analyze(
            file.filename,
            diff,
            file.previous_content
        )

        return FileReview(
            file=file.filename,
            issues=issues
        )

    async def post_review(self, pr, reviews):
        # Create review comments
        comments = []
        for review in reviews:
            for issue in review.issues:
                comments.append({
                    "path": review.file,
                    "line": issue.line,
                    "body": issue.comment,
                    "side": "RIGHT"
                })

        # Submit review
        pr.create_review(
            body=self._generate_summary(reviews),
            event="COMMENT",  # or "REQUEST_CHANGES"
            comments=comments
        )
```

### 2. Multi-Dimensional Analysis

```python
class CodeAnalyzer:
    def __init__(self):
        self.analyzers = [
            BugDetector(),
            SecurityAnalyzer(),
            PerformanceAnalyzer(),
            BestPracticesChecker(),
            TypeChecker(),
        ]

    async def analyze(self, file: str, diff: str, context: str):
        issues = []

        # Run all analyzers in parallel
        results = await asyncio.gather(*[
            analyzer.analyze(file, diff, context)
            for analyzer in self.analyzers
        ])

        for result in results:
            issues.extend(result.issues)

        # Deduplicate and prioritize
        return self.prioritize(self.deduplicate(issues))

class BugDetector:
    async def analyze(self, file, diff, context):
        prompt = f"""
Review this code change for potential bugs:

File: {file}
Diff:
{diff}

Context:
{context}

Identify:
1. Logic errors
2. Edge cases not handled
3. Null pointer risks
4. Type errors
5. Off-by-one errors

For each issue, provide:
- Line number
- Severity (critical/major/minor)
- Description
- Suggested fix

Output as JSON array.
"""

        response = await llm.complete(prompt)
        return self._parse_issues(response)

class SecurityAnalyzer:
    SECURITY_PATTERNS = [
        r'eval\(',  # Code injection
        r'exec\(',
        r'\.innerHTML\s*=',  # XSS
        r'password.*=.*input',  # Plaintext password
    ]

    async def analyze(self, file, diff, context):
        issues = []

        # Pattern matching
        for line_no, line in enumerate(diff.split('\n')):
            for pattern in self.SECURITY_PATTERNS:
                if re.search(pattern, line):
                    issues.append(SecurityIssue(
                        line=line_no,
                        severity="critical",
                        description=f"Security risk: {pattern}",
                        pattern=pattern
                    ))

        # LLM-based analysis
        llm_issues = await self._llm_security_check(diff, context)
        issues.extend(llm_issues)

        return issues
```

### 3. Smart Suggestions with Diffs

```python
class SuggestionGenerator:
    async def generate_fix(self, issue: Issue, code: str):
        prompt = f"""
Given this code with an issue:

{code}

Issue: {issue.description}
Line: {issue.line}

Provide:
1. Fixed code
2. Explanation of changes

Format as:
FIXED_CODE:
```
[corrected code here]
```

EXPLANATION:
[explanation here]
"""

        response = await llm.complete(prompt)
        fixed_code = self._extract_code(response)
        explanation = self._extract_explanation(response)

        # Generate diff
        diff = self._create_diff(code, fixed_code)

        return Suggestion(
            original=code,
            fixed=fixed_code,
            diff=diff,
            explanation=explanation
        )

    def _create_diff(self, original, fixed):
        # Use difflib to create unified diff
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            fixed.splitlines(keepends=True),
            fromfile='original',
            tofile='fixed'
        )
        return ''.join(diff)
```

### 4. Learning System

```python
class LearningReviewer:
    """Learn from human code reviews"""

    def __init__(self):
        self.review_db = ReviewDatabase()
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

    async def learn_from_review(self, pr: PullRequest):
        # Get human review comments
        comments = pr.get_review_comments()

        for comment in comments:
            # Extract pattern
            pattern = await self._extract_pattern(comment)

            # Store for future reference
            await self.review_db.store(
                code=comment.diff_hunk,
                comment=comment.body,
                pattern=pattern,
                reviewer=comment.user.login,
                embedding=self.embedder.encode(comment.diff_hunk)
            )

    async def suggest_similar_reviews(self, code: str):
        """Find similar past reviews"""
        code_embedding = self.embedder.encode(code)

        similar_reviews = await self.review_db.search(
            embedding=code_embedding,
            limit=5
        )

        return [
            f"Similar past review: {r.comment}"
            for r in similar_reviews
        ]
```

### 5. Quality Metrics

```python
class QualityMetrics:
    def calculate_metrics(self, pr: PullRequest):
        metrics = {
            "complexity": self._calculate_complexity(pr),
            "test_coverage_delta": self._coverage_change(pr),
            "documentation_score": self._doc_score(pr),
            "maintainability_index": self._maintainability(pr),
            "technical_debt": self._tech_debt(pr),
        }

        return metrics

    def _calculate_complexity(self, pr):
        """Calculate cyclomatic complexity"""
        total_complexity = 0

        for file in pr.get_files():
            if file.filename.endswith('.py'):
                complexity = radon.complexity.cc_visit(file.content)
                total_complexity += sum(c.complexity for c in complexity)

        return total_complexity

    def _coverage_change(self, pr):
        """Calculate test coverage delta"""
        before_coverage = self._get_coverage(pr.base.sha)
        after_coverage = self._get_coverage(pr.head.sha)

        return after_coverage - before_coverage
```

---

## Advanced Features

### 1. Context-Aware Reviews

```python
async def context_aware_review(self, pr: PullRequest):
    # Gather context
    context = {
        "repo_description": pr.base.repo.description,
        "recent_issues": await self._get_recent_issues(pr.base.repo),
        "coding_standards": await self._load_coding_standards(pr.base.repo),
        "recent_commits": pr.base.repo.get_commits()[:10],
    }

    # Review with context
    for file in pr.get_files():
        review = await self.review_with_context(
            file=file,
            context=context
        )

        await self.post_review(pr, review)
```

### 2. Incremental Reviews

```python
class IncrementalReviewer:
    """Only review new changes to PR"""

    def __init__(self):
        self.reviewed_commits = {}

    async def review_incrementally(self, pr: PullRequest):
        last_reviewed = self.reviewed_commits.get(pr.number)

        if last_reviewed:
            # Only review commits after last_reviewed
            new_commits = pr.get_commits().reversed[
                :list(pr.get_commits()).index(last_reviewed)
            ]
        else:
            new_commits = pr.get_commits()

        for commit in new_commits:
            await self.review_commit(commit)

        self.reviewed_commits[pr.number] = pr.head.sha
```

### 3. Team-Specific Customization

```python
class TeamCustomReviewer:
    """Customize reviews per team"""

    def __init__(self):
        self.team_configs = self._load_configs()

    def _load_configs(self):
        # Load from .ai-reviewer.yml in repo
        return {
            "backend": {
                "focus": ["security", "performance"],
                "strict": True,
                "auto_approve_threshold": 0.95
            },
            "frontend": {
                "focus": ["accessibility", "responsiveness"],
                "strict": False,
                "auto_approve_threshold": 0.85
            }
        }

    async def review(self, pr: PullRequest):
        # Detect team from labels or files
        team = self._detect_team(pr)

        config = self.team_configs[team]

        # Customize analysis
        self.analyzer.set_focus(config["focus"])
        self.analyzer.set_strictness(config["strict"])

        # Review
        result = await self.analyzer.analyze(pr)

        # Auto-approve if high quality
        if result.score > config["auto_approve_threshold"]:
            await pr.create_review(
                body="✅ LGTM - Auto-approved",
                event="APPROVE"
            )
```

---

## Deployment

### GitHub App

```python
# app.py
from flask import Flask, request
from github_webhook import Webhook

app = Flask(__name__)
webhook = Webhook(app, secret=WEBHOOK_SECRET)

@webhook.hook()
async def on_pull_request(data):
    action = data['action']

    if action in ['opened', 'synchronize', 'reopened']:
        pr = data['pull_request']
        await reviewer.review_pr(pr)

if __name__ == '__main__':
    app.run(port=3000)
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Testing

```python
async def test_bug_detection():
    code = """
def divide(a, b):
    return a / b  # No zero check!
"""

    issues = await bug_detector.analyze(code)

    assert any('zero' in issue.description.lower() for issue in issues)

async def test_security_check():
    code = """
user_input = request.GET['data']
eval(user_input)  # Code injection!
"""

    issues = await security_analyzer.analyze(code)

    assert any(issue.severity == 'critical' for issue in issues)
```

---

## Evaluation

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Accuracy** | 35% | Correctly identifies issues |
| **GitHub Integration** | 25% | Seamless PR workflow |
| **Learning System** | 20% | Learns from feedback |
| **Performance** | 10% | < 2 min per PR |
| **UX** | 10% | Clear, actionable comments |

---

## Submission

1. Working GitHub App deployed
2. Demo reviewing real PRs
3. Metrics showing improvements
4. Documentation

---

**¡Automatiza code reviews! 🔍**
