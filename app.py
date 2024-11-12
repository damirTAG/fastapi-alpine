import uvicorn
import os

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from alpine_routes.endpoints import router, close_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("starting...")
    yield
    print("shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/", tags=["Homepage"])
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
