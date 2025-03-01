from fastapi import FastAPI
from pydantic import ValidationError

from files_api.errors import (
    handle_broad_exceptions,
    handle_pydantic_validation_errors,
)
from files_api.routes import ROUTER
from files_api.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create a FastAPI ROUTERlication"""
    settings = settings or Settings()

    app = FastAPI()
    app.state.settings = settings
    app.include_router(ROUTER)

    app.add_exception_handler(exc_class_or_status_code=ValidationError, handler=handle_pydantic_validation_errors)

    app.middleware("http")(handle_broad_exceptions)
    
    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
