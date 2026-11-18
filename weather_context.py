"""User-initiated weather context with Open-Meteo and official MET Norway fallback.

Weather is informational; it NEVER replaces seasonal Model B inputs.
No GPS, user account, tokens or permanent storage are involved.
"""
from __future__ import annotations

import logging
import math
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
LOGGER = logging.getLogger(__name__)
RETRYABLE_STATUSES = {500, 502, 503, 504}
MET_FORECAST_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
MET_USER_AGENT = "CropCastAI/1.1 (+https://github.com/Kxni5hk/crop-yield-predictor)"
_met_cache = {}
_forecast_blocked_until = 0.0


class WeatherRateLimited(ValueError):
    def __init__(self, message, retry_after=0):
        super().__init__(message)
        self.retry_after = retry_after



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



def _request_json(url, params, timeout, stage):
    """Retry one transient failure; respect 429 instead of hammering the API."""
    for attempt in range(2):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("Weather provider returned malformed data.")
            return payload
        except requests.HTTPError as exc:
            response = exc.response
            status = getattr(response, "status_code", None)
            LOGGER.warning("Weather provider HTTP error; stage=%s status=%s", stage, status)
            if status == 429:
                headers = getattr(response, "headers", {}) or {}
                wait_value = headers.get("Retry-After", "")
                try:
                    wait_seconds = int(float(wait_value))
                except (TypeError, ValueError, OverflowError):
                    wait_seconds = 0
                wait_hint = (
                    f"Retry after about {wait_seconds} seconds. "
                    if 0 < wait_seconds <= 86400 else "Please try again later. "
                )
                raise WeatherRateLimited(
                    "Weather provider is rate limiting requests (HTTP 429). "
                    + wait_hint + "Crop yield predictions remain available.",
                    retry_after=wait_seconds,
                ) from exc
            if status in RETRYABLE_STATUSES and attempt == 0:
                time.sleep(0.4)
                continue
            raise ValueError(
                "Weather service is unavailable right now. "
                "Please try again later; crop yield predictions remain available."
            ) from exc
        except (requests.Timeout, requests.ConnectionError) as exc:
            LOGGER.warning("Weather provider network error; stage=%s type=%s", stage, type(exc).__name__)
            if attempt == 0:
                time.sleep(0.4)
                continue
            raise ValueError(
                "Weather service is unavailable due to a connection problem. "
                "Please try again later; crop yield predictions remain available."
            ) from exc
        except requests.RequestException as exc:
            LOGGER.warning("Weather provider request error; stage=%s type=%s", stage, type(exc).__name__)
            raise ValueError(
                "Weather service is unavailable right now. "
                "Please try again later; crop yield predictions remain available."
            ) from exc
        except ValueError as exc:
            raise ValueError("Weather provider returned malformed data. Please try again later.") from exc
    raise ValueError("Weather service is unavailable. Crop yield predictions remain available.")



def _met_json(latitude, longitude):
    """Respect MET Norway's Expires/Last-Modified caching and identifying UA."""
    key = (round(latitude, 4), round(longitude, 4))
    now = datetime.now(timezone.utc)
    cached = _met_cache.get(key)
    if cached and now < cached["expires"]:
        return cached["payload"]

    headers = {"User-Agent": MET_USER_AGENT, "Accept": "application/json"}
    if cached and cached.get("last_modified"):
        headers["If-Modified-Since"] = cached["last_modified"]
    try:
        resp = requests.get(
            MET_FORECAST_URL,
            params={"lat": key[0], "lon": key[1]},
            headers=headers,
            timeout=(5, 15),
        )
        if resp.status_code == 304 and cached:
            payload = cached["payload"]
        else:
            resp.raise_for_status()
            payload = resp.json()
            if not isinstance(payload, dict):
                raise ValueError("Backup weather service returned malformed data.")
    except requests.RequestException as exc:
        LOGGER.warning("Backup weather provider failed; status=%s",
                       getattr(getattr(exc, "response", None), "status_code", None))
        raise ValueError("Both forecast services are temporarily unavailable. "
                         "Crop yield predictions remain available.") from exc

    now = datetime.now(timezone.utc)
    try:
        expires = parsedate_to_datetime(resp.headers.get("Expires", ""))
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError, IndexError):
        expires = now + timedelta(minutes=30)
    if expires < now:
        expires = now + timedelta(minutes=10)

    # Bounded, in-memory cache; no user data is persisted.
    if len(_met_cache) >= 128 and key not in _met_cache:
        oldest_key = min(_met_cache, key=lambda k: _met_cache[k]["expires"])
        _met_cache.pop(oldest_key, None)
    _met_cache[key] = {
        "payload": payload,
        "expires": expires,
        "last_modified": resp.headers.get("Last-Modified")
            or (cached or {}).get("last_modified"),
    }
    return payload


def _met_label(symbol):
    symbol = str(symbol or "").lower()
    if "thunder" in symbol:
        return "Thunderstorms"
    if "snow" in symbol:
        return "Snow"
    if "rain" in symbol:
        return "Rain / showers"
    if "sleet" in symbol:
        return "Mixed precipitation"
    if "fog" in symbol:
        return "Fog"
    if "cloud" in symbol:
        return "Cloudy / partly cloudy"
    if "fair" in symbol or "clear" in symbol:
        return "Clear sky"
    return "Mixed conditions"


def _met_weather(payload, location, city):
    """Convert MET Norway forecast time-series into the existing UI schema."""
    series = payload.get("properties", {}).get("timeseries", [])
    if not isinstance(series, list) or not series:
        raise ValueError("Backup weather service returned incomplete forecast data.")
    tz_name = str(location.get("timezone") or "UTC")
    try:
        tz = ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, ValueError):
        tz = timezone.utc
        tz_name = "UTC"

    first = series[0]
    instant = first.get("data", {}).get("instant", {}).get("details", {})
    if not isinstance(instant, dict):
        raise ValueError("Backup weather service returned incomplete current conditions.")
    wind_ms = _number(instant.get("wind_speed"), "wind speed")
    first_data = first.get("data", {})
    summary = {}
    for key in ("next_1_hours", "next_6_hours", "next_12_hours"):
        x = first_data.get(key, {})
        if isinstance(x, dict) and isinstance(x.get("summary"), dict):
            summary = x["summary"]
            break

    daily = {}
    for item in series:
        try:
            moment = datetime.fromisoformat(
                str(item["time"]).replace("Z", "+00:00")
            )
            if moment.tzinfo is None:
                moment = moment.replace(tzinfo=timezone.utc)
            date = moment.astimezone(tz).date().isoformat()
            details = item["data"]["instant"]["details"]
            temperature = _number(details["air_temperature"], "forecast temperature")
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise ValueError("Backup weather service returned malformed hourly forecast.") from exc
        if date not in daily and len(daily) == 5:
            continue
        row = daily.setdefault(date, {
            "high": temperature, "low": temperature, "precip": 0.0, "has_precip": False,
        })
        row["high"] = max(row["high"], temperature)
        row["low"] = min(row["low"], temperature)

        # Prefer the shortest available accumulation period per timestamp.
        # Mixed periods may cross local midnight: these are approximate daily totals.
        for period in ("next_1_hours", "next_6_hours", "next_12_hours"):
            bucket = item.get("data", {}).get(period, {})
            details = bucket.get("details", {}) if isinstance(bucket, dict) else {}
            if "precipitation_amount" in details:
                row["precip"] += max(0.0, _number(
                    details["precipitation_amount"], "forecast precipitation"
                ))
                row["has_precip"] = True
                break

    forecast = [{
        "Date": date,
        "Max °C": round(row["high"], 1),
        "Min °C": round(row["low"], 1),
        "Precipitation (mm)": round(row["precip"], 1) if row["has_precip"] else None,
    } for date, row in sorted(daily.items())[:5]]
    if len(forecast) < 5:
        raise ValueError("Backup weather service supplied fewer than five forecast days.")

    parts = [str(location.get("name", city))]
    if location.get("admin1"):
        parts.append(str(location["admin1"]))
    if location.get("country"):
        parts.append(str(location["country"]))
    return {
        "location": ", ".join(parts),
        "as_of": str(first.get("time", "Not supplied")),
        "timezone": tz_name,
        "temperature_c": _number(instant.get("air_temperature"), "temperature"),
        "humidity_pct": _number(instant.get("relative_humidity"), "humidity"),
        "wind_kmh": round(wind_ms * 3.6, 1),
        "conditions": _met_label(summary.get("symbol_code")),
        "forecast": forecast,
        "source": "MET Norway Locationforecast 2.0",
        "backup_source": True,
    }


def fetch_city_weather(city: str):
    """Return first clearly labeled matching city and a five-day forecast."""
    if not isinstance(city, str) or not (2 <= len(city.strip()) <= 80):
        raise ValueError("Enter a city name with 2–80 characters.")
    city = city.strip()
    geodata = _request_json(
        GEOCODE_URL,
        {"name": city, "count": 3, "language": "en", "format": "json"},
        (4, 10),
        "geocoding",
    )
    matches = geodata.get("results", [])
    if not isinstance(matches, list):
        raise ValueError("Weather provider returned incomplete city data.")
    if not matches:
        raise ValueError("City not found. Try a more specific city name such as 'Jaipur'.")
    location = matches[0]
    if not isinstance(location, dict):
        raise ValueError("Weather provider returned incomplete city data.")
    latitude = _number(location.get("latitude"), "latitude")
    longitude = _number(location.get("longitude"), "longitude")
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError("Weather provider returned invalid coordinates.")
    global _forecast_blocked_until
    # After the free provider returns Retry-After, do not keep contacting it.
    if time.monotonic() < _forecast_blocked_until:
        return _met_weather(_met_json(latitude, longitude), location, city)

    try:
        data = _request_json(
            FORECAST_URL,
            {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "forecast_days": 5,
                "timezone": "auto",
            },
            (4, 12),
            "forecast",
        )
    except WeatherRateLimited as exc:
        _forecast_blocked_until = time.monotonic() + max(exc.retry_after, 1800)
        LOGGER.info("Using MET Norway backup after Open-Meteo forecast rate limit.")
        return _met_weather(_met_json(latitude, longitude), location, city)

    current = data.get("current", {})
    daily = data.get("daily", {})
    if not isinstance(current, dict) or not isinstance(daily, dict):
        raise ValueError("Weather provider returned incomplete data.")
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
