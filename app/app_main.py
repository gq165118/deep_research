import logging
import sys
from pathlib import Path


def _bootstrap() -> None:
    app_dir = Path(__file__).resolve().parent
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))
    from dotenv import load_dotenv

    env_path = app_dir.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)


_bootstrap()


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .backend.config import AppSettings
from .backend.router import health_router, research_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logging.getLogger("mult_agents").setLevel(logging.INFO)
logging.getLogger("backend").setLevel(logging.INFO)


def create_app() -> FastAPI:
    settings = AppSettings()
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(research_router)
    return app


app = create_app()


if __name__ == "__main__":
    runtime_settings = AppSettings()
    uvicorn.run(
        "app.app_main:app",
        host=runtime_settings.host,
        port=runtime_settings.port,
        reload=runtime_settings.app_env == "development",
    )
