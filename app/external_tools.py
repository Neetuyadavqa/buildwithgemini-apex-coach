# Copyright 2026 Google LLC
# External Public API tools for Apex Coach

import json
import urllib.request

CITY_COORDINATES = {
    "san francisco": (37.7749, -122.4194),
    "new york": (40.7128, -74.0060),
    "boston": (42.3601, -71.0589),
    "chicago": (41.8781, -87.6298),
    "london": (51.5074, -0.1278),
    "tokyo": (35.6762, 139.6503),
    "los angeles": (34.0522, -118.2437),
}


def get_live_outdoor_weather(city: str = "San Francisco") -> str:
    """Fetches real-time live weather and running conditions for a city using the Open-Meteo API.

    Args:
        city: Name of the city to check outdoor running conditions for (e.g. 'San Francisco', 'Boston', 'New York').

    Returns:
        A JSON string containing current temperature (°C/°F), humidity, wind speed, and outdoor running advice.
    """
    city_lower = city.lower().strip()
    lat, lon = CITY_COORDINATES.get(city_lower, (37.7749, -122.4194))

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ApexCoach/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        current = data.get("current", {})
        temp_c = current.get("temperature_2m", 20.0)
        temp_f = round((temp_c * 9 / 5) + 32, 1)
        humidity = current.get("relative_humidity_2m", 50)
        wind_kmh = current.get("wind_speed_10m", 10.0)

        # Outdoor running suitability assessment
        if 45 <= temp_f <= 65 and wind_kmh < 20:
            suitability = "Ideal for outdoor running! Cool temperature and light wind."
        elif temp_f > 85:
            suitability = "Caution: High heat. Hydrate heavily or perform an indoor treadmill workout."
        elif temp_f < 32:
            suitability = "Cold conditions: Wear insulated layers and windproof outer shell."
        else:
            suitability = "Good conditions for outdoor training."

        result = {
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "temperature_f": temp_f,
            "temperature_c": temp_c,
            "humidity_percent": humidity,
            "wind_speed_kmh": wind_kmh,
            "outdoor_running_advice": suitability,
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch live weather data: {str(e)}"})
