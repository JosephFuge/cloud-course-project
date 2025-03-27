import json
import sys

import loguru
from fastapi import (
    Request,
    Response,
)
from loguru import logger


def configure_logger():
    logger.remove()
    logger.add(
        sink=sys.stdout,
        diagnose=False,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <bold><white>{message}</white></bold> | <dim>{extra}</dim>",
        filter=process_log_record,
    )

def process_log_record(record: "loguru.Record") -> "loguru.Record":
    extra = record["extra"]

    if extra:
        record["extra"] = json.dumps(extra, default=str) # type: ignore
        
    return record

def log_request_info(request: Request):
    """Log the request info."""
    request_info = {
        "method": request.method,
        "path": request.url.path,
        "query_params": dict(request.query_params.items()),
        "path_params": dict(request.path_params.items()),
        "headers": dict(request.headers.items()),  # note: logging headers can leak secrets
        "base_url": str(request.base_url),
        "url": str(request.url),
        "client": str(request.client),
        "server": str(request.scope.get("server", "unknown")),
        "cookies": dict(request.cookies.items()), # note: logging cookies can leak secrets
    }
    logger.debug("Request received", http_request=request_info)

def log_response_info(response: Response):
    """Log the response info."""
    response_info = {
        "status_code": response.status_code,
        "headers": dict(response.headers.items()),
    }
    logger.debug("Response sent", http_response=response_info)

async def log_request_and_response_info(request: Request, call_next):
    log_request_info(request)
    response = await call_next(request)
    log_response_info(response)
    return response