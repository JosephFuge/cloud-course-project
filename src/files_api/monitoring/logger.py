import json
import sys
import traceback

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
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <bold><white>{message}</white></bold> | <dim>{extra}</dim> {stacktrace}",
        filter=process_log_record,
    )

def process_log_record(record: "loguru.Record") -> "loguru.Record":
    extra = record["extra"]

    if extra:
        record["extra"] = json.dumps(extra, default=str) # type: ignore
    
    record["stacktrace"] = "" # type: ignore
    if record["exception"]:
        err = record["exception"]
        stacktrace = get_formatted_stacktrace(err, replace_newline_character_with_carriage_return=True)
        record["stacktrace"] = stacktrace # type: ignore
        
    return record

def get_formatted_stacktrace(loguru_record_exception, replace_newline_character_with_carriage_return: bool) -> str:
    """Get the formatted stacktrace for the current exception."""
    exc_type, exc_value, exc_traceback = loguru_record_exception
    stacktrace_: list[str] = traceback.format_exception(exc_type, exc_value, exc_traceback)
    stacktrace: str = "".join(stacktrace_)
    if replace_newline_character_with_carriage_return:
        stacktrace = stacktrace.replace("\n", "\r")
    return stacktrace

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