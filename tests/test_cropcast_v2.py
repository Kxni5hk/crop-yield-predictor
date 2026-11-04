"""Realistic, lightweight tests for CropCast v2 helpers."""
import unittest
import numpy as np
import pandas as pd
from cropcast_v2 import (
    CROPS, validate_conditions, model_input_frame,
    compare_supported_crops, calculate_area_estimate, prediction_record,
)


class MockModel:
    def predict(self, rows):
        return (
            2.0 +
            rows["Rainfall_mm"].astype(float).to_numpy() * 0.002 +
            rows["Temperature_Celsius"].astype(float).to_numpy() * 0.01 +
            rows["Irrigation_Used"].astype(float).to_numpy() * 0.3 +
            rows["Crop"].map({crop: i * 0.05 for i, crop in enumerate(CROPS)}).to_numpy()
        )


class CropCastV2Tests(unittest.TestCase):
    def setUp(self):
        self.row = dict(
            Region="North", Soil_Type="Loam", Crop="Wheat",
            Rainfall_mm=550.0, Temperature_Celsius=27.5,
            Fertilizer_Used=True, Irrigation_Used=True,
            Weather_Condition="Sunny"
        )

    def test_validation_keeps_eight_columns_in_order(self):
        frame = model_input_frame(self.row)
        self.assertEqual(frame.shape, (1, 8))
        self.assertEqual(frame["Crop"].iloc[0], "Wheat")

    def test_validation_rejects_bad_inputs(self):
        for field, invalid in [
            ("Crop", "Banana"), ("Rainfall_mm", float("nan")),
            ("Rainfall_mm", 1001), ("Temperature_Celsius", 7),
            ("Irrigation_Used", "yes"),
        ]:
            with self.subTest(field=field):
                data = dict(self.row)
                data[field] = invalid
                with self.assertRaises(ValueError):
                    validate_conditions(data)

    def test_crop_comparison_matches_actual_model_calls(self):
        table = compare_supported_crops(MockModel(), self.row)
        self.assertEqual(len(table), 6)
        self.assertEqual(set(table["Crop"]), set(CROPS))
        self.assertTrue(np.isfinite(table["Estimated yield (t/ha)"]).all())
        chosen = table.set_index("Crop").loc["Wheat", "Estimated yield (t/ha)"]
        actual = float(MockModel().predict(pd.DataFrame([self.row]))[0])
        self.assertAlmostEqual(chosen, actual, places=9)

    def test_area_conversion(self):
        one = calculate_area_estimate(6.16, 1, "hectares")
        acres = calculate_area_estimate(6.16, 2.471053814671653, "acres")
        self.assertAlmostEqual(one["production_tonnes"], 6.16)
        self.assertAlmostEqual(acres["production_tonnes"], 6.16)
        with self.assertRaises(ValueError):
            calculate_area_estimate(6.16, -1, "hectares")

    def test_session_record(self):
        record = prediction_record(self.row, 6.16)
        self.assertEqual(record["Crop"], "Wheat")
        self.assertEqual(record["Model"], "Random Forest Model B v1.0.1")


if __name__ == "__main__":
    unittest.main()
