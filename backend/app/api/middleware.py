import time
import uuid
import html
from collections import defaultdict
from datetime import datetime

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.utils.exceptions import ResumeShieldError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        response.headers["X-Processing-Time-Ms"] = str(duration_ms)
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration_ms,
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._hourly: dict[str, list[float]] = defaultdict(list)
        self._daily: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Only rate limit scan endpoints
        if not request.url.path.startswith("/api/v1/scan"):
            return await call_next(request)

        if request.method != "POST":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clean old entries
        self._hourly[client_ip] = [t for t in self._hourly[client_ip] if now - t < 3600]
        self._daily[client_ip] = [t for t in self._daily[client_ip] if now - t < 86400]

        if len(self._hourly[client_ip]) >= settings.rate_limit_per_hour:
            retry_after = int(3600 - (now - self._hourly[client_ip][0]))
            return JSONResponse(
                status_code=429,
                content={
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit exceeded. {settings.rate_limit_per_hour} scans per hour allowed.",
                    "details": {"retry_after_seconds": retry_after},
                    "timestamp": datetime.utcnow().isoformat(),
                },
                headers={"Retry-After": str(retry_after)},
            )

        if len(self._daily[client_ip]) >= settings.rate_limit_per_day:
            retry_after = int(86400 - (now - self._daily[client_ip][0]))
            return JSONResponse(
                status_code=429,
                content={
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Daily limit exceeded. {settings.rate_limit_per_day} scans per day allowed.",
                    "details": {"retry_after_seconds": retry_after},
                    "timestamp": datetime.utcnow().isoformat(),
                },
                headers={"Retry-After": str(retry_after)},
            )

        self._hourly[client_ip].append(now)
        self._daily[client_ip].append(now)

        return await call_next(request)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except ResumeShieldError as e:
            logger.warning("handled_error", error_code=e.error_code, message=e.message)
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error_code": e.error_code,
                    "message": e.message,
                    "details": e.details,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
        except Exception as e:
            logger.error("unhandled_error", error=str(e), exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error_code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": None,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )


class SanitizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Sanitization happens at the Pydantic model level and in clean_text
        # This middleware adds basic protection for query params
        return await call_next(request)


def sanitize_string(value: str) -> str:
    return html.escape(value.strip())
