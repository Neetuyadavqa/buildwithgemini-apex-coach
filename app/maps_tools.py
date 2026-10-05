# Copyright 2026 Google LLC
# Google Maps Geocoding & Places (New) Tools for Apex Coach

import json
import os
import urllib.parse
import urllib.request
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def _get_api_key() -> str:
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set in .env")
    return key


def geocode_address(address: str) -> str:
    """Converts a street address or location name into geographic latitude and longitude coordinates.

    Args:
        address: The address or place name to geocode (e.g. 'Golden Gate Park, San Francisco, CA').

    Returns:
        A JSON string containing the location coordinates (lat, lng) and formatted address.
    """
    try:
        api_key = _get_api_key()
        encoded_address = urllib.parse.quote(address)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("status") == "OK" and data.get("results"):
            top_result = data["results"][0]
            loc = top_result["geometry"]["location"]
            result = {
                "address": address,
                "formatted_address": top_result.get("formatted_address"),
                "latitude": loc["lat"],
                "longitude": loc["lng"],
            }
            return json.dumps(result, indent=2)

        return json.dumps({"error": f"No geocoding results found for address: '{address}'."})
    except Exception as e:
        return json.dumps({"error": f"Geocoding failed: {str(e)}"})


def find_nearby_places(
    place_type: str, latitude: float, longitude: float, radius_meters: float = 5000.0
) -> str:
    """Finds nearby points of interest (e.g. parks, gyms, sports complexes) around a coordinate location.

    Args:
        place_type: Type of place to search for (e.g. 'park', 'gym', 'sports_complex', 'athletic_field').
        latitude: Center latitude coordinate.
        longitude: Center longitude coordinate.
        radius_meters: Search radius in meters (default is 5000 meters / 5 km).

    Returns:
        A JSON string containing matching nearby places with name, formatted address, location, and rating.
    """
    try:
        api_key = _get_api_key()
        url = "https://places.googleapis.com/v1/places:searchNearby"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types,places.rating",
        }

        payload = {
            "includedTypes": [place_type.lower().strip()],
            "maxResultCount": 5,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": latitude, "longitude": longitude},
                    "radius": float(radius_meters),
                }
            },
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        places = data.get("places", [])
        results = []
        for p in places:
            display_name = p.get("displayName", {}).get("text", "Unknown")
            results.append(
                {
                    "name": display_name,
                    "address": p.get("formattedAddress"),
                    "location": p.get("location"),
                    "rating": p.get("rating"),
                    "types": p.get("types", []),
                }
            )

        return json.dumps({"place_type": place_type, "count": len(results), "places": results}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to search nearby places: {str(e)}"})
