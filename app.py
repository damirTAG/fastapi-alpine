import uvicorn, os
from fastapi import FastAPI, APIRouter, HTTPException

from routes import Routes
from schema import RouteResponse, RoutesResponse

router = APIRouter()
app = FastAPI()
routes = Routes()

@router.get("/routes/", response_model=RoutesResponse)
async def get_all_routes():
    """Get a list of all available routes."""
    return routes.get_routes()

@router.get("/routes/{route_name}", response_model=RouteResponse)
async def get_route_info(route_name: str):
    result = await routes.parse(route_name.capitalize())
    if result.status == "error":
        raise HTTPException(status_code=404, detail=result.message)
    return result

@router.get("/routes/{route_id}", response_model=RouteResponse)
async def get_route_info(route_id: str):
    result = await routes.parse(route_id)
    if result.status == "error":
        raise HTTPException(status_code=404, detail=result.message)
    return result


@app.on_event("shutdown")
def shutdown_event():
    routes.close()

# Include the router in the FastAPI app
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))