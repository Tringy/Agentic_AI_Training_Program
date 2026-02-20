# Test Suite Index

Quick navigation for the comprehensive test suite.

## Main Documentation

| Document | Purpose | Lines |
|----------|---------|-------|
| [README.md](README.md) | Complete test documentation and usage | ~200 |
| [SUMMARY.md](SUMMARY.md) | Test suite overview and statistics | ~300 |
| [TEST_COVERAGE.md](TEST_COVERAGE.md) | Detailed coverage report | ~400 |
| [STRUCTURE.md](STRUCTURE.md) | Visual hierarchy and architecture | ~500 |
| [INDEX.md](INDEX.md) | This file - quick navigation | ~100 |

## Test Files

| File | Tests | Lines | Coverage Target | Purpose |
|------|-------|-------|-----------------|---------|
| [test_agent.py](test_agent.py) | 24 | 277 | 85%+ | Agent logic and LLM integration |
| [test_api.py](test_api.py) | 26 | 361 | 80%+ | FastAPI endpoints and middleware |
| [test_cache.py](test_cache.py) | 23 | 341 | 80%+ | Caching mechanisms |
| [test_governance.py](test_governance.py) | 30 | 426 | 75%+ | Responsible AI components |
| [test_rate_limiter.py](test_rate_limiter.py) | 19 | 303 | 85%+ | Rate limiting with token bucket |
| [test_security.py](test_security.py) | 29 | 319 | 85%+ | Input validation and security |

## Configuration & Utilities

| File | Purpose |
|------|---------|
| [conftest.py](conftest.py) | Pytest fixtures and test utilities |
| [requirements-test.txt](requirements-test.txt) | Test-specific dependencies |
| [../pytest.ini](../pytest.ini) | Pytest configuration |
| [../run_tests.sh](../run_tests.sh) | Test runner script |
| [../TESTING.md](../TESTING.md) | Quick reference guide |

## Quick Links

### Getting Started
- [Installation Instructions](README.md#quick-start)
- [Running Tests](../TESTING.md#quick-start)
- [Test Runner](../TESTING.md#using-the-test-runner-script)

### Test Details
- [Agent Tests](STRUCTURE.md#1-agent-tests-test_agentpy)
- [API Tests](STRUCTURE.md#2-api-tests-test_apipy)
- [Cache Tests](STRUCTURE.md#3-cache-tests-test_cachepy)
- [Governance Tests](STRUCTURE.md#4-governance-tests-test_governancepy)
- [Rate Limiter Tests](STRUCTURE.md#5-rate-limiter-tests-test_rate_limiterpy)
- [Security Tests](STRUCTURE.md#6-security-tests-test_securitypy)

### Coverage Reports
- [Coverage by Component](TEST_COVERAGE.md#coverage-by-component)
- [Summary Statistics](TEST_COVERAGE.md#summary-statistics)
- [Not Covered](TEST_COVERAGE.md#not-covered-by-design)

### Development
- [Adding New Tests](README.md#contributing)
- [Test Patterns](README.md#test-patterns-used)
- [Best Practices](../TESTING.md#best-practices)

## Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific file
pytest tests/test_agent.py -v

# Run with test runner
./run_tests.sh
```

## Test Statistics

- **Total Tests**: 151
- **Total Lines**: 2,256
- **Coverage Target**: 80%+
- **Test Files**: 6
- **Fixtures**: 15+
- **Documentation**: 4 files

## Status

✅ All test files created
✅ Comprehensive coverage
✅ Documentation complete
✅ CI/CD ready
✅ Production-ready

---

**Created**: January 26, 2026
**Status**: Complete
