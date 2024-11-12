from fastapi import APIRouter, HTTPException
from urllib.parse import unquote
from .schemas import RouteResponse, RoutesResponse
from .routes import Routes

router = APIRouter(prefix="/alpine_routes", tags=["Alpine routes"])
routes = Routes()

@router.get("/", response_model=RoutesResponse)
async def get_all_routes():
    """Get a list of all available mountaineering routes."""
    return routes.get_routes()

@router.get("/{route_name}", response_model=RouteResponse)
async def get_route_info_by_name(route_name: str):
    decoded_route_name = unquote(route_name)
    result = await routes.parse(decoded_route_name.capitalize())
    if result.status == "404":
        raise HTTPException(status_code=404, detail=result.message)
    return result

@router.get("/{route_id}", response_model=RouteResponse)
async def get_route_info_by_id(route_id: int):
    result = await routes.parse(route_id)
    if result.status == "404":
        raise HTTPException(status_code=404, detail=result.message)
    return result

def close_routes():
    routes.close()
