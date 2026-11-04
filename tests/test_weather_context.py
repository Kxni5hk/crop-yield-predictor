"""Weather schema and network-failure behavior tested without live API requests."""
import unittest
from unittest.mock import patch
import requests
from weather_context import fetch_city_weather, weather_label

class Response:
    def __init__(self, data): self.data = data
    def raise_for_status(self): pass
    def json(self): return self.data

class WeatherTests(unittest.TestCase):
    def test_weather_code_labels(self):
        self.assertEqual(weather_label(0), "Clear sky")
        self.assertEqual(weather_label(61), "Rain / showers")
        self.assertEqual(weather_label(95), "Thunderstorms")

    @patch("weather_context.requests.get")
    def test_city_forecast_parsed(self, get):
        get.side_effect = [
            Response({"results": [{"name":"Jaipur","country":"India","latitude":26.9,"longitude":75.8}]}),
            Response({"timezone":"Asia/Kolkata",
              "current":{"time":"2026-11-04T14:00","temperature_2m":24,"relative_humidity_2m":52,"wind_speed_10m":9,"weather_code":2},
              "daily":{"time":["2026-11-04","2026-11-05"],"temperature_2m_max":[29,30],"temperature_2m_min":[18,19],"precipitation_sum":[0,2]}})
        ]
        info = fetch_city_weather("Jaipur")
        self.assertEqual(info["location"], "Jaipur, India")
        self.assertEqual(info["temperature_c"], 24)
        self.assertEqual(len(info["forecast"]), 2)
        self.assertIn("Precipitation (mm)", info["forecast"][0])
        self.assertEqual(get.call_count, 2)

    @patch("weather_context.requests.get")
    def test_city_not_found(self, get):
        get.return_value = Response({"results":[]})
        with self.assertRaisesRegex(ValueError, "City not found"):
            fetch_city_weather("Unknowncity")

    @patch("weather_context.requests.get")
    def test_network_error_is_not_fatal_to_predictor(self, get):
        get.side_effect = requests.Timeout("timed out")
        with self.assertRaisesRegex(ValueError, "unavailable"):
            fetch_city_weather("Jaipur")

if __name__ == "__main__":
    unittest.main()
