from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

def create_app() -> FastAPI:
    app = FastAPI(
        title="CurricuForge",
        description="Generative AI–Powered Curriculum Design System",
        version="1.0.0"
    )

    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(router)

    return app
