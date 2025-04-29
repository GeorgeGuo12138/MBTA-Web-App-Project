import os
import json
import pprint
import urllib.request
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys from environment variables
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
MBTA_API_KEY = os.getenv("MBTA_API_KEY")

# Useful base URLs (you need to add the appropriate parameters for each API request)
MAPBOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
MBTA_BASE_URL = "https://api-v3.mbta.com/stops"



# A little bit of scaffolding if you want to use it
def get_json(url: str) -> dict:
    """
    Given a properly formatted URL for a JSON web API request, return a Python JSON object containing the response to that request.

    Both get_lat_lng() and get_nearest_station() might need to use this function.
    """
    with urllib.request.urlopen(url) as response:
        data = response.read()
        return json.loads(data)


def get_lat_lng(place_name: str) -> tuple[str, str]:
    """
    Given a place name or address, return a (latitude, longitude) tuple with the coordinates of the given place.

    See https://docs.mapbox.com/api/search/geocoding/ for Mapbox Geocoding API URL formatting requirements.
    """
    query = place_name
    query = urllib.parse.quote(place_name)
    url = f"{MAPBOX_BASE_URL}/{query}.json?access_token={MAPBOX_TOKEN}&proximity=-71.058,42.360"


    data = get_json(url)

    # Debugging
    print(url)
    pprint.pprint(data)

    if data["features"]:
        # Look specifically for Massachusetts results first
        for feature in data["features"]:
            place_name = feature["place_name"]
            if "Massachusetts" in place_name:
                coordinates = feature["geometry"]["coordinates"]
                longitude, latitude = coordinates[0], coordinates[1]
                return str(latitude), str(longitude)
                
        # If no Massachusetts results, use the first result
        coordinates = data["features"][0]["geometry"]["coordinates"]
        longitude, latitude = coordinates[0], coordinates[1]
        return str(latitude), str(longitude)
    else:
        raise ValueError("Location not found")

def get_nearest_station(latitude: str, longitude: str) -> tuple[str, bool]:
    """
    Given latitude and longitude strings, return a (station_name, wheelchair_accessible) tuple for the nearest MBTA station to the given coordinates.

    See https://api-v3.mbta.com/docs/swagger/index.html#/Stop/ApiWeb_StopController_index for URL formatting requirements for the 'GET /stops' API.
    """
    url = (f"{MBTA_BASE_URL}?api_key={MBTA_API_KEY}" f"&filter[latitude]={latitude}&filter[longitude]={longitude}&sort=distance")
    data = get_json(url)

    if not data["data"]:
        raise ValueError(f"No stops found near coordinates ({latitude},{longitude}). Pick a alocation near Boston Area.")
    nearest_stop = data["data"][0]
    station = nearest_stop["attributes"]["name"]
    wheelchair_accessible = nearest_stop["attributes"].get("wheelchair_boarding") == 1

    return station, wheelchair_accessible

def find_stop_near(place_name: str) -> tuple[str, bool]:
    """
    Given a place name or address, return the nearest MBTA stop and whether it is wheelchair accessible.

    This function might use all the functions above.
    """
    lat, lon, = get_lat_lng(place_name)
    return get_nearest_station(lat, lon)

def main():
    """
    You should test all the above functions here
    """
    location = input("Enter a location: ")
    try:
        stop_name, wheelchair_access = find_stop_near(location)
        print(f"Closest MBTA stop to {location}: {stop_name}")
        print(f"Wheelchair Accessible: {'Yes' if wheelchair_access else 'No'}")
    except Exception as e:
        print(f"Error: {e}")



if __name__ == "__main__":
    main()