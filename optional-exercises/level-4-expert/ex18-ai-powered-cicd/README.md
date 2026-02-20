# Exercise 18: AI-Powered CI/CD Pipeline

## Description
Intelligent CI/CD pipeline that uses AI to optimize builds, tests, and deployments.

## Objectives
- AI-powered test selection
- Intelligent failure analysis
- Auto-fix failing tests
- Code quality gates with LLM
- Deployment risk assessment

## Features

### 1. Smart Test Selection

```python
class SmartTestSelector:
    """Select only tests affected by code changes"""

    async def select_tests(self, changed_files: List[str]) -> List[str]:
        # Analyze code changes
        analysis = await self._analyze_changes(changed_files)

        # Use LLM to predict affected tests
        prompt = f"""
Analyze these code changes and predict which tests are affected:

Changed files:
{chr(10).join(changed_files)}

Code diff:
{self._get_diff()}

List only the test files that need to run.
"""

        response = await llm.complete(prompt)
        tests = self._parse_test_list(response)

        return tests

# Instead of running all 1000 tests, run only 50 affected tests
# Speedup: 20x faster
```

### 2. Failure Analysis Agent

```python
class FailureAnalyzer:
    """Automatically analyze and explain test failures"""

    async def analyze_failure(self, test_output: str):
        # Extract stack trace
        stack_trace = self._extract_stack_trace(test_output)

        # Get relevant code
        relevant_code = await self._get_code_context(stack_trace)

        # AI analysis
        prompt = f"""
Analyze this test failure:

Stack trace:
{stack_trace}

Relevant code:
{relevant_code}

Provide:
1. Root cause
2. Suggested fix
3. Prevention strategy
"""

        analysis = await llm.complete(prompt)

        # Post to PR as comment
        await github.post_comment(pr_number, analysis)
```

### 3. Auto-Fix Agent

```python
class AutoFixAgent:
    """Attempt to automatically fix failing tests"""

    async def auto_fix(self, test_failure: TestFailure):
        # Analyze failure
        analysis = await self.analyzer.analyze(test_failure)

        # Generate fix
        fix = await self._generate_fix(analysis)

        # Apply fix
        await self._apply_fix(fix)

        # Re-run test
        result = await self._run_test(test_failure.test_name)

        if result.passed:
            # Create PR with fix
            await github.create_pr(
                title=f"Auto-fix: {test_failure.test_name}",
                body=f"Automatically fixed test failure\n\n{analysis}"
            )
            return True

        return False
```

### 4. Code Quality Gate

```python
class AICodeQualityGate:
    """LLM-based code review before merge"""

    async def review_pr(self, pr: PullRequest):
        # Get diff
        diff = await github.get_diff(pr.number)

        # AI review
        review = await llm.complete(f"""
Review this code change:

{diff}

Check for:
- Bugs
- Security issues
- Performance problems
- Best practices
- Test coverage

Provide actionable feedback.
""")

        # Parse and post comments
        issues = self._parse_review(review)

        for issue in issues:
            await github.post_inline_comment(
                pr.number,
                issue.file,
                issue.line,
                issue.comment
            )

        # Block merge if critical issues
        if any(i.severity == "critical" for i in issues):
            await github.set_status(pr, "failure", "Critical issues found")
```

### 5. Deployment Risk Assessment

```python
class DeploymentRiskAssessor:
    """Assess risk before deploying to production"""

    async def assess_risk(self, deployment: Deployment) -> RiskScore:
        factors = {
            "code_changes": self._analyze_code_changes(deployment),
            "test_coverage": self._check_coverage(deployment),
            "recent_failures": self._check_recent_incidents(),
            "time_of_day": self._time_risk(),
            "rollback_readiness": self._check_rollback(),
        }

        # AI risk assessment
        prompt = f"""
Assess deployment risk:

Deployment: {deployment.version}
Environment: Production

Factors:
{json.dumps(factors, indent=2)}

Provide risk score (0-100) and recommendation.
"""

        assessment = await llm.complete(prompt)

        risk_score = self._extract_score(assessment)

        # Block if high risk
        if risk_score > 80:
            raise DeploymentBlocked(f"High risk: {risk_score}")

        return assessment
```

## GitHub Actions Integration

```yaml
# .github/workflows/ai-ci.yml
name: AI-Powered CI

on: [push, pull_request]

jobs:
  smart-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Smart Test Selection
        run: |
          python ai_ci/select_tests.py \
            --changed-files "${{ github.event.changed_files }}" \
            > selected_tests.txt

      - name: Run Selected Tests
        run: pytest $(cat selected_tests.txt)

      - name: Analyze Failures
        if: failure()
        run: python ai_ci/analyze_failures.py

      - name: Auto-Fix
        if: failure()
        run: python ai_ci/auto_fix.py

  ai-review:
    runs-on: ubuntu-latest
    steps:
      - name: AI Code Review
        run: python ai_ci/review_pr.py ${{ github.event.number }}

  risk-assessment:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Assess Deployment Risk
        run: |
          python ai_ci/assess_risk.py \
            --version ${{ github.sha }} \
            --environment production
```

## Metrics & Results

Expected improvements:
- CI time: 50-70% faster (smart test selection)
- MTTR: 60% reduction (auto-fix)
- Code quality: Catch issues before merge
- Deployment safety: Risk assessment prevents incidents

**Time**: 15-20h
**Resources**: [GitHub Actions](https://docs.github.com/actions), [pytest](https://pytest.org/)

---

**¡CI/CD inteligente! 🚀**
