"""Lightweight model-sensitivity scenarios (not SHAP and not causal inference).

Each scenario changes one original input at a time and predicts again with the
already-loaded Random Forest pipeline. No SHAP import, explainer, or model copy.
"""
import numpy as np
import pandas as pd

FEATURES = [
    "Region", "Soil_Type", "Crop", "Rainfall_mm", "Temperature_Celsius",
    "Fertilizer_Used", "Irrigation_Used", "Weather_Condition",
]

ALTERNATIVES = {
    "Region": ("North", "South", "East", "West"),
    "Soil_Type": ("Loam", "Clay", "Sandy", "Silt", "Peaty", "Chalky"),
    "Crop": ("Wheat", "Rice", "Maize", "Barley", "Cotton", "Soybean"),
    "Weather_Condition": ("Sunny", "Cloudy", "Rainy"),
}


def _alternate(feature, value):
    if feature == "Rainfall_mm":
        number = float(value)
        return min(1000.0, number + 50.0) if number < 975.0 else max(100.0, number - 50.0)
    if feature == "Temperature_Celsius":
        number = float(value)
        return min(40.0, number + 1.0) if number < 39.5 else max(15.0, number - 1.0)
    if feature in ("Fertilizer_Used", "Irrigation_Used"):
        return not bool(value)
    for alternative in ALTERNATIVES[feature]:
        if str(alternative) != str(value):
            return alternative
    raise ValueError(f"No alternative defined for {feature}: {value}")


def compare_one_feature_at_a_time(model, row):
    """Return eight what-if predictions, changing exactly one feature per row."""
    if isinstance(row, dict):
        row = pd.DataFrame([row])
    if not isinstance(row, pd.DataFrame) or len(row) != 1:
        raise ValueError("Expected exactly one input row.")
    missing = [feature for feature in FEATURES if feature not in row.columns]
    if missing:
        raise ValueError(f"Missing features: {missing}")
    original = row.loc[:, FEATURES].copy()
    baseline = float(model.predict(original)[0])
    if not np.isfinite(baseline):
        raise ValueError("Non-finite original prediction")

    scenarios = []
    labels = []
    for feature in FEATURES:
        alternate = _alternate(feature, original.iloc[0][feature])
        changed = original.iloc[0].copy()
        changed[feature] = alternate
        scenarios.append(changed)
        labels.append((feature, str(original.iloc[0][feature]), str(alternate)))

    alternative_rows = pd.DataFrame(scenarios, columns=FEATURES).reset_index(drop=True)
    scenario_predictions = np.asarray(model.predict(alternative_rows), dtype=float).reshape(-1)
    if len(scenario_predictions) != len(FEATURES) or not np.isfinite(scenario_predictions).all():
        raise ValueError("Invalid scenario predictions")

    table = pd.DataFrame([
        {
            "Feature changed": feature,
            "Original": before,
            "Alternative": after,
            "Scenario yield (t/ha)": float(pred),
            "Change vs current (t/ha)": float(pred - baseline),
        }
        for (feature, before, after), pred in zip(labels, scenario_predictions)
    ])
    return baseline, table
