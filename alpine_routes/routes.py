from datetime import datetime
import re, os
import sqlite3
import aiohttp

from typing import Dict, List, Union, Optional
from bs4 import BeautifulSoup
from .schemas import RouteResponse, RouteData, RoutesResponse, AllRoutes

import logging

logging.basicConfig(level=logging.DEBUG)
current_dir = os.path.dirname(__file__)

class Routes:
    def __init__(self, db_path: Optional[Union[str, os.PathLike]] = None) -> None:
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = os.path.join(current_dir, '..', 'database', 'alpine_routes.db')
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.OperationalError as e:
            print(f"Failed to connect to the database at {self.db_path}: {e}")
            self.conn = None
            self.cursor = None

    def _find_route_details(self, route_name: str) -> List[Dict[str, Union[int, str]]]:
        """Find all routes that match the route name or ID."""
        self.cursor.execute("SELECT id, route_name, route_link FROM routes WHERE route_name LIKE ?", (f'%{route_name}%',))
        results = self.cursor.fetchall()

        if not results:
            transformed_name = route_name.capitalize()[:-1] + route_name[-1].upper()
            self.cursor.execute("SELECT id, route_name, route_link FROM routes WHERE route_name LIKE ?", (f'%{transformed_name}%',))
            results = self.cursor.fetchall()
        if not results:
            self.cursor.execute("SELECT id, route_name, route_link FROM routes WHERE id = ?", (route_name,))
            results = self.cursor.fetchall()

        return [{"id": result[0], "route_name": result[1], "route_link": result[2]} for result in results]

    async def _fetch_page_content(self, url: str) -> Union[str, None]:
        """Fetch HTML content from the given URL."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text() if response.status == 200 else None

    def _clean_description(self, description: str) -> str:
        """Clean up and format the description text."""
        description = re.sub(r'\n\s*\n', '\n', description)
        return description.strip()

    def _parse_html_content(self, html_content: str) -> Dict[str, Union[str, List[str]]]:
        """Extract description and images from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        content_div = soup.find('div', {'id': 'content'})
        photo_gallery_div = soup.find('div', {'id': 'photo-gallery'})

        description = "\n".join(p.get_text() for p in content_div.find_all('p')) if content_div else ""
        description = self._clean_description(description)

        images = [f"https://mountain.kz/{a['href']}" for a in photo_gallery_div.find_all('a', {'rel': 'lightbox[id366]'})] if photo_gallery_div else []
        if not images and content_div:
            images = [f"https://mountain.kz/{a['href']}" for a in content_div.find_all('a', {'rel': 'lightbox'})]

        return {
            "description": description or "Description not available.",
            "images": images or ["No images available."]
        }

    async def parse(self, route_name: str) -> Dict[str, Union[str, List[Dict[str, Union[str, int]]], Dict[str, Union[str, List[str]]]]]:
        """High-level method to get parsed data for a route."""
        route_details = self._find_route_details(route_name)
        if not route_details:
            return RouteResponse(
                status="404",
                message="Route not found =(",
                data=None,
                retrieval_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        return RouteResponse(
            status="success",
            message="Route(-s) fetched.",
            data=[
                    await self._get_route_data(route)
                    for route in route_details
                ],
            retrieval_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )


    async def _get_route_data(self, route: Dict[str, str]) -> RouteData:
        """Helper method to fetch parsed data for a specific route."""
        html_content = await self._fetch_page_content(route["route_link"])
        if not html_content:
            return RouteData(
                id=route["id"],
                route_name=route["route_name"],
                link=route["route_link"],
                description="",
                images=[]
            )

        parsed_data = self._parse_html_content(html_content)

        return RouteData(
            id=route["id"],
            route_name=route["route_name"],
            link=route["route_link"],
            description=parsed_data.get("description", ""), 
            images=parsed_data.get("images", [])
        )
        

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        self.close()

    def get_routes(self):
        self.cursor.execute("SELECT id, route_name, route_link FROM routes")
        routes = self.cursor.fetchall()

        if not routes:
            return RoutesResponse(
                status="404",
                message="Nothing found",
                data=None,
                retrieval_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

        route_data = [AllRoutes(id=route[0], route_name=route[1], link=route[2]) for route in routes]

        return RoutesResponse(
            status="success",
            message="All routes fetched.",
            data=route_data,
            retrieval_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
