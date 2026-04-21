from typing import Any, Dict, List
from pprint import pprint
from datetime import date
import requests
import aiohttp


class GeocodingService:

    def __init__(self) -> None:
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {
            "User-Agent": "TravelPlannerApp/1.0 (educational project)"
        }

    def get_geocode(self, location: str) -> Dict[str, Any]:

        search_url = f"{self.base_url}/search"
        params = {
            "q": location,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }

        response = requests.get(
            search_url, headers=self.headers, params=params
        )
        data = response.json()[0]
        if not data:
            raise ValueError("Location not found")
        address = data.get("address")
        if not address:
            raise ValueError("Location not found")
        location_details = {
            "full_address": data.get("display_name"),
            "latitude": round(float(data.get("lat")), 4),
            "longitude": round(float(data.get("lon")), 4),
            "country": address.get("country"),
            "country_code": address.get("country_code"),
            "state": address.get("state"),
            "city": address.get("city"),
        }
        return location_details


if __name__ == "__main__":
    geocode_class = GeocodingService()
    data = geocode_class.get_geocode(location="Dum Dum, Kolkata")
    pprint(data)
