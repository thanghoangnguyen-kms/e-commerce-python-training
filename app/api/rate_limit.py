"""
Rate limiting configuration for API endpoints.

This module provides rate limiting functionality to prevent abuse of API endpoints.
Uses slowapi library for Redis-backed rate limiting.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Initialize limiter with remote address as key function
# This tracks rate limits per IP address
limiter = Limiter(key_func=get_remote_address)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.

    Returns a JSON response with appropriate status code and message.
    """
    logger.warning(
        f"Rate limit exceeded for {request.client.host if request.client else 'Unknown'} "
        f"on {request.method} {request.url.path}"
    )

    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please slow down and try again later.",
            "detail": str(exc.detail) if hasattr(exc, 'detail') else None
        }
    )


# Rate limit configuration for product endpoints
PRODUCT_RATE_LIMIT = "5/minute"  # 5 requests per minute for product endpoints

