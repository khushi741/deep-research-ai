from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router
from app.storage.database import init_db
from app.utils.logging import get_logger

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifespan management."""
    logger.info("Initializing Deep Research AI application database...")
    init_db()
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} ready.")
    yield
    logger.info("Shutting down Deep Research AI application.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-Quality Autonomous Deep Research AI Agent Backend",
    lifespan=lifespan
)

# Enable CORS for local Streamlit frontend & web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
