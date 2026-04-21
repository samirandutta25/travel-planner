import os
from typing import List, Optional
from enum import Enum
from dataclasses import dataclass
from pprint import pprint
import requests
from dotenv import load_dotenv

from geocoding_service import GeocodingService

@dataclass
class PointOfInterestInstance:
    name: str
    latitude: float
    longitude: float
    fsq_place_id: float
    distance_from_source_meter: int
    address: str
    locality: str
    postcode: str
    country_code: str


@dataclass
class StayOption:
    stay_type: str
    stay_type_fsq_code: str


@dataclass
class PointOfInterestQuery:
    search_query: str
    latitude: float | None = None
    longitude: float | None = None
    fsq_category_id: list | None = None
    radius_meter: int | None = None
    limit: int | None = None
    near: str | None = None

    def form_ll(self) -> str:
        return f"{self.latitude},{self.longitude}"


class StayTypes(Enum):
    BNB = 1
    Cabin = 2
    Hostel = 3
    Hotel = 4
    Lodge = 5
    Resort = 6


STAY_MAPPINGS = {
    StayTypes.BNB: StayOption(
        stay_type="Bed and Breakfast",
        stay_type_fsq_code="4bf58dd8d48988d1f8931735",
    ),
    StayTypes.Cabin: StayOption(
        stay_type="Cabin",
        stay_type_fsq_code="4bf58dd8d48988d1f8931735",
    ),
    StayTypes.Hostel: StayOption(
        stay_type="Hostel",
        stay_type_fsq_code="4bf58dd8d48988d1f8931735",
    ),
    StayTypes.Hotel: StayOption(
        stay_type="Hotel",
        stay_type_fsq_code="4bf58dd8d48988d1f8931735",
    ),
    StayTypes.Lodge: StayOption(
        stay_type="Lodge",
        stay_type_fsq_code="4bf58dd8d48988d1f8931735",
    ),
    StayTypes.Resort: StayOption(
        stay_type="Resort",
        stay_type_fsq_code="4bf58dd8d48988d1f8931735",
    ),
}

class Cuisines(Enum):
    Any = 1
    Indian = 2
    Asian = 3
    Italian  = 4
    FastFood = 5
    SouthIndian = 6
    BreakfastSpot = 7
    StreetFood = 8
    Bengali = 9

RESTAURANT_MAPPING = {
    Cuisines.Any: StayOption(
        stay_type="Restaurant",
        stay_type_fsq_code="4d4b7105d754a06374d81259",
    ),
    Cuisines.Indian: StayOption(
        stay_type="Indian Restaurant",
        stay_type_fsq_code="4bf58dd8d48988d10f941735",
    ),
    Cuisines.Asian: StayOption(
        stay_type="Asian Restaurant",
        stay_type_fsq_code="4bf58dd8d48988d142941735",
    ),
    Cuisines.Italian: StayOption(
        stay_type="Italian Restaurant",
        stay_type_fsq_code="4bf58dd8d48988d110941735",
    ),
    Cuisines.FastFood: StayOption(
        stay_type="Fast Food Restaurant",
        stay_type_fsq_code="4bf58dd8d48988d16e941735",
    ),
    Cuisines.SouthIndian: StayOption(
        stay_type="South Indian Restaurant",
        stay_type_fsq_code="54135bf5e4b08f3d2429dfde",
    ),
    Cuisines.BreakfastSpot: StayOption(
        stay_type="Breakfast Spot",
        stay_type_fsq_code="4bf58dd8d48988d143941735",
    ),
    Cuisines.StreetFood: StayOption(
        stay_type="Street Food",
        stay_type_fsq_code="53e0feef498e5aac066fd8a9",
    ),
    Cuisines.Bengali: StayOption(
        stay_type="Bengali Restaurant",
        stay_type_fsq_code="54135bf5e4b08f3d2429dff5",
    ),
}

LANDMARK_TYPES = {
    "landmark_outdoors": "4d4b7105d754a06377d81259",
    "amusement_parks": "4bf58dd8d48988d182941735",
    "travel_points": "4d4b7105d754a06379d81259",
    "sports": "4f4528bc4b90abdf24c9de85",
}

class PointOfInterestsService:

    @staticmethod
    def _get_api_details() -> tuple:
        load_dotenv()
        key = os.getenv("FOURSQUARED_API_KEY")
        version = os.getenv("FOURSQUARED_API_VERSION")
        return key, version

    def __init__(self, geocoding_service: GeocodingService) -> None:
        self._api_key, self._api_version = self.__class__._get_api_details()
        self._base_url = "https://places-api.foursquare.com/places"
        self._geo_srv = geocoding_service

    def _format_api_data(self, poi_response_list: dict):
        places = poi_response_list["results"]
        list_of_poi = []
        for place in places:
            location = place.get("location")
            poi = PointOfInterestInstance(
                name=place.get("name", "NA"),
                latitude=place.get("latitude"),
                longitude=place.get("longitude"),
                fsq_place_id=place.get("fsq_place_id"),
                distance_from_source_meter=place.get("distance"),
                address=location.get("formatted_address"),
                locality=location.get("locality"),
                postcode=location.get("postcode"),
                country_code=location.get("country"),
            )
            list_of_poi.append(poi)
        return list_of_poi

    def search_places_of_interest(
        self, poi_query: PointOfInterestQuery
    ) -> List[PointOfInterestInstance]:
        url = f"{self._base_url}/search"

        params = {
            "query": poi_query.search_query,
            "radius": (
                poi_query.radius_meter if poi_query.radius_meter else 5000
            ),
        }
        if poi_query.fsq_category_id:
            params["fsq_category_ids"] = ",".join(poi_query.fsq_category_id)

        if poi_query.limit:
            params["limit"] = poi_query.limit

        if poi_query.latitude and poi_query.longitude:
            params["ll"] = poi_query.form_ll()

        headers = {
            "X-Places-Api-Version": self._api_version,
            "accept": "application/json",
            "authorization": f"Bearer {self._api_key}",
        }
        response = requests.get(url, headers=headers, params=params)
        return self._format_api_data(response.json())

    def search_land_mark_near_location(
        self, landmark_name: str, geo_area: str
    ) -> PointOfInterestInstance:
        loc = self._geo_srv.get_geocode(geo_area)
        landmark_array = [cat_id for cat_id in LANDMARK_TYPES.values()]
        query = PointOfInterestQuery(
            search_query=landmark_name,
            latitude=loc.get("latitude"),
            longitude=loc.get("longitude"),
            fsq_category_id=landmark_array,
            radius_meter=100000,
            limit=1,
        )

        list_poi = self.search_places_of_interest(query)
        if not list_poi:
            raise ValueError(
                "Landmark not found or > 100 km away from location"
            )
        return list_poi[0]

    def search_stay_near_location(
        self, stay: StayTypes, latitude: float, longitude: float, limit: int = 4
    ) -> List[PointOfInterestInstance]:
        stay_obj = STAY_MAPPINGS[stay]
        query = PointOfInterestQuery(
            latitude=latitude,
            longitude=longitude,
            search_query=stay_obj.stay_type,
            fsq_category_id=[stay_obj.stay_type_fsq_code],
            radius_meter=4000,
            limit=limit,
        )
        return self.search_places_of_interest(query)
    
    def search_dining_near_location(
        self, cuisine: Cuisines, latitude: float, longitude: float, limit: int = 4
    ) -> List[PointOfInterestInstance]:
        din_obj = RESTAURANT_MAPPING[cuisine]
        query = PointOfInterestQuery(
            latitude=latitude,
            longitude=longitude,
            search_query=din_obj.stay_type,
            fsq_category_id=[din_obj.stay_type_fsq_code],
            radius_meter=4000,
            limit=limit,
        )
        return self.search_places_of_interest(query)
    
    def search_pubs_near_location(
        self, latitude: float, longitude: float, limit: int = 4
    ) -> List[PointOfInterestInstance]:
        query = PointOfInterestQuery(
            latitude=latitude,
            longitude=longitude,
            search_query="Pub",
            fsq_category_id=["4bf58dd8d48988d116941735"],
            radius_meter=5000,
            limit=limit,
        )
        return self.search_places_of_interest(query)


if __name__ == "__main__":
    geocode_srv = GeocodingService()
    poi_fct = PointOfInterestsService(geocode_srv)
    location = "Lalbagh"
    city = "Bengaluru, IN"
    print(f"Search {location}")
    vm_data = poi_fct.search_land_mark_near_location(
        landmark_name=location, geo_area=city
    )
    pprint(vm_data)

    print(f"\n\nSearch Dominos Pizza in 4km radius of {location}")
    query = PointOfInterestQuery(
        latitude=vm_data.latitude,
        longitude=vm_data.longitude,
        search_query="Domino's Pizza",
        fsq_category_id=["63be6904847c3692a84b9bb5"],
        radius_meter=4000,
        limit=2,
    )
    data = poi_fct.search_places_of_interest(query)
    pprint(data)

    print(f"\n\nSearch Hotel near {location}")

    data = poi_fct.search_stay_near_location(
        latitude=vm_data.latitude, longitude=vm_data.longitude, stay=StayTypes.Hotel
    )
    pprint(data)


    print(f"\n\nSearch Restaurant near {location}")

    data = poi_fct.search_dining_near_location(
        latitude=vm_data.latitude, longitude=vm_data.longitude, cuisine=Cuisines.Indian
    )
    pprint(data)
