import json
import os
import urllib.parse
import urllib.request
from dotenv import load_dotenv

# ─── Load your secrets (.env is never committed to GitHub) ──────────────────────
load_dotenv()                       # reads the .env file once
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
MBTA_API_KEY = os.getenv("MBTA_API_KEY")

# Base URLs that never change
MAPBOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
MBTA_BASE_URL  = "https://api-v3.mbta.com/stops"


# ─────────────────────────── Helper functions ──────────────────────────────────
def get_json(url: str) -> dict:
    """Return the JSON response (as a Python dict) for any HTTP GET request."""
    with urllib.request.urlopen(url) as resp:
        data_bytes = resp.read()
    return json.loads(data_bytes.decode("utf-8"))


def get_lat_lng(place_name: str) -> tuple[str, str]:
    """
    Convert “Fenway Park” → (“42.346”, “-71.097”)

    Mapbox wants the query URL-encoded and the token added as a parameter.
    """
    query   = urllib.parse.quote(place_name)
    url     = f"{MAPBOX_BASE_URL}/{query}.json?access_token={MAPBOX_TOKEN}&limit=1"
    data    = get_json(url)
    # geometry.coordinates is [longitude, latitude]
    lon, lat = data["features"][0]["geometry"]["coordinates"]
    return str(lat), str(lon)


def get_nearest_station(latitude: str, longitude: str) -> tuple[str, bool]:
    """
    Return (station_name, is_wheelchair_accessible) for the closest MBTA stop.

    MBTA V3 lets us pass filter[latitude] & filter[longitude] and sort by distance.  [oai_citation:0‡HexDocs](https://hexdocs.pm/mbta_sdk/MBTA.Api.Prediction.html?utm_source=chatgpt.com)
    Wheelchair code: 1 = accessible, 2 = NOT accessible, 0 = unknown.
    """
    params = urllib.parse.urlencode(
        {
            "api_key": MBTA_API_KEY,
            "filter[latitude]":  latitude,
            "filter[longitude]": longitude,
            "sort": "distance",
            "page[limit]": 1,         # only need the closest one
        },
        safe="[]",                    # keep the square brackets as-is
    )
    url   = f"{MBTA_BASE_URL}?{params}"
    data  = get_json(url)
    stop  = data["data"][0]["attributes"]
    name  = stop["name"]
    wheel = stop["wheelchair_boarding"] == 1
    return name, wheel


def find_stop_near(place_name: str) -> tuple[str, bool]:
    """Glue the two steps together for convenient reuse."""
    lat, lon = get_lat_lng(place_name)
    return get_nearest_station(lat, lon)


# ─────────────────────────── Quick manual test ─────────────────────────────────
if __name__ == "__main__":
    print(find_stop_near("Museum of Science"))