import json
import os
import pprint
import urllib.request

from dotenv import load_dotenv


# ─────────────────────────── Load API keys ─────────────────────────────────────
load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
MBTA_API_KEY = os.getenv("MBTA_API_KEY")

MAPBOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
MBTA_BASE_URL  = "https://api-v3.mbta.com/stops"


# ─────────────────────────── Helper: GET → JSON ───────────────────────────────
def get_json(url: str) -> dict:
    """Download *url* and return the parsed JSON."""
    with urllib.request.urlopen(url) as resp:
        data_bytes = resp.read()
    return json.loads(data_bytes.decode("utf-8"))


# ─────────────────────────── Geocoding via Mapbox ─────────────────────────────
def get_lat_lng(place_name: str) -> tuple[str, str]:
    """
    Convert a place name (“Fenway Park”) into (lat, lon) strings.

    Because we are avoiding urllib.parse, we only replace blanks with %20.
    That is enough for simple inputs used in this assignment.
    """
    query = place_name
    query = query.replace(" ", "%20")
    url = f"{MAPBOX_BASE_URL}/{query}.json?access_token={MAPBOX_TOKEN}&types=poi,address,place"
    data  = get_json(url)

    # Mapbox returns coordinates as [longitude, latitude]
    lon, lat = data["features"][0]["geometry"]["coordinates"]
    return str(lat), str(lon)


# ───────────────────────────── MBTA nearest stop ──────────────────────────────
def get_nearest_station(lat: str, lon: str) -> tuple[str, bool]:
    """
    Given coordinates, return (station_name, is_wheelchair_accessible).

    We build the query string manually – square brackets are written verbatim.
    """
    url = (
        f"{MBTA_BASE_URL}"
        f"?api_key={MBTA_API_KEY}"
        f"&filter[latitude]={lat}"
        f"&filter[longitude]={lon}"
        f"&sort=distance"
        f"&page[limit]=1"
    )
    data = get_json(url)

    stop   = data["data"][0]["attributes"]
    name   = stop["name"]
    # Wheelchair code: 1 = accessible; 2 or 0 = not / unknown
    wheel  = stop["wheelchair_boarding"] == 1
    return name, wheel


# ─────────────────────────── Convenience wrapper ──────────────────────────────
def find_stop_near(place_name: str) -> tuple[str, bool]:
    """One-liner for outside use."""
    lat, lon = get_lat_lng(place_name)
    return get_nearest_station(lat, lon)


# ─────────────────────────── Manual quick-test ────────────────────────────────
if __name__ == "__main__":
    result = find_stop_near("Museum of Science")
    pprint.pprint(result)          # e.g. ('Science Park/West End', True)
