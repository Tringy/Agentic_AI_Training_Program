# URL Shortener - Feature Specification for Agent-Driven Development

**Version**: 1.0  
**Last Updated**: February 2026  
**Project Scope**: Lab 01 - Vibe Coding Introduction  
**Target Audience**: AI Agents & Development Teams

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Current State Analysis](#current-state-analysis)
3. [Architecture Constraints](#architecture-constraints-as-is)
4. [Feature Specifications](#feature-specifications)
5. [Frontend Pages](#frontend-pages)
6. [Testing Strategy](#testing-strategy)
7. [How to Use This Spec](#how-to-use-this-spec)
8. [Implementation Guidelines](#implementation-guidelines)

---

## Project Overview

### Vision
Build a production-ready URL shortener service that demonstrates AI-assisted development workflows. The service enables users to convert long URLs into shareable, memorable short links while tracking usage metrics.

### Tech Stack
- **Backend**: Python 3.11+ | FastAPI 0.109+ | SQLite 3
- **Frontend**: Node.js 20+ | Next.js 14+ | React 18+ | TypeScript 5+ | Tailwind CSS 3.4+
- **Deployment**: Docker | Fly.io | GitHub Actions CI/CD
- **Infrastructure**: Persistent volumes for SQLite, environment-based configuration

### Success Metrics
- Production deployment working end-to-end
- <200ms response time for redirect operations
- >95% uptime in production
- Clear agent-driven implementation pattern established

---

## Current State Analysis

### ✅ Fully Implemented & Deployed
- POST /shorten endpoint with unique code generation and collision detection
- GET /{short_code} with HTTP 307 redirects to original URLs
- SQLite persistence with automatic schema initialization
- URL validation using Pydantic HttpUrl
- CORS support for cross-origin requests
- Next.js UI with real-time validation and copy button
- Docker containerization for both backend and frontend
- Docker Compose orchestration
- Environment-based configuration (12-factor)
- Health check endpoint
- Deployment configuration (Fly.io manifests)

### ❌ Not Yet Implemented
- **LRU Caching** - In-memory cache for URL lookups (Feature 1.3)
- **Analytics** - Click tracking and usage metrics (Phase 2)
- **Custom Short Codes** - User-specified codes (Phase 3)
- **URL Expiration** - Time-limited redirects (Phase 3)
- **QR Codes** - QR code generation (Phase 3)
- **Rate Limiting** - Request throttling per IP (Phase 4)
- **Advanced Security** - Input sanitization, open redirect prevention (Phase 4)
- **Database Optimization** - Indices, backups, migrations (Phase 4)
- **Comprehensive Logging** - Structured logging and monitoring (Phase 4)
- **Full Test Suite** - Unit, integration, and performance tests

### Known Limitations (By Design)
- No user authentication system
- No URL ownership verification
- Single-instance deployment (no distributed caching)
- SQLite storage (not suitable for 100k+ URLs at scale)
- No error recovery or disaster recovery plan
- Minimal logging infrastructure

---

## Architecture Constraints (As-Is)

### Backend Runtime Requirements
- All new database operations must be non-blocking (async-ready)
- SQLite file persisted in `/data` volume
- All endpoints return consistent status codes and error formats
- Health check endpoint required for monitoring

### Frontend Runtime Requirements
- API base URL configurable via `NEXT_PUBLIC_API_URL` environment variable
- Network calls must handle timeouts and failures
- UI remains responsive during network delays

### Database Schema Baseline
Current `urls` table structure:
```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_code TEXT UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

All new features must be backward-compatible with existing schema or include migration path.

---

## Feature Specifications

Each feature below is independent and can be implemented in any order. Agent should grab a feature spec and implement it completely including tests.

### Feature: URL Lookup Caching (LRU)

**Functional Requirements**:
1. Cache URL mappings in memory using LRU eviction
2. Reduce database queries for frequently accessed codes
3. Maintain configurable size limit
4. Invalidate cache when new URLs are created
5. Expose cache statistics for monitoring

**Acceptance Criteria**:
```
GIVEN cache is enabled
WHEN accessing same short code multiple times
THEN subsequent hits return <10ms

GIVEN cache at max size
WHEN new entry added
THEN least recently used entry is evicted

GIVEN new URL shortened
WHEN POST /shorten completes
THEN cache is updated/invalidated appropriately
```

**Test Cases**:
- ✓ Cache hit <10ms
- ✓ LRU eviction works correctly
- ✓ Thread-safe concurrent access
- ✓ Cache invalidation on POST /shorten
- ✓ Configurable size via CACHE_SIZE env var

**Implementation**:
- Create `backend/cache.py` with simple LRUCache using cachetools
- Integrate into `get_original_url()` function
- Add GET `/api/cache-stats` endpoint
- Add POST `/api/cache-clear` endpoint (for testing)
- Update requirements.txt: `cachetools==5.3.2`

**Files Updated**:
- backend/cache.py (NEW)
- backend/main.py (integrate caching)
- backend/requirements.txt (add dependency)

---



### Feature: Click Tracking & Analytics

**Functional Requirements**:
1. Track each redirect/click on shortened URLs
2. Record timestamp of each click
3. Optionally record user agent and IP address
4. Provide analytics endpoint for retrieving click data
5. Maintain click count separately for performance

**Acceptance Criteria**:
```
GIVEN a shortened URL is accessed
WHEN GET /{short_code} is called
THEN the system must:
  - Record click with timestamp
  - Still perform redirect immediately (<100ms)
  - Store click data asynchronously (non-blocking)

GIVEN user requests analytics for a short code
WHEN GET /api/analytics/{short_code} is called
THEN the response must:
  - Have status code 200
  - Return {"short_code": "...", "click_count": N, "last_click": "..."}
```

**Schema Changes**:
```sql
CREATE TABLE clicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_code TEXT NOT NULL,
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_agent TEXT,
    ip_address TEXT,
    referrer TEXT,
    FOREIGN KEY(short_code) REFERENCES urls(short_code)
);

ALTER TABLE urls ADD COLUMN click_count INTEGER DEFAULT 0;
```

**Implementation Notes for Agents**:
- Use async database operations to avoid blocking redirect
- Consider caching click counts for frequently accessed codes
- Implement batched inserts for high-traffic scenarios (Phase 4)

---

### Feature: Analytics API Endpoints

**Functional Requirements**:
1. Retrieve analytics for all shortened URLs (paginated)
2. Show click counts, creation date, most popular links
3. Support filtering by date range
4. Return data in JSON format for frontend consumption

**Acceptance Criteria**:
```
GIVEN user requests analytics overview
WHEN GET /api/analytics?page=1&limit=10 is called
THEN response must:
  - Return list of URLs with click counts
  - Include pagination metadata
  - Sort by click count (most popular first)
```

**Files to Add**:
- backend/routes/analytics.py (new module)
- frontend/app/analytics/page.tsx (new page)

---

### Feature: Custom Short Codes

**Functional Requirements**:
1. Allow users to specify custom short codes (optional)
2. Validate custom code format (alphanumeric, 3-20 chars)
3. Check for code availability before accepting
4. Fall back to auto-generated code if custom unavailable
5. Prevent special characters and reserved words

**Acceptance Criteria**:
```
GIVEN user provides custom short code
WHEN POST /shorten includes {"url": "...", "custom_code": "mycode"}
THEN system must:
  - Validate code format
  - Check availability
  - Use custom code if available
  - Reject with 409 Conflict if taken

GIVEN custom code is "api" or other reserved word
WHEN submission is made
THEN response must:
  - Have status code 400
  - Indicate code is reserved
```

**Schema Changes**:
```sql
ALTER TABLE urls ADD COLUMN is_custom BOOLEAN DEFAULT 0;
```

**Files Updated**:
- backend/main.py (POST /shorten endpoint)
- frontend/components/URLShortener.tsx (UI for custom code)

---

### Feature: URL Expiration

**Functional Requirements**:
1. Allow optional expiration date on shortened URLs
2. Return 410 Gone for expired URLs
3. Clean up expired entries (periodic job)
4. Show expiration info in analytics

**Acceptance Criteria**:
```
GIVEN URL with expiration date is accessed
WHEN current date is after expiration
THEN response must:
  - Have status code 410 (Gone)
  - Return message: "This short link has expired"

GIVEN expiration date is set
WHEN GET /api/analytics/{short_code} is called
THEN response must include expiration date
```

**Schema Changes**:
```sql
ALTER TABLE urls ADD COLUMN expires_at TIMESTAMP;
```

---

### Feature: QR Code Generation

**Functional Requirements**:
1. Generate QR code for each shortened URL
2. Return QR code as SVG/PNG on demand
3. QR code links to the short URL
4. Cache generated QR codes

**Acceptance Criteria**:
```
GIVEN user requests QR code
WHEN GET /api/qrcode/{short_code} is called
THEN response must:
  - Have content type image/svg+xml or image/png
  - Display scannable QR code
  - Link to short URL

GIVEN multiple requests for same QR code
WHEN endpoint is called multiple times
THEN QR codes must be cached (<10ms subsequent requests)
```

**Dependencies**:
- qrcode library
- Pillow (PIL) for image processing

**Files to Add**:
- backend/services/qr_generator.py
- backend/routes/qrcode.py

---

### Feature: Rate Limiting

**Functional Requirements**:
1. Limit requests per IP address
2. Implement sliding window rate limiting
3. Return 429 Too Many Requests when exceeded
4. Allow higher limits for authenticated users (future)

**Acceptance Criteria**:
```
GIVEN client makes 100+ requests per minute
WHEN threshold is exceeded
THEN response must:
  - Have status code 429
  - Include Retry-After header
  - Return descriptive error message
```

**Implementation Notes for Agents**:
- Use Redis for distributed rate limiting (Phase 4+)
- Implement in-memory cache for single-instance deployment
- Track by IP or User-Agent header

---

### Feature: Input Validation & Security

**Functional Requirements**:
1. Implement strict URL validation
2. Prevent open redirect vulnerabilities
3. Sanitize user inputs
4. Validate custom codes for injection attacks
5. Implement request size limits

**Acceptance Criteria**:
```
GIVEN malicious input is submitted
WHEN POST /shorten receives {"url": "javascript://alert()"}
THEN response must:
  - Have status code 400
  - Reject input safely
  - Not execute any code
  - Not redirect to malicious URL
```

**Security Tests**:
- ✓ SQL injection attempts blocked
- ✓ Open redirect prevention
- ✓ XSS prevention in responses
- ✓ CSRF token validation (if applicable)

---

### Feature: Database Optimization & Backups

**Functional Requirements**:
1. Add database indexing on frequently queried columns
2. Implement automatic backups
3. Add migration system for schema changes
4. Monitor database size and performance

**Acceptance Criteria**:
```
GIVEN database has 100k+ URLs
WHEN lookup or insertion is performed
THEN operations must complete in <50ms

GIVEN system failure occurs
WHEN database is recovered from backup
THEN all data must be consistent and accessible
```

**Implementation**:
- Create indices on: short_code, original_url, created_at
- Implement backup job (daily snapshots)
- Use Alembic for schema migrations

---

### Feature: Comprehensive Logging & Monitoring

**Functional Requirements**:
1. Log all operations (create, redirect, error)
2. Include request tracking IDs
3. Monitor performance metrics
4. Alert on anomalies
5. Centralize logs for debugging

**Acceptance Criteria**:
```
GIVEN application error occurs
WHEN error middleware processes exception
THEN log must:
  - Include timestamp, error type, stack trace
  - Include request path and parameters (safe)
  - Include trace ID for request correlation

GIVEN dashboard queries logs
WHEN filtering by error level
THEN must retrieve relevant logs efficiently
```

**Log Levels**:
- DEBUG: Detailed execution flow
- INFO: Normal operations
- WARNING: Unexpected but handled conditions
- ERROR: Failures requiring attention
- CRITICAL: System-level failures

**Metrics to Track**:
- Request count and latency
- Redirect performance
- Database operation times
- Error rates by type
- API endpoint usage

---

---

## Frontend Pages

Frontend pages should be implemented as Next.js app router pages with TypeScript and Tailwind CSS.

### Page: Analytics Dashboard

**Location**: `frontend/app/analytics/page.tsx`

**Functional Requirements**:
1. Display list of all shortened URLs with click counts
2. Show creation date and last access date
3. Implement pagination (10 URLs per page)
4. Sort by most popular (highest click count first)
5. Search/filter by short code or original URL
6. Display statistics (total URLs, total clicks, average clicks/URL)

**Features**:
- Table layout with columns: Short Code | Original URL | Clicks | Created | Last Access | Action(Delete)
- Top statistics cards showing totals
- Date range filter
- Search bar for short codes
- Delete button for each URL
- Responsive design (mobile-friendly)

**Dependencies**:
- React hooks for state management
- Tailwind CSS for styling

**Files Updated**:
- frontend/app/analytics/page.tsx (NEW)
- frontend/app/layout.tsx (add navigation link)

---

### Page: URL Management

**Location**: `frontend/app/manage/page.tsx`

**Functional Requirements**:
1. Display user's created shortened URLs
2. Allow viewing metadata
3. Allow deletion of shortened URLs
4. Show basic stats for each URL
5. Copy short URL to clipboard
6. Link to individual analytics

**Features**:
- List view of user's URLs
- Quick stats (clicks, created date)
- Delete confirmation dialog
- Copy and share buttons
- Link to analytics page

**Files Updated**:
- frontend/app/manage/page.tsx (NEW)
- frontend/app/layout.tsx (add navigation link)

---

### Page: URL Analytics Details

**Location**: `frontend/app/analytics/[code]/page.tsx`

**Functional Requirements**:
1. Show detailed stats for a single shortened URL
2. Display click timeline/history
3. Show referrer information
4. Display device/browser breakdown

**Features**:
- Header with short code and original URL
- Summary stats (total clicks, first click, last click)
- Chart showing clicks over time
- Referrer breakdown table
- Browser/device breakdown

**Files Updated**:
- frontend/app/analytics/[code]/page.tsx (NEW)

---

### Component: Navigation Bar

**Location**: `frontend/components/Navigation.tsx`

**Functional Requirements**:
1. Display main navigation links
2. Show current page indicator
3. Responsive mobile menu
4. Logo/branding

**Links**:
- Home (URL Shortener)
- Analytics
- Manage URLs

**Files Updated**:
- frontend/components/Navigation.tsx (NEW)
- frontend/app/layout.tsx (integrate)

---

### Component: Stats Card

**Location**: `frontend/components/StatsCard.tsx`

**Functional Requirements**:
1. Reusable card displaying a stat
2. Show title and value
3. Optional trend indicator

**Used In**:
- Analytics Dashboard
- Individual URL Analytics

**Files Updated**:
- frontend/components/StatsCard.tsx (NEW)

---

### Component: URL Table

**Location**: `frontend/components/URLTable.tsx`

**Functional Requirements**:
1. Display URLs in table format
2. Sortable columns
3. Filterable/searchable
4. Pagination controls
5. Action buttons (view, copy, delete)

**Used In**:
- Analytics Dashboard
- Manage URLs Page

**Files Updated**:
- frontend/components/URLTable.tsx (NEW)

---

## Testing Strategy

### Backend Testing (Python)

**Unit Tests** - `tests/unit/`:

#### 1. Code Generation Tests
```python
# tests/unit/test_shortener.py
import pytest
from backend.main import generate_short_code, code_exists, get_existing_code

class TestCodeGeneration:
    def test_generate_unique_codes(self):
        """Verify generate_short_code() produces unique codes"""
        codes = {generate_short_code() for _ in range(1000)}
        assert len(codes) == 1000, "Generated codes should be unique"
    
    def test_code_length(self):
        """Verify generated codes are correct length"""
        for _ in range(100):
            code = generate_short_code()
            assert len(code) == 6, "Code must be 6 characters"
    
    def test_code_charset(self):
        """Verify codes only contain alphanumeric characters"""
        import string
        valid_chars = set(string.ascii_letters + string.digits)
        for _ in range(100):
            code = generate_short_code()
            assert all(c in valid_chars for c in code), "Code contains invalid characters"
    
    def test_code_distribution(self):
        """Verify code generation has good distribution"""
        codes = [generate_short_code() for _ in range(1000)]
        unique_codes = set(codes)
        assert len(unique_codes) > 990, "Should have high uniqueness rate"
```

#### 2. Model Validation Tests
```python
# tests/unit/test_models.py
import pytest
from pydantic import ValidationError
from backend.main import URLRequest, URLResponse

class TestURLModels:
    def test_valid_url_request(self):
        """Verify URLRequest accepts valid URLs"""
        req = URLRequest(url="https://example.com")
        assert str(req.url) == "https://example.com/"
    
    def test_url_with_path_and_query(self):
        """Verify long URLs with paths are accepted"""
        url = "https://example.com/path/to/resource?key=value&foo=bar"
        req = URLRequest(url=url)
        assert "path" in str(req.url)
    
    def test_invalid_url_format(self):
        """Verify invalid URLs are rejected"""
        with pytest.raises(ValidationError):
            URLRequest(url="not-a-url")
    
    def test_invalid_url_missing_protocol(self):
        """Verify URLs without protocol are rejected"""
        with pytest.raises(ValidationError):
            URLRequest(url="example.com")
    
    def test_invalid_url_empty(self):
        """Verify empty URL is rejected"""
        with pytest.raises(ValidationError):
            URLRequest(url="")
    
    def test_url_response_model(self):
        """Verify URLResponse model structure"""
        resp = URLResponse(short_code="abc123", short_url="http://localhost:8000/abc123")
        assert resp.short_code == "abc123"
        assert resp.short_url == "http://localhost:8000/abc123"
```

#### 3. LRU Cache Tests
```python
# tests/unit/test_cache.py
import pytest
from backend.cache import URLCache

class TestLRUCache:
    @pytest.fixture
    def cache(self):
        """Create fresh cache instance for each test"""
        return URLCache(max_size=100)
    
    def test_cache_hit(self, cache):
        """Verify cache returns stored values"""
        cache.set("abc123", "https://example.com")
        result = cache.get("abc123")
        assert result == "https://example.com"
    
    def test_cache_miss(self, cache):
        """Verify cache returns None for missing keys"""
        result = cache.get("nonexistent")
        assert result is None
    
    def test_cache_eviction(self, cache):
        """Verify LRU eviction when cache fills"""
        for i in range(150):
            cache.set(f"code{i}", f"url{i}")
        
        # Cache size should not exceed max
        assert cache.size() <= 100
        
        # First entries should be evicted (LRU)
        assert cache.get("code0") is None
        assert cache.get("code149") is not None
    
    def test_cache_update_refreshes_order(self, cache):
        """Verify accessing entry updates its recency"""
        cache.set("code1", "url1")
        cache.set("code2", "url2")
        
        # Fill cache near limit
        for i in range(3, 100):
            cache.set(f"code{i}", f"url{i}")
        
        # Access code1 to refresh its position
        _ = cache.get("code1")
        
        # Add one more to trigger eviction
        cache.set("code100", "url100")
        
        # code1 should still exist (was recently accessed)
        assert cache.get("code1") == "url1"
    
    def test_cache_clear(self, cache):
        """Verify cache can be completely cleared"""
        cache.set("code1", "url1")
        cache.set("code2", "url2")
        assert cache.size() == 2
        
        cache.clear()
        assert cache.size() == 0
        assert cache.get("code1") is None
    
    def test_cache_stats(self, cache):
        """Verify cache statistics tracking"""
        cache.set("code1", "url1")
        
        # 2 hits
        cache.get("code1")
        cache.get("code1")
        
        # 1 miss
        cache.get("nonexistent")
        
        stats = cache.stats()
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 2/3
    
    def test_cache_thread_safety(self, cache):
        """Verify cache handles concurrent access"""
        import threading
        
        def writer(start, end):
            for i in range(start, end):
                cache.set(f"code{i}", f"url{i}")
        
        def reader():
            for _ in range(100):
                cache.get("code50")
        
        # Run multiple threads
        threads = [
            threading.Thread(target=writer, args=(0, 50)),
            threading.Thread(target=writer, args=(50, 100)),
            threading.Thread(target=reader),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Cache should be consistent
        assert cache.size() <= 100
```

#### 4. Database Function Tests
```python
# tests/unit/test_database.py
import pytest
import tempfile
from pathlib import Path
from backend.main import save_url, code_exists, get_original_url, get_existing_code, init_db

class TestDatabaseFunctions:
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set database path to temp location
            import backend.main as main_module
            original_path = main_module.DATABASE_FILE
            main_module.DATABASE_FILE = Path(tmpdir) / "test.db"
            init_db()
            yield main_module.DATABASE_FILE
            # Cleanup
            main_module.DATABASE_FILE = original_path
    
    def test_save_and_retrieve_url(self, temp_db):
        """Verify URL can be saved and retrieved"""
        save_url("abc123", "https://example.com")
        assert code_exists("abc123")
        assert get_original_url("abc123") == "https://example.com"
    
    def test_code_not_found(self, temp_db):
        """Verify missing codes return None"""
        assert not code_exists("missing")
        assert get_original_url("missing") is None
    
    def test_duplicate_url_detection(self, temp_db):
        """Verify duplicate URLs return existing code"""
        save_url("code1", "https://example.com/path")
        existing = get_existing_code("https://example.com/path")
        assert existing == "code1"
    
    def test_unique_constraint(self, temp_db):
        """Verify short codes must be unique"""
        save_url("duplicate", "https://example1.com")
        with pytest.raises(Exception):  # IntegrityError wrapped in HTTPException
            save_url("duplicate", "https://example2.com")
    
    def test_large_url_storage(self, temp_db):
        """Verify system handles very long URLs"""
        long_url = "https://example.com/" + "a" * 2000
        save_url("longcode", long_url)
        assert get_original_url("longcode") == long_url
```

**Integration Tests** - `tests/integration/`:
```python
# test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestShortenEndpoint:
    def test_shorten_valid_url(self):
        """Test full /shorten workflow with valid URL"""
        response = client.post(
            "/shorten",
            json={"url": "https://example.com/test"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "short_code" in data
        assert "short_url" in data
        assert len(data["short_code"]) == 6
        assert data["short_code"].isalnum()
    
    def test_shorten_duplicate_url(self):
        """Test that duplicate URLs return same short code"""
        url = "https://example.com/duplicate"
        
        resp1 = client.post("/shorten", json={"url": url})
        code1 = resp1.json()["short_code"]
        
        resp2 = client.post("/shorten", json={"url": url})
        code2 = resp2.json()["short_code"]
        
        assert code1 == code2, "Duplicate URLs should return same code"
    
    def test_shorten_invalid_url(self):
        """Test that invalid URLs are rejected"""
        response = client.post(
            "/shorten",
            json={"url": "not-a-url"}
        )
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_shorten_missing_field(self):
        """Test that missing URL field returns error"""
        response = client.post("/shorten", json={})
        assert response.status_code == 422  # Validation error
    
    def test_shorten_response_time(self):
        """Test that shorten completes within performance budget"""
        import time
        start = time.time()
        response = client.post(
            "/shorten",
            json={"url": "https://example.com/perf-test"}
        )
        elapsed = (time.time() - start) * 1000  # ms
        assert response.status_code == 200
        assert elapsed < 100, f"Request took {elapsed}ms, expected <100ms"

class TestRedirectEndpoint:
    def test_redirect_valid_code(self):
        """Test redirect to original URL"""
        # Create shortened URL
        create_response = client.post(
            "/shorten",
            json={"url": "https://example.com/redirect-test"}
        )
        code = create_response.json()["short_code"]
        
        # Follow redirect
        response = client.get(f"/{code}", follow_redirects=False)
        assert response.status_code == 307
        assert "location" in response.headers
        assert "https://example.com/redirect-test" in response.headers["location"]
    
    def test_redirect_invalid_code(self):
        """Test that invalid codes return 404"""
        response = client.get("/invalid404")
        assert response.status_code == 404
    
    def test_redirect_case_sensitive(self):
        """Test that codes are case-sensitive"""
        # Create with lowercase
        create_response = client.post(
            "/shorten",
            json={"url": "https://example.com/case-test"}
        )
        code = create_response.json()["short_code"]
        
        # Try uppercase
        response = client.get(f"/{code.upper()}")
        assert response.status_code == 404, "Codes should be case-sensitive"
    
    def test_redirect_response_time(self):
        """Test redirect performance (especially with cache)"""
        import time
        create_response = client.post(
            "/shorten",
            json={"url": "https://example.com/perf-redirect"}
        )
        code = create_response.json()["short_code"]
        
        # First redirect (cache miss)
        start = time.time()
        client.get(f"/{code}", follow_redirects=False)
        first_time = (time.time() - start) * 1000
        
        # Second redirect (cache hit)
        start = time.time()
        client.get(f"/{code}", follow_redirects=False)
        second_time = (time.time() - start) * 1000
        
        assert second_time < first_time, "Cached redirects should be faster"
        assert second_time < 10, "Cached redirect should be <10ms"

class TestHealthEndpoint:
    def test_health_check(self):
        """Test health endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_health_response_time(self):
        """Test health check completes quickly"""
        import time
        start = time.time()
        response = client.get("/health")
        elapsed = (time.time() - start) * 1000
        assert response.status_code == 200
        assert elapsed < 50, f"Health check took {elapsed}ms, expected <50ms"

class TestCacheEndpoint:
    def test_cache_stats(self):
        """Test cache statistics endpoint"""
        # Make some requests
        response = client.get("/api/cache-stats")
        assert response.status_code == 200
        data = response.json()
        assert "hits" in data
        assert "misses" in data
        assert "hit_rate" in data
        assert "size" in data
    
    def test_cache_hit_rate_improves(self):
        """Test that hit rate improves with repeated accesses"""
        # Create a URL
        create_response = client.post(
            "/shorten",
            json={"url": "https://example.com/cache-test"}
        )
        code = create_response.json()["short_code"]
        
        # Clear cache stats
        client.post("/api/cache-clear")
        stats_before = client.get("/api/cache-stats").json()
        
        # Access same code multiple times
        for _ in range(10):
            client.get(f"/{code}", follow_redirects=False)
        
        stats_after = client.get("/api/cache-stats").json()
        assert stats_after["hits"] > stats_before["hits"]
        assert stats_after["hit_rate"] > 0
```

**Test Coverage Target**: >85% code coverage

**Test Files to Create**:
- tests/conftest.py (pytest fixtures)
- tests/unit/test_shortener.py
- tests/unit/test_models.py
- tests/unit/test_cache.py
- tests/unit/test_database.py
- tests/integration/test_api.py
- tests/integration/test_database.py
- tests/performance/test_cache_performance.py

**Cache Testing Strategy**:
```python
# tests/performance/test_cache_performance.py
import pytest
import time
from backend.main import app, cache
from fastapi.testclient import TestClient

client = TestClient(app)

class TestCachePerformance:
    def test_cache_miss_penalty(self):
        \"\"\"Measure latency difference between cache hit and miss\"\"\"
        code = \"testcode123\"\n        url = \"https://performance-test.example.com\"\n        
        # First access (cache miss)\n        cache.clear()\n        start = time.perf_counter()\n        result = cache.get(code)\n        miss_time = (time.perf_counter() - start) * 1000\n        \n        # Populate cache\n        cache.set(code, url)\n        \n        # Second access (cache hit)\n        start = time.perf_counter()\n        result = cache.get(code)\n        hit_time = (time.perf_counter() - start) * 1000\n        \n        # Hit should be significantly faster\n        assert hit_time < miss_time\n        assert hit_time < 5, f\"Cache hit should be <5ms, got {hit_time}ms\"\n        print(f\"Cache hit speedup: {miss_time / hit_time:.1f}x\")\n    \n    def test_redirect_latency_with_cache(self):\n        \"\"\"Test end-to-end redirect latency improvement with cache\"\"\"n        # Warm up cache with a URL\n        create_resp = client.post(\"/shorten\", json={\"url\": \"https://example.com\"})\n        code = create_resp.json()[\"short_code\"]\n        \n        # First redirect (fresh from DB)\n        start = time.perf_counter()\n        client.get(f\"/{code}\", follow_redirects=False)\n        first_ms = (time.perf_counter() - start) * 1000\n        \n        # Subsequent redirects (from cache)\n        times = []\n        for _ in range(100):\n            start = time.perf_counter()\n            client.get(f\"/{code}\", follow_redirects=False)\n            times.append((time.perf_counter() - start) * 1000)\n        \n        avg_cached = sum(times) / len(times)\n        assert avg_cached < 20, f\"Average cached redirect should be <20ms, got {avg_cached}ms\"\n        assert all(t < 50 for t in times), \"All cached redirects should be <50ms\"\n    \n    def test_cache_under_load(self):\n        \"\"\"Test cache consistency under concurrent requests\"\"\"n        import concurrent.futures\n        \n        # Create multiple URLs\n        codes = []\n        for i in range(10):\n            resp = client.post(\"/shorten\", json={\"url\": f\"https://example.com/load-{i}\"})\n            codes.append(resp.json()[\"short_code\"])\n        \n        # Simulate concurrent access\n        def access_random_code():\n            import random\n            code = random.choice(codes)\n            return client.get(f\"/{code}\", follow_redirects=False).status_code\n        \n        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:\n            results = list(executor.map(access_random_code, range(1000)))\n        \n        # All requests should succeed\n        assert all(r == 307 for r in results), \"All redirects should succeed\"\n        \n        # Cache should have expected size\n        stats = cache.stats()\n        assert stats['hits'] > 900, f\"Expected >900 cache hits, got {stats['hits']}\"\n```

---

### Frontend Testing (TypeScript/React)

**Component Tests** - `__tests__/components/`:
```typescript
// URLShortener.test.tsx
describe('URLShortener Component', () => {
  it('displays input field and submit button', () => {
    render(<URLShortener />)
    expect(screen.getByPlaceholderText(/enter a url/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /shorten/i })).toBeInTheDocument()
  })

  it('validates URL before submission', () => {
    render(<URLShortener />)
    const input = screen.getByPlaceholderText(/enter a url/i)
    const button = screen.getByRole('button', { name: /shorten/i })
    
    fireEvent.change(input, { target: { value: 'invalid' } })
    fireEvent.click(button)
    
    expect(screen.getByText(/valid url/i)).toBeInTheDocument()
  })

  it('handles API response and displays shortened URL', async () => {
    const mockFetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({
        short_code: 'abc123',
        short_url: 'http://short.url/abc123'
      })
    })
    global.fetch = mockFetch

    render(<URLShortener />)
    // ... user interaction
    await waitFor(() => {
      expect(screen.getByText('http://short.url/abc123')).toBeInTheDocument()
    })
  })
})
```

**E2E Tests** - `e2e/`:
```typescript
// shortener.e2e.ts (Playwright/Cypress)
test('Complete URL shortening workflow', async ({ page }) => {
  await page.goto('http://localhost:3000')
  
  await page.fill('input[type="text"]', 'https://example.com/very/long/path')
  await page.click('button:has-text("Shorten")')
  
  await page.waitForSelector('text=/short\.url/')
  const shortUrl = await page.textContent('.result-url')
  expect(shortUrl).toMatch(/^http.*\d+/)
  
  const copyButton = await page.$('button:has-text("Copy")')
  await copyButton.click()
  const copied = await page.textContent('.copy-status')
  expect(copied).toContain('Copied')
})
```

**Test Coverage Target**: >75% component coverage

---

### Performance Testing

**Load Testing** - Apache JMeter / Locust:
```
Scenarios:
- 1000 concurrent users shortening URLs
- 5000 concurrent redirect requests
- Mixed read/write ratio (80% read, 20% write)

Success Criteria:
- 95th percentile latency <200ms
- 99th percentile latency <500ms
- Error rate <1%
```

---

### Security Testing

**Static Analysis**:
- backend: `pylint`, `black`, `mypy` type checking
- frontend: `eslint`, TypeScript strict mode

**Dependency Scanning**:
- `pip audit` for Python vulnerabilities
- `npm audit` for JavaScript vulnerabilities

**Input Testing**:
- SQL injection attempts
- XSS payloads
- Open redirect attempts
- File path traversal attempts

---

## Next Steps

### To Implement LRU Caching (Phase 1.3):
1. Create `backend/cache.py` with URLCache class
2. Integrate cache into `get_original_url()` function
3. Add cache invalidation to `POST /shorten` endpoint
4. Add `GET /api/cache-stats` and `POST /api/cache-clear` endpoints
5. Write comprehensive cache tests
6. Update `requirements.txt` with cachetools dependency
7. Run performance tests to validate improvements

### To Implement Phase 2 (Analytics):
1. Extend database schema with clicks table
2. Implement click tracking on redirects
3. Build analytics API endpoints
4. Create frontend dashboard

### Project Resources
- **Backend Code**: [backend/main.py](backend/main.py)
- **Frontend Code**: [frontend/components/URLShortener.tsx](frontend/components/URLShortener.tsx)
- **Docker Setup**: [docker-compose.yml](docker-compose.yml)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)

**Pre-Deployment Verification**:
1. All unit tests pass (>85% coverage)
2. Integration tests pass
3. Performance tests meet targets
4. Security scans clean
5. Linting passes
6. Type checking passes

---

## Agent Implementation Guidelines

### LRU Cache Implementation Pattern

**Basic Cache Module** (`backend/cache.py`):
```python
from cachetools import LRUCache
from threading import Lock
from datetime import datetime
from typing import Optional, Dict

class URLCache:
    """Thread-safe LRU cache for URL lookups."""
    
    def __init__(self, max_size: int = 1000):
        self.cache = LRUCache(maxsize=max_size)
        self.lock = Lock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache, recording hit/miss."""
        with self.lock:
            if key in self.cache:
                self.hits += 1
                return self.cache[key]
            else:
                self.misses += 1
                return None
    
    def set(self, key: str, value: str) -> None:
        """Set value in cache, evicting LRU entry if necessary."""
        with self.lock:
            self.cache[key] = value
    
    def invalidate(self, key: str) -> None:
        """Remove specific key from cache."""
        with self.lock:
            self.cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    def stats(self) -> Dict:
        """Get cache statistics."""
        with self.lock:
            total = self.hits + self.misses
            hit_rate = self.hits / total if total > 0 else 0
            return {
                'size': len(self.cache),
                'max_size': self.cache.maxsize,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'timestamp': datetime.now().isoformat()
            }
    
    def size(self) -> int:
        """Get current cache size."""
        with self.lock:
            return len(self.cache)
```

**Integration in main.py**:
```python
import os
from backend.cache import URLCache

# Initialize cache with configurable size
CACHE_SIZE = int(os.getenv("CACHE_SIZE", "1000"))
cache = URLCache(max_size=CACHE_SIZE)

def get_original_url(code: str) -> Optional[str]:
    """Retrieve original URL with caching."""
    # Check cache first
    cached_url = cache.get(code)
    if cached_url is not None:
        return cached_url
    
    # Fall back to database
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT original_url FROM urls WHERE short_code = ?", (code,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        url = result[0]
        cache.set(code, url)  # Cache the result
        return url
    
    # Cache None values to avoid repeated DB lookups
    cache.set(code, None)
    return None

@app.post("/shorten")
async def shorten_url(request: URLRequest) -> URLResponse:
    """Shorten URL and invalidate cache if needed."""
    url_str = str(request.url)
    
    # Check for duplicates
    existing_code = get_existing_code(url_str)
    if existing_code:
        return URLResponse(
            short_code=existing_code,
            short_url=f"{BASE_URL}/{existing_code}"
        )
    
    # Generate new code
    short_code = generate_short_code()
    save_url(short_code, url_str)
    
    # Invalidate any related cache entries (optional: only if needed)
    cache.invalidate(short_code)
    
    return URLResponse(
        short_code=short_code,
        short_url=f"{BASE_URL}/{short_code}"
    )

@app.get("/api/cache-stats")
async def cache_stats():
    """Return cache statistics."""
    return cache.stats()

@app.post("/api/cache-clear")
async def cache_clear():
    """Clear cache (useful for testing)."""
    cache.clear()
    return {"message": "Cache cleared"}
```

### Best Practices for AI Code Generation

**1. Implementation Sequence**:
- Start with database models and migrations
- Implement core endpoints before features
- Add error handling before optimization
- Write tests after feature completion

**2. Code Organization**:
```
backend/
  ├── main.py (entry, middleware)
  ├── models.py (Pydantic models)
  ├── database/
  │   ├── __init__.py
  │   ├── connection.py
  │   └── migrations.py
  ├── services/ (business logic)
  ├── routes/ (endpoints)
  ├── utils/ (helpers)
  └── tests/
```

**3. Error Handling Pattern**:
```python
# Consistent error responses
from fastapi import HTTPException, status

try:
    # operation
except ValueError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Validation failed: {str(e)}"
    )
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error"
    )
```

**4. Type Hints**:
- Always use full type hints for function signatures
- Use `Optional[T]` instead of None defaults
- Define request/response models as Pydantic classes

**5. Testing and Validation**:
- Write test for each acceptance criterion
- Include performance benchmarks
- Verify cache behavior under load
- Test cache invalidation paths

**6. Cache-Specific Patterns**:
- Always use thread-safe cache implementations (Lock, RLock)
- Cache both positive results (found URLs) and negative results (not found) to avoid repeated misses
- Implement cache invalidation on data mutations (POST /shorten)
- Provide cache statistics endpoints for monitoring
- Design cache size as configurable via environment variable
- Use performance tests to measure cache hit rate improvements

---

## Acceptance Testing Checklist

### For Each New Feature Implementation

**Functionality Checks**:
- [ ] All acceptance criteria met from feature spec
- [ ] Happy path scenarios pass
- [ ] Error scenarios handled correctly
- [ ] Edge cases tested

**Performance Checks**:
- [ ] Latency targets met
- [ ] Memory usage acceptable
- [ ] Database queries optimized
- [ ] No N+1 query problems

**Quality Checks**:
- [ ] Unit tests written (>85% coverage for feature)
- [ ] Integration tests pass
- [ ] Code follows existing patterns
- [ ] Type hints complete (Python/TypeScript)
- [ ] Error messages user-friendly

**Documentation Checks**:
- [ ] Acceptance criteria validated
- [ ] Configuration documented
- [ ] Breaking changes documented
- [ ] Implementation notes clear

---

## Success Criteria

### For Phase 1.3: LRU Caching (Next Priority)
✓ Cache implementation passes all unit tests  
✓ Cache hit rate >60% under typical usage  
✓ Redirect latency on cache hits <10ms  
✓ No data loss on cache eviction  
✓ Thread-safe under concurrent requests  
✓ Configuration manageable via environment variable  

### For Phase 2-4: Feature Completion
✓ Each phase delivered with all acceptance criteria met  
✓ Implementation can be done by AI agent from spec alone  
✓ Code quality maintained (>80% test coverage)  
✓ Performance targets consistently met  
✓ No production incidents  
✓ Documentation updated for each feature  

---

## How to Use This Spec

1. Pick any feature from [Feature Specifications](#feature-specifications) or [Frontend Pages](#frontend-pages)
2. Read the entire specification for that feature
3. Implement all acceptance criteria
4. Write tests to verify acceptance criteria
5. Verify works end-to-end
6. Submit for review

**Features are independent** - implement in any order. Multiple agents can work in parallel.

### Priority Recommendations:
- **LRU Cache** (simplest, high impact on performance)
- **Click Tracking & Analytics API** (enables analytics dashboard)
- **Analytics Dashboard & Management Pages** (depends on analytics API)
- **Custom Short Codes, Expiration, QR Codes** (independent features)
- **Rate Limiting, Security, Database Optimization** (advanced features)

### Reference Files:
- **Backend Entry**: [backend/main.py](backend/main.py) - 241 lines, fully implemented
- **Frontend Component**: [frontend/components/URLShortener.tsx](frontend/components/URLShortener.tsx) - 181 lines
- **Database Setup**: [backend/main.py](backend/main.py#L1-L50) - SQLite initialization
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md) - Fly.io configuration

---

## Implementation Guidelines

**Before Starting**:
- Read the complete feature specification end-to-end
- Understand all acceptance criteria
- Review test cases provided in the spec
- Check implementation notes for patterns/gotchas

**During Implementation**:
- Code patterns: Pydantic models, type hints, async/await, try/except error handling
- Use environment variables for configuration (DATABASE_PATH, BASE_URL, CACHE_SIZE, etc.)
- Update `backend/requirements.txt` or `frontend/package.json` if adding dependencies
- All new code needs comprehensive tests (unit, integration, and edge cases)

**After Implementation**:
- Run all acceptance criteria manually or via tests
- Verify no regressions in existing functionality
- Test with concurrent requests/multiple users
- Update documentation if behavior changes
- Check codebase style consistency with existing patterns

**When Stuck**:
- Acceptance criteria provide the "what", implementation notes provide the "how"
- Review similar features already implemented for patterns
- Error handling should use meaningful messages for debugging
- Ask clarifying questions if spec is ambiguous

---

**End of Feature Specification**
