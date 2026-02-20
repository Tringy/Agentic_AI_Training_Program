# Test Suite Structure

Visual overview of the test suite organization and architecture.

## Directory Structure

```
fullstack-production-agent/
├── src/                          # Source code
│   ├── agent.py                 # ProductionAgent class
│   ├── cache.py                 # LLMCache class
│   ├── governance.py            # BiasDetector, AuditTrail, HITL
│   ├── llm_client.py            # LLM client with retry
│   ├── main.py                  # FastAPI application
│   ├── rate_limiter.py          # RateLimiter class
│   └── security.py              # InputValidator class
│
├── tests/                        # Test suite (THIS DIRECTORY)
│   ├── __init__.py              # Package marker
│   ├── conftest.py              # Shared fixtures and utilities
│   │
│   ├── test_agent.py            # Tests for agent.py
│   ├── test_api.py              # Tests for main.py (API)
│   ├── test_cache.py            # Tests for cache.py
│   ├── test_governance.py       # Tests for governance.py
│   ├── test_rate_limiter.py     # Tests for rate_limiter.py
│   ├── test_security.py         # Tests for security.py
│   │
│   ├── README.md                # Test documentation
│   ├── SUMMARY.md               # Test suite overview
│   ├── TEST_COVERAGE.md         # Coverage details
│   ├── STRUCTURE.md             # This file
│   └── requirements-test.txt    # Test dependencies
│
├── pytest.ini                    # Pytest configuration
├── run_tests.sh                  # Test runner script
├── TESTING.md                    # Quick reference guide
└── requirements.txt              # Project dependencies
```

## Test File Mapping

| Source File | Test File | Tests | Lines | Coverage Target |
|-------------|-----------|-------|-------|-----------------|
| `src/agent.py` | `tests/test_agent.py` | 24 | 277 | 85%+ |
| `src/main.py` | `tests/test_api.py` | 26 | 361 | 80%+ |
| `src/cache.py` | `tests/test_cache.py` | 23 | 341 | 80%+ |
| `src/governance.py` | `tests/test_governance.py` | 30 | 426 | 75%+ |
| `src/rate_limiter.py` | `tests/test_rate_limiter.py` | 19 | 303 | 85%+ |
| `src/security.py` | `tests/test_security.py` | 29 | 319 | 85%+ |
| `tests/conftest.py` | (fixtures) | - | 218 | - |

## Test Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Execution Flow                       │
└─────────────────────────────────────────────────────────────┘

1. pytest discovers tests
        ↓
2. conftest.py loads fixtures
        ↓
3. Mock objects created
        ↓
4. Tests execute in isolation
        ↓
5. Assertions verify behavior
        ↓
6. Coverage measured
        ↓
7. Results reported
```

## Component Test Coverage

### 1. Agent Tests (`test_agent.py`)

```
TestProductionAgent
├── Query Processing
│   ├── test_process_basic_query
│   ├── test_process_with_context
│   ├── test_process_with_user_id
│   └── test_concurrent_requests
│
├── Metrics & Tracking
│   ├── test_confidence_calculation
│   ├── test_reasoning_extraction
│   ├── test_cost_calculation
│   ├── test_cost_calculation_accuracy
│   └── test_latency_tracking
│
├── Integration
│   ├── test_bias_detection_integration
│   ├── test_bias_detection_disabled
│   ├── test_audit_trail_logging
│   └── test_audit_trail_disabled
│
├── Error Handling
│   ├── test_error_handling_api_error
│   └── test_error_handling_rate_limit
│
└── Edge Cases
    ├── test_empty_query_handling
    ├── test_long_query_handling
    └── test_special_characters_in_query
```

### 2. API Tests (`test_api.py`)

```
TestHealthEndpoint
├── test_health_check_success
└── test_health_check_response_format

TestAgentQueryEndpoint
├── Request Validation
│   ├── test_query_missing_required_fields
│   ├── test_query_empty_query
│   └── test_query_too_long
│
├── Success Scenarios
│   ├── test_query_success
│   ├── test_query_with_context
│   └── test_query_cache_hit
│
└── Security & Limits
    ├── test_query_rate_limit_exceeded
    ├── test_query_injection_detection
    └── test_query_internal_error

TestMetricsEndpoint
├── test_metrics_initial_state
└── test_metrics_after_requests

TestRateLimitStatusEndpoint
└── test_rate_limit_status

TestCORSHeaders
├── test_cors_headers_present
├── test_cors_allows_all_origins
└── test_cors_on_post_request

TestErrorHandling
├── test_404_not_found
├── test_405_method_not_allowed
├── test_422_validation_error_format
└── test_500_error_format

TestRequestLoggingMiddleware
├── test_request_logging
└── test_error_request_logging
```

### 3. Cache Tests (`test_cache.py`)

```
TestLLMCache
├── Initialization
│   ├── test_cache_initialization
│   └── test_cache_default_ttl
│
├── Hashing
│   ├── test_hash_request_consistency
│   ├── test_hash_request_different_messages
│   ├── test_hash_request_different_models
│   └── test_hash_request_message_order
│
├── Cache Operations
│   ├── test_cache_miss_empty_cache
│   ├── test_cache_set_and_get
│   ├── test_cache_hit_exact_match
│   ├── test_cache_miss_different_query
│   ├── test_cache_miss_different_model
│   ├── test_cache_ttl_expiration
│   ├── test_cache_multiple_entries
│   └── test_cache_update_existing_entry
│
├── Statistics
│   ├── test_cache_statistics_initial
│   └── test_cache_statistics_after_set
│
└── Edge Cases
    ├── test_cache_with_complex_messages
    ├── test_cache_with_metadata
    ├── test_cache_special_characters
    ├── test_cache_very_long_content
    ├── test_cache_concurrent_access
    └── test_cache_invalidation_manual
```

### 4. Governance Tests (`test_governance.py`)

```
TestBiasDetector
├── Initialization
│   ├── test_bias_detector_initialization
│   └── test_gendered_terms_defined
│
├── Detection
│   ├── test_detect_bias_neutral_text
│   ├── test_detect_bias_gendered_language
│   ├── test_detect_bias_stereotypical_roles
│   ├── test_detect_bias_inclusive_language
│   ├── test_detect_bias_with_context
│   ├── test_detect_bias_score_range
│   ├── test_detect_bias_multiple_types
│   └── test_detect_bias_suggestions_format
│
└── Edge Cases
    ├── test_detect_bias_empty_text
    ├── test_detect_bias_long_text
    └── test_detect_bias_special_characters

TestAuditTrail
├── test_audit_trail_initialization
├── test_log_decision_basic
├── test_log_decision_with_metadata
├── test_log_decision_default_actor
├── test_log_decision_different_action_types
├── test_log_decision_complex_input_data
└── test_log_decision_complex_output_data

TestHumanInTheLoopAgent
├── test_hitl_agent_initialization
├── test_hitl_agent_default_timeout
├── test_execute_with_approval_low_risk
├── test_execute_with_approval_high_risk
├── test_execute_with_approval_medium_risk
└── test_pending_requests_storage

TestResponsibleAIIntegration
├── test_bias_detection_and_audit_trail
├── test_full_governance_pipeline
└── test_bias_thresholds
```

### 5. Rate Limiter Tests (`test_rate_limiter.py`)

```
TestTokenBucket
└── test_token_bucket_initialization

TestRateLimiter
├── Initialization
│   ├── test_rate_limiter_initialization
│   └── test_rate_limiter_default_values
│
├── Token Acquisition
│   ├── test_acquire_single_token_success
│   └── test_acquire_multiple_tokens
│
├── Limit Enforcement
│   ├── test_rpm_limit_enforcement
│   ├── test_tpm_limit_enforcement
│   ├── test_burst_capacity
│   └── test_token_refill_over_time
│
├── Per-User Limiting
│   ├── test_per_user_rate_limiting
│   └── test_multiple_users_independent_limits
│
├── Status & Management
│   ├── test_get_status
│   └── test_rate_limiter_reset
│
└── Edge Cases
    ├── test_thread_safety
    ├── test_zero_tokens_acquire
    ├── test_negative_tokens_acquire
    ├── test_very_large_token_request
    └── test_concurrent_user_access
```

### 6. Security Tests (`test_security.py`)

```
TestInputValidator
├── Initialization
│   ├── test_validator_initialization
│   └── test_injection_patterns_compiled
│
├── Injection Detection
│   ├── test_check_injection_clean_input
│   ├── test_check_injection_ignore_instructions
│   ├── test_check_injection_disregard_pattern
│   ├── test_check_injection_forget_pattern
│   ├── test_check_injection_system_prompt_pattern
│   ├── test_check_injection_you_are_now_pattern
│   ├── test_check_injection_pretend_pattern
│   ├── test_check_injection_repeat_pattern
│   ├── test_check_injection_case_insensitive
│   ├── test_check_injection_multiple_patterns
│   └── test_injection_patterns_comprehensive
│
├── Sanitization
│   ├── test_sanitize_normal_text
│   ├── test_sanitize_max_length_enforcement
│   ├── test_sanitize_exactly_max_length
│   ├── test_sanitize_default_max_length
│   ├── test_sanitize_special_characters
│   ├── test_sanitize_html_content
│   ├── test_sanitize_sql_injection_attempt
│   ├── test_sanitize_newlines_and_tabs
│   ├── test_sanitize_unicode_characters
│   └── test_sanitize_whitespace_only
│
├── Validate & Sanitize
│   ├── test_validate_and_sanitize_clean_input
│   ├── test_validate_and_sanitize_injection_attempt
│   ├── test_validate_and_sanitize_long_input
│   ├── test_validate_and_sanitize_empty_input
│   └── test_validate_and_sanitize_preserves_meaning
│
└── Edge Cases
    ├── test_false_positives_benign_queries
    └── test_boundary_cases
```

## Fixture Organization (`conftest.py`)

```
conftest.py
│
├── Configuration
│   ├── event_loop (async support)
│   └── reset_metrics (cleanup)
│
├── Mock LLM
│   ├── MockAnthropicResponse
│   ├── mock_anthropic_client
│   └── mock_anthropic_error_client
│
├── Components
│   ├── cache
│   ├── rate_limiter
│   ├── input_validator
│   ├── bias_detector
│   ├── mock_audit_trail
│   └── production_agent
│
├── API Testing
│   ├── test_client
│   └── mock_settings
│
└── Sample Data
    ├── sample_query
    ├── sample_context
    ├── sample_agent_request
    └── sample_injection_attempt
```

## Test Data Flow

```
┌──────────────┐
│  Test Suite  │
└──────┬───────┘
       │
       ├─────→ conftest.py loads fixtures
       │       │
       │       ├─→ Mock Anthropic Client
       │       ├─→ Component Instances
       │       ├─→ Sample Data
       │       └─→ Test Client
       │
       ├─────→ Test executes with fixtures
       │       │
       │       ├─→ Mock returns deterministic data
       │       ├─→ Component processes request
       │       └─→ Assertions verify behavior
       │
       └─────→ Coverage measured
               │
               └─→ Report generated
```

## Test Execution Strategies

### Parallel Execution
```
pytest tests/ -n auto

Process 1: test_agent.py
Process 2: test_api.py
Process 3: test_cache.py
Process 4: test_governance.py
Process 5: test_rate_limiter.py
Process 6: test_security.py
```

### Sequential by Module
```
pytest tests/test_agent.py      (24 tests)
pytest tests/test_api.py        (26 tests)
pytest tests/test_cache.py      (23 tests)
pytest tests/test_governance.py (30 tests)
pytest tests/test_rate_limiter.py (19 tests)
pytest tests/test_security.py   (29 tests)
```

### By Test Category
```
pytest tests/ -m unit           (unit tests)
pytest tests/ -m integration    (integration tests)
pytest tests/ -m api            (API tests)
pytest tests/ -m security       (security tests)
```

## Documentation Hierarchy

```
TESTING.md (Root)
    │
    ├─→ Quick Reference
    │   ├─ Common commands
    │   ├─ Environment setup
    │   └─ Troubleshooting
    │
    └─→ tests/README.md
        │
        ├─→ Detailed Documentation
        ├─→ Test Patterns
        └─→ Contributing
            │
            ├─→ tests/SUMMARY.md
            │   ├─ Files created
            │   ├─ Statistics
            │   └─ Success criteria
            │
            ├─→ tests/TEST_COVERAGE.md
            │   ├─ Coverage by component
            │   ├─ Code paths covered
            │   └─ Coverage goals
            │
            └─→ tests/STRUCTURE.md (This file)
                ├─ Visual hierarchy
                ├─ Test organization
                └─ Data flow
```

## Integration Points

```
Test Suite ←→ Source Code
     ↓
conftest.py (fixtures)
     ↓
Mock Objects (no external calls)
     ↓
Assertions (verify behavior)
     ↓
Coverage Report (measure completeness)
```

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Test Files | 6 |
| Total Test Cases | 151 |
| Total Lines of Test Code | 2,256 |
| Documentation Files | 4 |
| Configuration Files | 3 |
| Fixtures Defined | 15+ |
| Mock Objects | 3 |
| Coverage Target | 80%+ |

---

**Last Updated**: January 26, 2026
**Status**: Complete and Production-Ready
