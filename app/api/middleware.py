import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request/response details and processing time.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        # Start timer
        start_time = time.time()

        # Log request details
        logger.info(f"→ Request: {request.method} {request.url.path}")
        logger.info(f"  Client: {request.client.host if request.client else 'Unknown'}")
        logger.info(f"  User-Agent: {request.headers.get('user-agent', 'Unknown')}")

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response details
            logger.info(f"← Response: {response.status_code}")
            logger.info(f"  Duration: {duration:.3f}s")

            # Add custom headers
            response.headers["X-Process-Time"] = f"{duration:.3f}s"

            return response

        except Exception as e:
            # Log errors
            duration = time.time() - start_time
            logger.error(f"✗ Error processing request: {str(e)}")
            logger.error(f"  Duration: {duration:.3f}s")
            raise

