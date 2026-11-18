"""Weather schema and network-failure behavior tested without live API requests."""
import unittest
from unittest.mock import patch
import requests
import weather_context
from weather_context import fetch_city_weather, weather_label

class Response:
    def __init__(self, data, status=200, headers=None):
        self.data = data
        self.status_code = status
        self.headers = headers or {}
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)
    def json(self): return self.data

class WeatherTests(unittest.TestCase):
    def setUp(self):
        weather_context._forecast_blocked_until = 0.0
        weather_context._met_cache.clear()

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


    @patch("weather_context.time.sleep")
    @patch("weather_context.requests.get")
    def test_429_includes_retry_after_without_extra_requests(self, get, sleep):
        get.return_value = Response({}, status=429, headers={"Retry-After": "60"})
        with self.assertRaisesRegex(ValueError, "429.*60 seconds"):
            fetch_city_weather("Jaipur")
        self.assertEqual(get.call_count, 1)
        sleep.assert_not_called()

    @patch("weather_context.time.sleep")
    @patch("weather_context.requests.get")
    def test_transient_503_recovers(self, get, sleep):
        location = {"results": [{"name":"Jaipur","country":"India","latitude":26.9,"longitude":75.8}]}
        forecast = {"timezone":"Asia/Kolkata",
            "current":{"time":"2026-11-04T14:00","temperature_2m":24,
                       "relative_humidity_2m":52,"wind_speed_10m":9,"weather_code":2},
            "daily":{"time":["2026-11-04"],"temperature_2m_max":[29],
                     "temperature_2m_min":[18],"precipitation_sum":[0]}}
        get.side_effect = [Response({}, status=503), Response(location), Response(forecast)]
        self.assertEqual(fetch_city_weather("Jaipur")["location"], "Jaipur, India")
        self.assertEqual(get.call_count, 3)
        sleep.assert_called_once()

    @patch("weather_context.requests.get")
    def test_malformed_provider_json(self, get):
        get.return_value = Response(["unexpected", "list"])
        with self.assertRaisesRegex(ValueError, "malformed"):
            fetch_city_weather("Jaipur")


    @patch("weather_context.requests.get")
    def test_forecast_rate_limit_uses_met_norway_with_attribution(self, get):
        geo = {"results":[{"name":"Rohtak","admin1":"Haryana","country":"India",
                           "latitude":28.89,"longitude":76.58,"timezone":"Asia/Kolkata"}]}
        series = []
        for i in range(5):
            series.append({
                "time": f"2026-11-{18+i:02d}T00:00:00Z",
                "data": {
                    "instant":{"details":{"air_temperature":23+i, "relative_humidity":55,
                                          "wind_speed":3.0}},
                    "next_6_hours":{"details":{"precipitation_amount":i*0.5},
                                    "summary":{"symbol_code":"partlycloudy_day"}},
                }
            })
        backup = {"properties":{"timeseries":series}}
        get.side_effect = [
            Response(geo),
            Response({}, status=429, headers={"Retry-After": "22163"}),
            Response(backup),
            Response(geo),
        ]
        result = fetch_city_weather("Rohtak")
        self.assertTrue(result["backup_source"])
        self.assertIn("MET Norway", result["source"])
        self.assertEqual(result["location"], "Rohtak, Haryana, India")
        self.assertEqual(result["wind_kmh"], 10.8)
        self.assertEqual(len(result["forecast"]), 5)
        self.assertEqual(get.call_count, 3)
        self.assertEqual(get.call_args.kwargs["headers"]["User-Agent"],
                         weather_context.MET_USER_AGENT)
        self.assertEqual(get.call_args.kwargs["params"], {"lat":28.89,"lon":76.58})

        # The next lookup must respect the Open-Meteo Retry-After window,
        # and the MET Norway Expires cache: no extra forecast HTTP requests.
        next_result = fetch_city_weather("Rohtak")
        self.assertEqual(next_result["source"], result["source"])
        self.assertEqual(get.call_count, 4)

    @patch("weather_context.requests.get")
    def test_backup_failure_reports_both_sources_unavailable(self, get):
        geo = {"results":[{"name":"Jaipur","country":"India","latitude":26.9,
                           "longitude":75.8,"timezone":"Asia/Kolkata"}]}
        get.side_effect = [
            Response(geo),
            Response({}, status=429, headers={"Retry-After": "120"}),
            Response({}, status=503),
        ]
        with self.assertRaisesRegex(ValueError, "Both forecast services"):
            fetch_city_weather("Jaipur")
        self.assertEqual(get.call_count, 3)

    @patch("weather_context.requests.get")
    def test_backup_missing_required_days_is_not_fake_success(self, get):
        geo = {"results":[{"name":"Jaipur","country":"India","latitude":26.9,
                           "longitude":75.8,"timezone":"Asia/Kolkata"}]}
        one_hour = {"properties":{"timeseries":[{
            "time": "2026-11-18T00:00:00Z",
            "data":{"instant":{"details":{"air_temperature":25,
                                          "relative_humidity":50,"wind_speed":2}}}
        }]}}
        get.side_effect = [
            Response(geo),
            Response({}, status=429, headers={"Retry-After": "3600"}),
            Response(one_hour),
        ]
        with self.assertRaisesRegex(ValueError, "fewer than five"):
            fetch_city_weather("Jaipur")


if __name__ == "__main__":
    unittest.main()
