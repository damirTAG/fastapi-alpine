from pydantic import BaseModel
from typing import List, Union, Dict

class AllRoutes(BaseModel):
    id: int
    route_name: str
    link: str

class RoutesResponse(BaseModel):
    status: str
    message: str
    data: Union[List[AllRoutes], AllRoutes, None]
    retrieval_time: str

class RouteData(BaseModel):
    id: int
    route_name: str
    link: str
    description: str
    images: List[str]

class RouteResponse(BaseModel):
    status: str
    message: str
    data: Union[List[RouteData], RouteData, None]
    retrieval_time: str