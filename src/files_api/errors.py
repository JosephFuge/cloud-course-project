from fastapi import (
    Request,
    status,
)
from fastapi.responses import JSONResponse
from pydantic import ValidationError


async def handle_broad_exceptions(request: Request, call_next):
    """Handle any exception that goes unhandled by a more specific exception handler."""
    try:
        return await call_next(request)
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


async def handle_pydantic_validation_errors(request: Request, exc: ValidationError):
    errors = exc.errors()

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": [{"msg": error["msg"], "input": error["input"]} for error in errors]},
    )
