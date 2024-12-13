import uvicorn
import os

from contextlib import asynccontextmanager
from fastapi import FastAPI

from alpine_routes.endpoints import router
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("starting...")
    yield
    print("shutting down...")

app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    kwargs = dict(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
    uvicorn.run(app, **kwargs)
