"""User-initiated weather context via Open-Meteo's noncommercial endpoints.

Weather is informational; it NEVER replaces seasonal Model B inputs.
No GPS, user account, tokens or permanent storage are involved.
"""
from __future__ import annotations

import math
import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def _number(value, key):
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Weather provider returned an invalid {key}.") from exc
    if not math.isfinite(number):
        raise ValueError(f"Weather provider returned a non-finite {key}.")
    return number


def weather_label(code):
    code = int(code)
    if code == 0:
        return "Clear sky"
    if code in (1, 2, 3):
        return "Cloudy / partly cloudy"
    if code in (45, 48):
        return "Fog"
    if 51 <= code <= 57:
        return "Drizzle"
    if 61 <= code <= 67 or 80 <= code <= 82:
        return "Rain / showers"
    if 71 <= code <= 77 or 85 <= code <= 86:
        return "Snow"
    if code >= 95:
        return "Thunderstorms"
    return "Mixed conditions"


def fetch_city_weather(city: str):
    """Return first clearly labeled matching city and a five-day forecast."""
    if not isinstance(city, str) or not (2 <= len(city.strip()) <= 80):
        raise ValueError("Enter a city name with 2–80 characters.")
    city = city.strip()
    try:
        geocode_response = requests.get(
            GEOCODE_URL,
            params={"name": city, "count": 3, "language": "en", "format": "json"},
            timeout=(4, 10),
        )
        geocode_response.raise_for_status()
        geodata = geocode_response.json()
        matches = geodata.get("results", []) if isinstance(geodata, dict) else []
        if not matches:
            raise ValueError("City not found. Try a more specific name such as 'Jaipur, India'.")
        location = matches[0]
        latitude = _number(location.get("latitude"), "latitude")
        longitude = _number(location.get("longitude"), "longitude")
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            raise ValueError("Weather provider returned invalid coordinates.")

        weather_response = requests.get(
            FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "forecast_days": 5,
                "timezone": "auto",
            },
            timeout=(4, 12),
        )
        weather_response.raise_for_status()
        data = weather_response.json()
    except requests.RequestException as exc:
        raise ValueError("Weather service is unavailable. Prediction tools remain usable.") from exc
    except (KeyError, TypeError, IndexError, AttributeError) as exc:
        raise ValueError("Weather provider returned incomplete data.") from exc

    current = data.get("current", {})
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])
    precipitation = daily.get("precipitation_sum", [])
    if not all(isinstance(v, list) and len(v) >= 1 for v in (dates, highs, lows, precipitation)):
        raise ValueError("Weather forecast is missing required daily values.")
    limit = min(5, len(dates), len(highs), len(lows), len(precipitation))
    forecast = []
    for i in range(limit):
        forecast.append({
            "Date": str(dates[i]),
            "Max °C": _number(highs[i], "maximum temperature"),
            "Min °C": _number(lows[i], "minimum temperature"),
            "Precipitation (mm)": _number(precipitation[i], "precipitation"),
        })

    parts = [str(location.get("name", city))]
    if location.get("admin1"):
        parts.append(str(location["admin1"]))
    if location.get("country"):
        parts.append(str(location["country"]))
    return {
        "location": ", ".join(parts),
        "as_of": str(current.get("time", "Not supplied")),
        "timezone": str(data.get("timezone", "Unknown")),
        "temperature_c": _number(current.get("temperature_2m"), "temperature"),
        "humidity_pct": _number(current.get("relative_humidity_2m"), "humidity"),
        "wind_kmh": _number(current.get("wind_speed_10m"), "wind speed"),
        "conditions": weather_label(current.get("weather_code", -1)),
        "forecast": forecast,
        "source": "Open-Meteo.com",
    }
