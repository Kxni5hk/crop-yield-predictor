"""Quick scenario tests with a lightweight deterministic mock model."""
import unittest
import numpy as np
import pandas as pd
from sensitivity import FEATURES, compare_one_feature_at_a_time

class MockModel:
    def predict(self, rows):
        return (
            2.5
            + rows["Rainfall_mm"].astype(float).to_numpy() * 0.002
            + rows["Temperature_Celsius"].astype(float).to_numpy() * 0.01
            + rows["Irrigation_Used"].astype(float).to_numpy() * 0.3
        )

class SensitivityTests(unittest.TestCase):
    def setUp(self):
        self.row = {
            "Region": "North", "Soil_Type": "Loam", "Crop": "Wheat",
            "Rainfall_mm": 550.0, "Temperature_Celsius": 27.5,
            "Fertilizer_Used": True, "Irrigation_Used": True,
            "Weather_Condition": "Sunny",
        }

    def test_eight_scenarios_without_modifying_input(self):
        baseline, table = compare_one_feature_at_a_time(MockModel(), self.row)
        self.assertEqual(len(table), len(FEATURES))
        self.assertEqual(self.row["Rainfall_mm"], 550.0)
        self.assertAlmostEqual(baseline, 4.175, places=8)
        rainfall = table.loc[table["Feature changed"] == "Rainfall_mm"].iloc[0]
        self.assertAlmostEqual(rainfall["Change vs current (t/ha)"], 0.1, places=8)
        self.assertTrue(np.isfinite(table["Change vs current (t/ha)"]).all())

    def test_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            compare_one_feature_at_a_time(MockModel(), {"Crop": "Wheat"})
        with self.assertRaises(ValueError):
            compare_one_feature_at_a_time(MockModel(), pd.DataFrame([self.row, self.row]))

if __name__ == "__main__":
    unittest.main()
