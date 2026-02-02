"""
Security and Rate Limiting Middleware
Production-ready middleware for security headers, rate limiting, and request validation.
"""

import time
import hashlib
from typing import Callable, Dict, Optional
from collections import defaultdict
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.types import ASGIApp

from .config import settings


# ============== SECURITY HEADERS MIDDLEWARE ==============

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    
    
    Headers added:
    - X-Content-Type-Options: Prevent MIME sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: Enable XSS filter
    - Referrer-Policy: Control referrer information
    - Content-Security-Policy: Restrict resource loading
    - Strict-Transport-Security: Force HTTPS (production only)
    - Permissions-Policy: Control browser features
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        if settings.SECURITY_HEADERS_ENABLED:
            # Prevent MIME type sniffing
            response.headers["X-Content-Type-Options"] = "nosniff"
            
            # Prevent clickjacking
            response.headers["X-Frame-Options"] = "DENY"
            
            # Enable XSS filter (legacy browsers)
            response.headers["X-XSS-Protection"] = "1; mode=block"
            
            # Control referrer information
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            # Content Security Policy
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
                "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' ws: wss:; "
                "frame-ancestors 'none';"
            )
            response.headers["Content-Security-Policy"] = csp
            
            # HSTS - only in production with HTTPS
            if settings.is_production:
                response.headers["Strict-Transport-Security"] = (
                    "max-age=31536000; includeSubDomains; preload"
                )
            
            # Permissions Policy (formerly Feature-Policy)
            response.headers["Permissions-Policy"] = (
                "accelerometer=(), camera=(), geolocation=(), "
                "gyroscope=(), magnetometer=(), microphone=(), "
                "payment=(), usb=()"
            )
            
            # Remove server header
            if "server" in response.headers:
                del response.headers["server"]
        
        return response


# ============== RATE LIMITING MIDDLEWARE ==============

class RateLimitStore:
    
    
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)
    
    def add_request(self, key: str, timestamp: float):
        """Record a request timestamp."""
        self._requests[key].append(timestamp)
    
    def get_request_count(self, key: str, window_start: float) -> int:
      
        self._requests[key] = [
            ts for ts in self._requests[key] if ts > window_start
        ]
        return len(self._requests[key])
    
    def cleanup(self, max_age: float = 3600):
    
        cutoff = time.time() - max_age
        for key in list(self._requests.keys()):
            self._requests[key] = [
                ts for ts in self._requests[key] if ts > cutoff
            ]
            if not self._requests[key]:
                del self._requests[key]


# Global rate limit store
rate_limit_store = RateLimitStore()


class RateLimitMiddleware(BaseHTTPMiddleware):
    
    
    def __init__(
        self,
        app: ASGIApp,
        requests_per_window: int = None,
        window_seconds: int = None,
    ):
        super().__init__(app)
        self.requests_per_window = requests_per_window or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW
    
    def _get_client_key(self, request: Request) -> str:
       
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Include path for more granular rate limiting
        path = request.url.path
        
        # Create hash for privacy
        key = f"{client_ip}:{path}"
        return hashlib.md5(key.encode()).hexdigest()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/"] or request.url.path.startswith("/static"):
            return await call_next(request)
        
        client_key = self._get_client_key(request)
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        # Check current request count
        request_count = rate_limit_store.get_request_count(client_key, window_start)
        
        if request_count >= self.requests_per_window:
            # Calculate retry-after
            oldest_request = min(rate_limit_store._requests[client_key])
            retry_after = int(oldest_request + self.window_seconds - current_time) + 1
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests",
                    "retry_after": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests_per_window),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(oldest_request + self.window_seconds)),
                },
            )
        
        # Record this request
        rate_limit_store.add_request(client_key, current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_per_window - request_count - 1
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response


# ============== REQUEST VALIDATION MIDDLEWARE ==============

class RequestValidationMiddleware(BaseHTTPMiddleware):
  
    
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check Content-Length
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > self.MAX_CONTENT_LENGTH:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"detail": "Request body too large"},
                    )
            except ValueError:
                pass
        
        return await call_next(request)


# ============== REQUEST LOGGING MIDDLEWARE ==============

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests with timing information."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Add timing header
        response.headers["X-Response-Time"] = f"{duration:.4f}s"
        
        # Log request (in production, use proper logging)
        if settings.DEBUG:
            client = request.client.host if request.client else "unknown"
            print(
                f"{request.method} {request.url.path} "
                f"[{response.status_code}] {duration:.4f}s - {client}"
            )
        
        return response


# ============== EXCEPTION HANDLERS ==============

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Custom HTTP exception handler with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": str(request.url.path),
        },
        headers=exc.headers,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    # In production, don't expose internal errors
    if settings.is_production:
        detail = "An internal error occurred"
    else:
        detail = str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "status_code": 500,
            "detail": detail,
            "path": str(request.url.path),
        },
    )
