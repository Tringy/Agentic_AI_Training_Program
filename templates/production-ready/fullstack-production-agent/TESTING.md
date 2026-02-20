# Testing Guide

Quick reference guide for running tests in the Production AI Agent project.

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest tests/
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### View Coverage Report
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## Test Commands

### Basic Commands

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with extra verbose output (show test names)
pytest tests/ -vv

# Run with summary of all outcomes
pytest tests/ -ra
```

### Run Specific Tests

```bash
# Run specific file
pytest tests/test_agent.py

# Run specific class
pytest tests/test_agent.py::TestProductionAgent

# Run specific test
pytest tests/test_agent.py::TestProductionAgent::test_process_basic_query

# Run tests matching pattern
pytest tests/ -k "cache"
pytest tests/ -k "test_api or test_agent"
```

### Coverage Options

```bash
# Basic coverage
pytest tests/ --cov=src

# Coverage with missing lines
pytest tests/ --cov=src --cov-report=term-missing

# HTML coverage report
pytest tests/ --cov=src --cov-report=html

# Fail if coverage below threshold
pytest tests/ --cov=src --cov-fail-under=80

# Multiple report formats
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

### Performance Options

```bash
# Run tests in parallel (requires pytest-xdist)
pytest tests/ -n auto

# Run tests in parallel with 4 workers
pytest tests/ -n 4

# Show slowest tests
pytest tests/ --durations=10
```

### Debugging Options

```bash
# Show print statements
pytest tests/ -s

# Stop on first failure
pytest tests/ -x

# Drop into debugger on failure
pytest tests/ --pdb

# Show local variables on failure
pytest tests/ -l

# Run last failed tests only
pytest tests/ --lf

# Run failed tests first
pytest tests/ --ff
```

### Output Options

```bash
# Quiet output (only show failures)
pytest tests/ -q

# Show capture output on failure
pytest tests/ --tb=short

# No capture (show all output immediately)
pytest tests/ --capture=no
```

---

## Using the Test Runner Script

The `run_tests.sh` script provides convenient test execution:

```bash
# Basic usage
./run_tests.sh

# Skip coverage
./run_tests.sh --no-coverage

# Verbose output
./run_tests.sh --verbose

# Run in parallel
./run_tests.sh --parallel

# Run specific test file
./run_tests.sh --test tests/test_agent.py

# Show help
./run_tests.sh --help
```

---

## Environment Setup

### Required Environment Variables

```bash
# Set test API key
export ANTHROPIC_API_KEY="test_api_key_12345"

# Set environment
export ENVIRONMENT="test"
```

### Using .env File

Create `.env.test`:
```env
ANTHROPIC_API_KEY=test_api_key_12345
ENVIRONMENT=test
DEBUG=false
```

Load before tests:
```bash
source .env.test
pytest tests/
```

---

## Test Organization

### Test Files Structure
```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Shared fixtures
├── test_agent.py            # Agent tests
├── test_api.py              # API tests
├── test_rate_limiter.py     # Rate limiter tests
├── test_cache.py            # Cache tests
├── test_security.py         # Security tests
└── test_governance.py       # Governance tests
```

### Test Markers

Tests can be marked for selective execution:

```python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.security
@pytest.mark.slow
@pytest.mark.asyncio
```

Run by marker:
```bash
pytest tests/ -m "unit"
pytest tests/ -m "not slow"
pytest tests/ -m "api or security"
```

---

## Common Test Scenarios

### Test Agent Behavior
```bash
pytest tests/test_agent.py -v
```

### Test API Endpoints
```bash
pytest tests/test_api.py -v
```

### Test Security
```bash
pytest tests/test_security.py -v
```

### Test All Async Functions
```bash
pytest tests/ -k "asyncio" -v
```

### Test Error Handling
```bash
pytest tests/ -k "error" -v
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

### GitLab CI Example

```yaml
test:
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - pytest tests/ --cov=src --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

---

## Troubleshooting

### Tests Fail to Import Modules

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Ensure you're running from project root:
```bash
cd /path/to/fullstack-production-agent
pytest tests/
```

### Async Tests Not Running

**Problem**: Async tests are skipped

**Solution**: Install pytest-asyncio:
```bash
pip install pytest-asyncio
```

### Coverage Not Working

**Problem**: Coverage reports 0%

**Solution**: Ensure source path is correct:
```bash
pytest tests/ --cov=src --cov-report=term
```

### Tests Running Slowly

**Problem**: Tests take too long

**Solution**: Run in parallel:
```bash
pip install pytest-xdist
pytest tests/ -n auto
```

### Environment Variable Issues

**Problem**: Tests fail due to missing env vars

**Solution**: Set required variables:
```bash
export ANTHROPIC_API_KEY="test_key"
pytest tests/
```

---

## Best Practices

### Before Committing

```bash
# Run all tests
pytest tests/

# Check coverage
pytest tests/ --cov=src --cov-fail-under=80

# Run linting (if configured)
flake8 src/ tests/

# Run type checking (if configured)
mypy src/
```

### During Development

```bash
# Run relevant tests only
pytest tests/test_agent.py -v

# Use watch mode (requires pytest-watch)
ptw tests/test_agent.py

# Stop on first failure
pytest tests/ -x -v
```

### For Pull Requests

```bash
# Full test suite with coverage
pytest tests/ --cov=src --cov-report=html -v

# Check coverage threshold
pytest tests/ --cov=src --cov-fail-under=80

# Generate coverage badge
coverage-badge -o coverage.svg -f
```

---

## Additional Resources

### Documentation
- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)

### Test Files
- See `tests/README.md` for detailed test documentation
- See `tests/TEST_COVERAGE.md` for coverage report
- See `conftest.py` for available fixtures

### Getting Help

```bash
# Pytest help
pytest --help

# List available fixtures
pytest --fixtures

# List available markers
pytest --markers
```

---

## Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Agent | 85% | ✅ |
| API | 80% | ✅ |
| Rate Limiter | 85% | ✅ |
| Cache | 80% | ✅ |
| Security | 85% | ✅ |
| Governance | 75% | ✅ |
| **Overall** | **80%** | **✅** |

---

## Quick Reference Card

```bash
# Run tests
pytest tests/                           # All tests
pytest tests/test_agent.py             # Specific file
pytest tests/ -k "cache"               # Match pattern

# Coverage
pytest tests/ --cov=src                # Basic
pytest tests/ --cov=src --cov-report=html  # HTML report

# Options
pytest tests/ -v                       # Verbose
pytest tests/ -x                       # Stop on first failure
pytest tests/ -s                       # Show print statements
pytest tests/ --lf                     # Last failed
pytest tests/ -n auto                  # Parallel

# Debugging
pytest tests/ --pdb                    # Debug on failure
pytest tests/ -l                       # Show locals
pytest tests/ --tb=short               # Short traceback
```
