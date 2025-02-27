from fastapi import FastAPI

from files_api.routes import ROUTER
from files_api.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create a FastAPI ROUTERlication"""
    settings = settings or Settings()

    app = FastAPI()
    app.state.settings = settings
    app.include_router(ROUTER)
    
    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
