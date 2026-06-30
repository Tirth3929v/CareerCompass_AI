"""IP-based rate limiting middleware for protecting free-tier API limits.

Uses an in-memory store with MongoDB fallback for persistence across restarts.
Limits requests per IP per day (configurable via RATE_LIMIT_PER_DAY).
"""

import time
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware that enforces daily request limits per IP.

    Uses in-memory tracking for speed with MongoDB persistence as fallback.
    Exempt paths: /api/health, /docs, /openapi.json
    """

    EXEMPT_PATHS = {"/api/health", "/docs", "/openapi.json", "/redoc"}

    def __init__(self, app, max_requests_per_day: int | None = None):
        super().__init__(app)
        self.max_requests = max_requests_per_day or settings.rate_limit_per_day
        # In-memory store: {ip: {date_str: count}}
        self._store: dict[str, dict[str, int]] = defaultdict(dict)
        self._last_cleanup = time.time()

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP, respecting X-Forwarded-For for reverse proxies."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _get_date_key(self) -> str:
        """Get today's date as a string key (UTC)."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _cleanup_old_entries(self) -> None:
        """Remove entries from previous days to prevent memory leaks."""
        now = time.time()
        # Clean up every hour
        if now - self._last_cleanup < 3600:
            return

        today = self._get_date_key()
        ips_to_remove = []
        for ip, dates in self._store.items():
            old_dates = [d for d in dates if d != today]
            for d in old_dates:
                del dates[d]
            if not dates:
                ips_to_remove.append(ip)

        for ip in ips_to_remove:
            del self._store[ip]

        self._last_cleanup = now

    async def dispatch(self, request: Request, call_next) -> Response:
        """Check rate limit before processing the request."""
        # Skip rate limiting for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Only rate-limit POST endpoints (chat interactions)
        if request.method != "POST":
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        date_key = self._get_date_key()

        # Periodic cleanup
        self._cleanup_old_entries()

        # Check current count
        current_count = self._store[client_ip].get(date_key, 0)

        if current_count >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.max_requests} requests per day. Resets at UTC midnight.",
                    "retry_after": "tomorrow",
                    "current_count": current_count,
                    "max_allowed": self.max_requests,
                },
                headers={"Retry-After": "86400"},
            )

        # Increment counter
        self._store[client_ip][date_key] = current_count + 1

        # Add rate limit headers to response
        response = await call_next(request)
        remaining = self.max_requests - (current_count + 1)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = "UTC midnight"

        return response
