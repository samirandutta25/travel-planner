from typing import Any
from langchain_core.tools import tool
from .geocoding_service import GeocodingService
from .weather_service import WeatherAPIService

@tool
def get_weather(latitude: float, longitude: float) -> str:
    """
    Get Weather Forecast Information for a given latitude
    and longitude. Gets min, max average temperature 
    Chance of rainfall(precipitation), and a weather decription
    like cloudy, sunny etc. for the next 7 days from now.
    """
    weather_service = WeatherAPIService()
    return weather_service.get_forecast(latitude, longitude)

@tool
def get_coordinates(location: str) -> Any:
    """
    full_address, latitude, longitude, country,
    country_code, state, city information for any 
    address passed in as string better if comma 
    separated, adding state, country after the address makes 
    the results much more reliable and help resolve 
    duplicate addresses
    """
    geo_service = GeocodingService()
    return geo_service.get_geocode(location=location)