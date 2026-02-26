from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, profile, trip_vacancy
from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.config import config

from contextlib import asynccontextmanager


from app.core.redis_client import init_redis, get_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = init_redis(config.REDIS_URL)
    await redis.connect()
    print(f"✓ Connected to Redis at {config.REDIS_URL}")

    yield

    await redis.disconnect()
    print("✓ Redis connection closed")


app = FastAPI(title=config.APPLICATION_NAME, lifespan=lifespan)

# Configure CORS
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


@app.get("/api/v1/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.email}"}
