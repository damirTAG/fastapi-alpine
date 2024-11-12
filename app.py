import uvicorn
import os
from fastapi import FastAPI
from alpine_routes.endpoints import router, close_routes

app = FastAPI()
app.include_router(router)

@app.on_event("shutdown")
def shutdown_event():
    close_routes()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
