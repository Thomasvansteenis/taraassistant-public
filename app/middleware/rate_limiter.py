"""Rate limiting middleware using token bucket algorithm."""
import time
from dataclasses import dataclass
from typing import Dict

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


@dataclass
class RateLimitBucket:
    """Token bucket for rate limiting."""
    tokens: float
    last_update: float
    max_tokens: int
    refill_rate: float  # tokens per second

    def consume(self) -> bool:
        """Try to consume a token.

        Returns:
            True if allowed, False if rate limited.
        """
        now = time.time()
        elapsed = now - self.last_update

        # Refill tokens based on elapsed time
        self.tokens = min(
            self.max_tokens,
            self.tokens + elapsed * self.refill_rate
        )
        self.last_update = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    def time_until_available(self) -> float:
        """Calculate seconds until next token is available."""
        if self.tokens >= 1:
            return 0
        return (1 - self.tokens) / self.refill_rate


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with per-session token buckets."""

    def __init__(self, app, requests_per_minute: int = 20):
        """Initialize rate limiter.

        Args:
            app: FastAPI application.
            requests_per_minute: Maximum requests allowed per minute.
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.buckets: Dict[str, RateLimitBucket] = {}
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()

    def _get_session_id(self, request: Request) -> str:
        """Extract session identifier from request."""
        # Try session cookie first, then fall back to IP
        session_id = request.cookies.get("session_id")
        if not session_id:
            session_id = request.client.host if request.client else "unknown"
        return session_id

    def _get_or_create_bucket(self, session_id: str) -> RateLimitBucket:
        """Get or create rate limit bucket for session."""
        if session_id not in self.buckets:
            self.buckets[session_id] = RateLimitBucket(
                tokens=float(self.requests_per_minute),
                last_update=time.time(),
                max_tokens=self.requests_per_minute,
                refill_rate=self.requests_per_minute / 60.0
            )
        return self.buckets[session_id]

    def _cleanup_old_buckets(self):
        """Remove stale buckets to prevent memory leaks."""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return

        # Remove buckets not accessed in last 10 minutes
        stale_threshold = now - 600
        self.buckets = {
            k: v for k, v in self.buckets.items()
            if v.last_update > stale_threshold
        }
        self._last_cleanup = now

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Only rate limit the chat API endpoint
        if request.url.path == "/api/chat" and request.method == "POST":
            session_id = self._get_session_id(request)
            bucket = self._get_or_create_bucket(session_id)

            if not bucket.consume():
                retry_after = bucket.time_until_available()
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Please wait {retry_after:.1f} seconds.",
                        "retry_after": retry_after,
                        "limit": self.requests_per_minute
                    },
                    headers={"Retry-After": str(int(retry_after) + 1)}
                )

            self._cleanup_old_buckets()

        response = await call_next(request)
        return response
