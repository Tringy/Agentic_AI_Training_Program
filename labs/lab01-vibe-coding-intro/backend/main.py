"""URL Shortener Backend - FastAPI Implementation"""

import logging
import os
import random
import sqlite3
import string
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from time import time as current_time
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, HttpUrl, field_validator

try:
    from cache import URLCache
except ImportError:
    from backend.cache import URLCache

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuration from environment variables
DATABASE_PATH = os.getenv("DATABASE_PATH", "/data")
DATABASE_FILE = Path(DATABASE_PATH) / "urls.db"
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
SHORT_CODE_LENGTH = 6
CACHE_SIZE = int(os.getenv("CACHE_SIZE", "1000"))

# Initialize cache
cache = URLCache(max_size=CACHE_SIZE)

# Ensure database directory exists
DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

# Rate limiting tracker (IP -> list of request timestamps)
rate_limit_tracker: dict = defaultdict(list)
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds


def check_rate_limit(ip: str) -> tuple[bool, Optional[dict]]:
    """Check if client has exceeded rate limit.

    Returns:
        (is_allowed, retry_after_info_dict_or_none)
    """
    now = current_time()
    # Remove old requests outside the window
    rate_limit_tracker[ip] = [req_time for req_time in rate_limit_tracker[ip] if now - req_time < RATE_LIMIT_WINDOW]

    if len(rate_limit_tracker[ip]) >= RATE_LIMIT_REQUESTS:
        # Rate limit exceeded
        oldest_request = rate_limit_tracker[ip][0]
        retry_after = int(RATE_LIMIT_WINDOW - (now - oldest_request)) + 1
        return False, {"retry_after": retry_after, "limit": RATE_LIMIT_REQUESTS, "window": RATE_LIMIT_WINDOW}

    # Record this request
    rate_limit_tracker[ip].append(now)
    return True, None


# Pydantic Models
class URLRequest(BaseModel):
    """Request model for URL shortening"""

    url: HttpUrl
    custom_code: Optional[str] = None
    expires_at: Optional[str] = None

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: HttpUrl) -> HttpUrl:
        """Validate URL is not empty"""
        if not str(v):
            raise ValueError("URL cannot be empty")
        return v

    @field_validator("custom_code")
    @classmethod
    def validate_custom_code(cls, v: Optional[str]) -> Optional[str]:
        """Validate custom code format if provided"""
        if v:
            if len(v) < 3 or len(v) > 20:
                raise ValueError("Custom code must be 3-20 characters long")
            if not v.isalnum():
                raise ValueError("Custom code must be alphanumeric")
            # Reserved words
            reserved = {"api", "health", "shorten", "info", "analytics", "cache", "qrcode"}
            if v.lower() in reserved:
                raise ValueError(f"Custom code '{v}' is reserved")
        return v


class URLResponse(BaseModel):
    """Response model for shortened URL"""

    short_code: str
    short_url: str


class URLInfo(BaseModel):
    """Model for URL information"""

    short_code: str
    original_url: str
    short_url: str


class URLAnalytics(BaseModel):
    """Model for URL analytics"""

    short_code: str
    original_url: str
    short_url: str
    click_count: int
    created_at: str
    last_accessed_at: Optional[str] = None
    expires_at: Optional[str] = None
    is_custom: bool = False


class AnalyticsResponse(BaseModel):
    """Response model for analytics endpoints"""

    short_code: str
    click_count: int
    last_click: Optional[str] = None


class AnalyticsListResponse(BaseModel):
    """Response model for analytics list"""

    total_urls: int
    total_clicks: int
    average_clicks: float
    urls: list[URLAnalytics]
    page: int
    total_pages: int


# Database Functions
def init_db() -> None:
    """Initialize SQLite database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Create urls table with click tracking
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            original_url TEXT NOT NULL,
            click_count INTEGER DEFAULT 0,
            is_custom BOOLEAN DEFAULT 0,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed_at TIMESTAMP
        )
        """
    )

    # Create clicks table for tracking individual clicks
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT NOT NULL,
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_agent TEXT,
            ip_address TEXT,
            referrer TEXT,
            FOREIGN KEY(short_code) REFERENCES urls(short_code)
        )
        """
    )

    # Create indices for performance
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_urls_short_code ON urls(short_code)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_urls_created_at ON urls(created_at)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_clicks_short_code ON clicks(short_code)
        """
    )

    conn.commit()
    conn.close()


def generate_short_code() -> str:
    """Generate a unique 6-character alphanumeric short code"""
    characters = string.ascii_letters + string.digits
    while True:
        code = "".join(random.choices(characters, k=SHORT_CODE_LENGTH))
        # Check if code already exists
        if not code_exists(code):
            return code


def code_exists(code: str) -> bool:
    """Check if a short code already exists in database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM urls WHERE short_code = ?", (code,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def get_original_url(code: str) -> Optional[str]:
    """Retrieve original URL for a given short code"""
    # Check cache first
    cached_url = cache.get(code)
    if cached_url is not None:
        # Return None if explicitly cached as not found
        return cached_url if cached_url != "__NOT_FOUND__" else None

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

    # Cache negative result to avoid repeated DB lookups
    cache.set(code, "__NOT_FOUND__")
    return None


def get_existing_code(url: str) -> Optional[str]:
    """Check if URL already exists and return its short code"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT short_code FROM urls WHERE original_url = ?", (url,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def record_click(short_code: str, user_agent: Optional[str] = None, ip_address: Optional[str] = None, referrer: Optional[str] = None) -> None:
    """Record a click for a shortened URL."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        # Insert click record
        cursor.execute(
            """
            INSERT INTO clicks (short_code, user_agent, ip_address, referrer)
            VALUES (?, ?, ?, ?)
            """,
            (short_code, user_agent, ip_address, referrer),
        )

        # Update click count and last accessed time
        cursor.execute(
            """
            UPDATE urls 
            SET click_count = click_count + 1, last_accessed_at = CURRENT_TIMESTAMP
            WHERE short_code = ?
            """,
            (short_code,),
        )
        conn.commit()
    finally:
        conn.close()


def is_expired(expires_at: Optional[str]) -> bool:
    """Check if a URL has expired."""
    if not expires_at:
        return False
    from datetime import datetime

    exp_time = datetime.fromisoformat(expires_at)
    return datetime.now() >= exp_time


def get_analytics(short_code: str) -> Optional[dict]:
    """Get analytics for a specific shortened URL."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Get URL info and click count
    cursor.execute(
        """
        SELECT short_code, click_count, last_accessed_at, original_url
        FROM urls
        WHERE short_code = ?
        """,
        (short_code,),
    )
    result = cursor.fetchone()

    if not result:
        conn.close()
        return None

    short_code, click_count, last_accessed_at, _ = result

    conn.close()
    return {"short_code": short_code, "click_count": click_count, "last_click": last_accessed_at}


def get_all_analytics(page: int = 1, limit: int = 10) -> dict:
    """Get analytics for all shortened URLs with pagination."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Get total count
    cursor.execute("SELECT COUNT(*) FROM urls")
    total_urls = cursor.fetchone()[0]

    # Get total clicks
    cursor.execute("SELECT SUM(click_count) FROM urls")
    total_clicks = cursor.fetchone()[0] or 0

    # Get paginated results
    offset = (page - 1) * limit
    cursor.execute(
        """
        SELECT short_code, original_url, click_count, created_at, last_accessed_at, expires_at, is_custom
        FROM urls
        ORDER BY click_count DESC, created_at DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    )
    rows = cursor.fetchall()
    conn.close()

    urls = [
        URLAnalytics(
            short_code=row[0],
            original_url=row[1],
            short_url=f"{BASE_URL}/{row[0]}",
            click_count=row[2],
            created_at=row[3],
            last_accessed_at=row[4],
            expires_at=row[5],
            is_custom=bool(row[6]),
        )
        for row in rows
    ]

    total_pages = (total_urls + limit - 1) // limit
    average_clicks = total_clicks / total_urls if total_urls > 0 else 0

    return {
        "total_urls": total_urls,
        "total_clicks": total_clicks,
        "average_clicks": average_clicks,
        "urls": urls,
        "page": page,
        "total_pages": total_pages,
    }


def save_url(short_code: str, original_url: str) -> None:
    """Save URL mapping to database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
            (short_code, original_url),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save URL mapping")
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: Cleanup if needed


# FastAPI Application
app = FastAPI(title="URL Shortener API", description="API for shortening long URLs", version="1.0.0", lifespan=lifespan)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate Limiting Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    client_ip = request.client.host if request.client else "unknown"

    # Skip rate limiting for health checks
    if request.url.path == "/health":
        return await call_next(request)

    allowed, limit_info = check_rate_limit(client_ip)
    if not allowed:
        logger.warning(f"Rate limit exceeded for IP {client_ip}")
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded", "retry_after": limit_info["retry_after"]})

    return await call_next(request)


# Routes
@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post(
    "/shorten",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["URL Shortening"],
    summary="Shorten a URL",
    description="Takes a long URL and returns a shortened version with a 6-character code",
)
async def shorten_url(request: URLRequest) -> URLResponse:
    """
    Shorten a URL.

    - **url**: The long URL to shorten (must be a valid HTTP/HTTPS URL)
    - **custom_code**: (Optional) Custom 3-20 character alphanumeric code
    - **expires_at**: (Optional) ISO format datetime for expiration

    Returns:
    - **short_code**: The 6-character unique identifier or custom code
    - **short_url**: The full shortened URL
    """
    original_url = str(request.url)

    # Check if URL already exists (with same custom/expiration settings)
    existing_code = get_existing_code(original_url)
    if existing_code:
        return URLResponse(short_code=existing_code, short_url=f"{BASE_URL}/{existing_code}")

    # Determine short code
    short_code = request.custom_code
    is_custom = False

    if short_code:
        is_custom = True
        # Check if custom code is available
        if code_exists(short_code):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Custom code '{short_code}' is already taken")
    else:
        # Generate new short code
        short_code = generate_short_code()

    # Save URL with custom flag and expiration
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO urls (short_code, original_url, is_custom, expires_at)
            VALUES (?, ?, ?, ?)
            """,
            (short_code, original_url, is_custom, request.expires_at),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save URL mapping")
    finally:
        conn.close()

    # Invalidate cache entry for this code (shouldn't exist but be safe)
    cache.invalidate(short_code)

    return URLResponse(short_code=short_code, short_url=f"{BASE_URL}/{short_code}")


@app.get(
    "/{short_code}",
    tags=["URL Redirection"],
    summary="Redirect to original URL",
    description="Redirects to the original URL associated with the short code",
)
async def redirect_url(short_code: str, request: Request) -> RedirectResponse:
    """
    Redirect to the original URL.

    - **short_code**: The 6-character short code

    Returns a 307 redirect to the original URL.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT original_url, expires_at FROM urls WHERE short_code = ?", (short_code,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Short code '{short_code}' not found")

    original_url, expires_at = result

    # Check if expires
    if is_expired(expires_at):
        raise HTTPException(status_code=410, detail="This short link has expired")

    # Record click
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    referrer = request.headers.get("referer")

    try:
        record_click(short_code, user_agent=user_agent, ip_address=ip_address, referrer=referrer)
    except Exception as e:
        # Don't fail redirect if click tracking fails
        logging.warning(f"Failed to record click for {short_code}: {e}")

    return RedirectResponse(url=original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get(
    "/info/{short_code}",
    response_model=URLInfo,
    tags=["URL Information"],
    summary="Get URL information",
    description="Retrieve information about a shortened URL",
)
async def get_url_info(short_code: str) -> URLInfo:
    """
    Get information about a shortened URL.

    - **short_code**: The 6-character short code

    Returns the original URL and short URL information.
    """
    original_url = get_original_url(short_code)

    if not original_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Short code '{short_code}' not found")

    return URLInfo(short_code=short_code, original_url=original_url, short_url=f"{BASE_URL}/{short_code}")


@app.get(
    "/api/cache-stats",
    tags=["Cache"],
    summary="Get cache statistics",
    description="Returns cache hit/miss statistics and size information",
)
async def cache_stats() -> dict:
    """Get cache statistics including hit rate, size, and performance metrics."""
    return cache.stats()


@app.post(
    "/api/cache-clear",
    tags=["Cache"],
    summary="Clear cache",
    description="Clears all cache entries (useful for testing)",
)
async def cache_clear() -> dict:
    """Clear all cache entries and reset statistics."""
    cache.clear()
    return {"message": "Cache cleared", "timestamp": __import__("datetime").datetime.now().isoformat()}


@app.get(
    "/api/analytics",
    response_model=AnalyticsListResponse,
    tags=["Analytics"],
    summary="Get all analytics",
    description="Retrieve analytics for all shortened URLs with pagination",
)
async def get_all_analytics_endpoint(page: int = 1, limit: int = 10) -> AnalyticsListResponse:
    """Get analytics for all shortened URLs.

    - **page**: Page number (default: 1)
    - **limit**: Results per page (default: 10)
    """
    result = get_all_analytics(page, limit)
    return AnalyticsListResponse(**result)


@app.get(
    "/api/analytics/{short_code}",
    response_model=AnalyticsResponse,
    tags=["Analytics"],
    summary="Get URL analytics",
    description="Retrieve analytics for a specific shortened URL",
)
async def get_analytics_endpoint(short_code: str) -> AnalyticsResponse:
    """Get analytics for a specific shortened URL.

    - **short_code**: The 6-character short code
    """
    analytics = get_analytics(short_code)
    if not analytics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Short code '{short_code}' not found")
    return AnalyticsResponse(**analytics)


@app.get(
    "/api/qrcode/{short_code}",
    tags=["QR Code"],
    summary="Get QR code for URL",
    description="Returns a QR code as SVG for the shortened URL",
)
async def get_qrcode(short_code: str):
    """Get QR code for a shortened URL.

    Returns the QR code as an SVG image.
    - **short_code**: The 6-character short code
    """
    if not code_exists(short_code):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Short code '{short_code}' not found")

    try:
        from io import BytesIO

        import qrcode
        from fastapi.responses import StreamingResponse

        short_url = f"{BASE_URL}/{short_code}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(short_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        return StreamingResponse(img_bytes, media_type="image/png")
    except Exception as e:
        logging.error(f"Failed to generate QR code: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate QR code")


@app.get(
    "/api/rate-limit-stats",
    tags=["Rate Limiting"],
    summary="Get rate limit statistics",
    description="Returns rate limiting statistics (admin only)",
)
async def get_rate_limit_stats() -> dict:
    """Get rate limiting statistics."""
    return {
        "rate_limit_requests": RATE_LIMIT_REQUESTS,
        "rate_limit_window_seconds": RATE_LIMIT_WINDOW,
        "active_ips": len(rate_limit_tracker),
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }


@app.delete(
    "/{short_code}",
    tags=["URL Management"],
    summary="Delete a shortened URL",
    description="Delete a shortened URL and all its analytics data",
)
async def delete_url(short_code: str) -> dict:
    """Delete a shortened URL.

    - **short_code**: The 6-character short code
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Check if URL exists
    cursor.execute("SELECT id FROM urls WHERE short_code = ?", (short_code,))
    url_record = cursor.fetchone()

    if not url_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Short code '{short_code}' not found")

    try:
        # Delete clicks
        cursor.execute("DELETE FROM clicks WHERE short_code = ?", (short_code,))
        # Delete URL
        cursor.execute("DELETE FROM urls WHERE short_code = ?", (short_code,))
        conn.commit()

        # Invalidate cache
        cache.invalidate(short_code)

        logger.info(f"Deleted URL with short code: {short_code}")
        return {"message": f"Successfully deleted short code '{short_code}'"}
    except Exception as e:
        logger.error(f"Failed to delete URL: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete URL")
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
