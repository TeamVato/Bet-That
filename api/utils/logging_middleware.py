"""Structured logging middleware for FastAPI"""

import json
import logging
import time
from typing import Callable

from fastapi import Request, Response

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """Middleware for structured request/response logging"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start_time = time.time()

        # Extract client info
        client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"

        user_agent = request.headers.get("User-Agent", "")
        user_id = request.headers.get("X-User-Id", "")

        # Prepare log data
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "user_id": user_id,
            "timestamp": time.time(),
        }

        # Process request/response
        response_message = None

        async def send_wrapper(message):
            nonlocal response_message
            if message["type"] == "http.response.start":
                response_message = message
            await send(message)

        await self.app(scope, receive, send_wrapper)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        if response_message:
            log_data.update(
                {
                    "status_code": response_message.get("status", ""),
                    "process_time_ms": round(process_time * 1000, 2),
                }
            )

        # Log in JSON format for easy parsing
        logger.info(json.dumps(log_data))
