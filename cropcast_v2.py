"""Small, memory-conscious helpers for the CropCast AI v2 public demo.

No model is loaded here: each caller reuses the existing cached Model B pipeline.
"""
from __future__ import annotations

from datetime import datetime, timezone
import numpy as np
import pandas as pd

FEATURE_COLUMNS = (
    "Region", "Soil_Type", "Crop", "Rainfall_mm", "Temperature_Celsius",
    "Fertilizer_Used", "Irrigation_Used", "Weather_Condition",
)
CROPS = ("Wheat", "Rice", "Maize", "Barley", "Cotton", "Soybean")
SOILS = ("Loam", "Clay", "Sandy", "Silt", "Peaty", "Chalky")
REGIONS = ("North", "South", "East", "West")
WEATHER = ("Sunny", "Cloudy", "Rainy")


def validate_conditions(inputs: dict) -> dict:
    """Return validated model inputs in model feature order, without silent coercions."""
    if not isinstance(inputs, dict):
        raise ValueError("Farm conditions must be a dictionary.")
    missing = [name for name in FEATURE_COLUMNS if name not in inputs]
    if missing:
        raise ValueError("Missing inputs: " + ", ".join(missing))
    validated = {name: inputs[name] for name in FEATURE_COLUMNS}
    for name, choices in (
        ("Region", REGIONS), ("Soil_Type", SOILS),
        ("Crop", CROPS), ("Weather_Condition", WEATHER),
    ):
        if validated[name] not in choices:
            raise ValueError(f"Unsupported {name}: {validated[name]}")
    for name, lower, upper in (
        ("Rainfall_mm", 100.0, 1000.0),
        ("Temperature_Celsius", 15.0, 40.0),
    ):
        try:
            number = float(validated[name])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be numeric.") from exc
        if not np.isfinite(number) or not lower <= number <= upper:
            raise ValueError(f"{name} must be between {lower:g} and {upper:g}.")
        validated[name] = number
    for name in ("Fertilizer_Used", "Irrigation_Used"):
        if not isinstance(validated[name], (bool, np.bool_)):
            raise ValueError(f"{name} must be Yes or No.")
        validated[name] = bool(validated[name])
    return validated


def model_input_frame(inputs: dict) -> pd.DataFrame:
    return pd.DataFrame([validate_conditions(inputs)], columns=FEATURE_COLUMNS)


def compare_supported_crops(model, inputs: dict) -> pd.DataFrame:
    """Compare actual Model B predictions for all six supported crops.

    This is model response to a changed Crop input, NOT agronomic suitability.
    """
    basic = validate_conditions(inputs)
    scenarios = [{**basic, "Crop": crop} for crop in CROPS]
    frame = pd.DataFrame(scenarios, columns=FEATURE_COLUMNS)
    predictions = np.asarray(model.predict(frame), dtype=float).reshape(-1)
    if len(predictions) != len(CROPS) or not np.isfinite(predictions).all():
        raise ValueError("Model returned invalid crop-comparison values.")
    return pd.DataFrame({
        "Crop": list(CROPS),
        "Estimated yield (t/ha)": predictions,
        "Estimated yield (kg/ha)": predictions * 1000.0,
    }).sort_values("Estimated yield (t/ha)", ascending=False).reset_index(drop=True)


def calculate_area_estimate(yield_t_per_ha: float, area: float, unit: str):
    """Unit conversion only, not a second model prediction."""
    value = float(yield_t_per_ha)
    amount = float(area)
    if not np.isfinite(value) or not np.isfinite(amount) or amount <= 0 or amount > 1_000_000:
        raise ValueError("Yield must be finite, and land area must be positive and realistic.")
    if unit == "hectares":
        hectares = amount
    elif unit == "acres":
        hectares = amount / 2.471053814671653
    else:
        raise ValueError("Area unit must be hectares or acres.")
    return {"area_hectares": hectares, "production_tonnes": value * hectares, "production_kg": value * hectares * 1000.0}


def prediction_record(inputs: dict, predicted_yield: float) -> dict:
    conditions = validate_conditions(inputs)
    value = float(predicted_yield)
    if not np.isfinite(value):
        raise ValueError("Non-finite yield.")
    return {
        "Time (UTC)": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        **conditions,
        "Predicted yield (t/ha)": value,
        "Model": "Random Forest Model B v1.0.1",
    }
