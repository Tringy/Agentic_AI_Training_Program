# Test Suite for Production AI Agent

Comprehensive test suite covering all components of the production-ready AI agent template.

## Test Structure

### Core Test Files

1. **test_agent.py** - Agent logic and LLM integration
   - Query processing with mocked LLM
   - Confidence calculation
   - Reasoning extraction
   - Cost tracking and latency measurement
   - Error handling (API errors, rate limits)
   - Integration with cache, bias detector, and audit trail

2. **test_api.py** - FastAPI endpoints
   - `/health` endpoint
   - `/agent/query` endpoint (main agent endpoint)
   - `/metrics` endpoint
   - `/rate-limit/{user_id}` endpoint
   - CORS headers validation
   - Error handling (400, 404, 422, 429, 500)
   - Request logging middleware

3. **test_rate_limiter.py** - Rate limiting functionality
   - RPM (requests per minute) limits
   - TPM (tokens per minute) limits
   - Token bucket algorithm implementation
   - Per-user rate limiting
   - Burst capacity handling
   - Thread safety

4. **test_cache.py** - Caching mechanisms
   - Exact cache hit/miss
   - Request hashing consistency
   - Cache TTL expiration
   - Cache statistics
   - Multiple entries handling
   - Concurrent access

5. **test_security.py** - Input validation and security
   - Prompt injection detection
   - Max length enforcement
   - Input sanitization
   - Special characters handling
   - Multiple injection patterns
   - False positive prevention

6. **test_governance.py** - Responsible AI components
   - Bias detection in text
   - Gendered language detection
   - Audit trail logging
   - Human-in-the-loop workflows
   - Risk-based approval thresholds
   - Complete governance pipeline

7. **conftest.py** - Pytest configuration and fixtures
   - Mock LLM clients
   - Component fixtures (cache, rate limiter, validators)
   - Sample data and test payloads
   - Setup/teardown utilities

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_agent.py
pytest tests/test_api.py
pytest tests/test_rate_limiter.py
```

### Run Specific Test Class
```bash
pytest tests/test_agent.py::TestProductionAgent
pytest tests/test_api.py::TestHealthEndpoint
```

### Run Specific Test Function
```bash
pytest tests/test_agent.py::TestProductionAgent::test_process_basic_query
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run with Verbose Output
```bash
pytest tests/ -v
```

### Run Async Tests Only
```bash
pytest tests/ -k "asyncio"
```

### Run Fast Tests (exclude slow)
```bash
pytest tests/ -m "not slow"
```

## Test Coverage Goals

Target: 80%+ coverage for all components

- **Agent**: 85%+ (core logic)
- **API**: 80%+ (endpoints and middleware)
- **Rate Limiter**: 85%+ (token bucket algorithm)
- **Cache**: 80%+ (cache operations)
- **Security**: 85%+ (input validation)
- **Governance**: 75%+ (bias detection and audit)

## Test Patterns Used

### Mocking
- Mock Anthropic API client for deterministic tests
- Mock external dependencies (storage, databases)
- Mock time-dependent operations

### Fixtures
- Shared component instances
- Sample data and payloads
- Setup/teardown automation

### Parametrization
- Test multiple scenarios with same test logic
- Edge cases and boundary conditions

### Async Testing
- Use `pytest-asyncio` for async functions
- Test concurrent request handling

## Common Test Scenarios

### Happy Path Tests
- Normal operation with valid inputs
- Expected outputs and behavior

### Error Handling Tests
- Invalid inputs
- Missing required fields
- API errors and timeouts
- Rate limit exceeded

### Edge Cases
- Empty inputs
- Very long inputs
- Special characters
- Concurrent access

### Integration Tests
- Component interactions
- End-to-end workflows
- Full pipeline execution

## Test Data

Sample data is provided via fixtures in `conftest.py`:

- `sample_query` - Standard test query
- `sample_context` - Request context data
- `sample_agent_request` - Complete API request payload
- `sample_injection_attempt` - Malicious input for security testing

## Debugging Tests

### Run with Print Statements
```bash
pytest tests/ -s
```

### Run with Debug on Failure
```bash
pytest tests/ --pdb
```

### Show Local Variables on Failure
```bash
pytest tests/ -l
```

### Run Last Failed Tests
```bash
pytest tests/ --lf
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables (use test values)
3. Run tests: `pytest tests/ --cov=src`
4. Generate coverage report
5. Fail if coverage < 80%

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure tests pass: `pytest tests/`
3. Check coverage: `pytest --cov=src`
4. Update this README if adding new test files

## Notes

- Some tests may be skipped if optional dependencies are not installed
- Mock implementations are used extensively to avoid external API calls
- Tests are designed to be fast and deterministic
- Some stub implementations may cause tests to pass trivially (implement full logic for complete testing)

## Dependencies

Required for testing:
- pytest
- pytest-asyncio
- pytest-cov
- httpx (FastAPI test client)
- Mock/unittest.mock (standard library)

Install all test dependencies:
```bash
pip install -r requirements.txt
```
