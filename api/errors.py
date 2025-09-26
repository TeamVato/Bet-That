"""Error handlers for Bet-That API"""
import logging
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from .settings import settings

logger = logging.getLogger(__name__)

def add_error_handlers(app: FastAPI):
    """Add global error handlers to the FastAPI app"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "detail": getattr(exc, 'cause', None) or exc.detail,
                "status_code": exc.status_code,
                "timestamp": datetime.now().isoformat()
            },
            headers={
                "X-Compliance-Disclaimer": settings.compliance_disclaimer,
                "X-Error-Type": "validation_error"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred. Please try again later.",
                "status_code": 500,
                "timestamp": datetime.now().isoformat()
            },
            headers={
                "X-Compliance-Disclaimer": settings.compliance_disclaimer,
                "X-Error-Type": "system_error"
            }
        )
