"""Smoke tests for CropCast's SHAP module (synthetic data only)."""
import unittest
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from explainability import FEATURES, explain_prediction


class ExplainabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng = np.random.default_rng(41)
        size = 180
        cls.x = pd.DataFrame({
            "Region": rng.choice(["North", "South", "East", "West"], size),
            "Soil_Type": rng.choice(["Loam", "Clay", "Sandy"], size),
            "Crop": rng.choice(["Wheat", "Rice", "Maize"], size),
            "Rainfall_mm": rng.uniform(100, 1000, size),
            "Temperature_Celsius": rng.uniform(15, 40, size),
            "Fertilizer_Used": rng.choice([True, False], size),
            "Irrigation_Used": rng.choice([True, False], size),
            "Weather_Condition": rng.choice(["Sunny", "Rainy", "Cloudy"], size),
        })[FEATURES]
        target = (3 + cls.x["Rainfall_mm"] * 0.002
                  - cls.x["Temperature_Celsius"] * 0.012
                  + cls.x["Irrigation_Used"].astype(int) * 0.5)
        numeric = ["Rainfall_mm", "Temperature_Celsius"]
        categorical = [col for col in FEATURES if col not in numeric]
        preprocessing = ColumnTransformer([
            ("num", "passthrough", numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ])
        cls.model = Pipeline([
            ("preprocessor", preprocessing),
            ("regressor", RandomForestRegressor(
                n_estimators=12, max_depth=8, random_state=41, n_jobs=1)),
        ]).fit(cls.x, target)

    def test_explanation_reconstructs_prediction(self):
        explanation = explain_prediction(self.model, self.x.iloc[[0]])
        expected = float(self.model.predict(self.x.iloc[[0]])[0])
        self.assertAlmostEqual(explanation["prediction"], expected, places=6)
        self.assertLess(explanation["reconstruction_error"], 0.01)
        self.assertEqual(set(explanation["table"]["Feature"]), set(FEATURES))
        self.assertEqual(len(explanation["table"]), 8)

    def test_missing_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            explain_prediction(self.model, {"Crop": "Wheat"})

    def test_multiple_rows_are_rejected(self):
        with self.assertRaises(ValueError):
            explain_prediction(self.model, self.x.iloc[:2])


if __name__ == "__main__":
    unittest.main()
