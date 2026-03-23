import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, chat, offer, profile, trip_plan, trip_vacancy
from app.api.dependencies import get_current_user
from app.core.config import config
from app.core.logging import setup_logging
from app.core.redis_client import init_redis
from app.models.user import User

setup_logging(level="DEBUG" if config.DEBUG else "INFO")

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = init_redis(config.REDIS_URL)
    await redis.connect()
    logger.info("Connected to Redis at %s", config.REDIS_URL)

    yield

    await redis.disconnect()
    logger.info("Redis connection closed")


app = FastAPI(title=config.APPLICATION_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(trip_vacancy.router, prefix="/api/v1")
app.include_router(offer.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(trip_plan.router, prefix="/api/v1")

# Mount uploads directory for serving uploaded files
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/api/v1/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.email}"}
