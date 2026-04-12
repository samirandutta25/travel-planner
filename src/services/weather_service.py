from typing import Any, Dict, List
from pprint import pprint
from datetime import date
import requests
import aiohttp


class WeatherAPIService:

    _WEATHER_CODE_MAPPING = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    def __init__(self) -> None:
        self.base_url = "https://api.open-meteo.com/v1"

    def get_forecast(self, latitude: float, longitude: float) -> Any:
        forecast_url = f"{self.base_url}/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
            "forecast_days": 7,
        }

        weather_data: Dict[str, Any] = {
            "location": {
                "latitude": latitude,
                "longitude": longitude,
            }
        }
        data = requests.get(forecast_url, params=params)
        weather_data["daily_data"] = self._parse_forecast_result(data.json())
        return weather_data

    def _parse_forecast_result(
        self, raw_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        forecasts = []
        raw_data = raw_data.get("daily", dict())
        # Below all are same length Arrays
        dates: List = raw_data.get("time", [])
        n: int = len(dates)
        temp_max: List = raw_data.get("temperature_2m_max", [])
        temp_min: List = raw_data.get("temperature_2m_min", [])
        chance_of_rain: List = raw_data.get(
            "precipitation_probability_max", []
        )
        weather_code: List = raw_data.get("weathercode", [])
        for i in range(n):
            forecasts.append(
                {
                    "date": dates[i],
                    "max_temperature": round(temp_max[i], 2),
                    "min_temperature": round(temp_min[i], 2),
                    "average_temperature": round(
                        (temp_max[i] + temp_min[i]) / 2, 2
                    ),
                    "raining_prbability": chance_of_rain[i],
                    "weather_code": int(weather_code[i]),
                    "weather_description": self._WEATHER_CODE_MAPPING.get(
                        int(weather_code[i]), "UNKNOWN"
                    ),
                }
            )
        return forecasts


if __name__ == "__main__":
    weather_fct = WeatherAPIService()
    data = weather_fct.get_forecast(latitude=22.57, longitude=88.36)
    pprint(data)
