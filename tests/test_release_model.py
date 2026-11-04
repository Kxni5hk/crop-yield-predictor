"""Integration check against the checksum-verified public CropCast model release.

Run explicitly: python tests/test_release_model.py MODEL_PATH
Only load the owner's trusted release asset after verifying its SHA-256.
"""
import hashlib
import sys
from pathlib import Path
import joblib
import pandas as pd

from explainability import explain_prediction
from sensitivity import compare_one_feature_at_a_time
from cropcast_v2 import compare_supported_crops

EXPECTED_SHA256 = "2e3605235e16dd13c382c2c1493e575d4225ad0ee0342f96d22ae5ab358f932b"


def main(model_path):
    path = Path(model_path)
    with path.open("rb") as model_file:
        digest = hashlib.file_digest(model_file, "sha256").hexdigest()
    assert digest == EXPECTED_SHA256, "Release model SHA256 mismatch"

    model = joblib.load(path)
    example = pd.DataFrame([{
        "Region": "North",
        "Soil_Type": "Loam",
        "Crop": "Wheat",
        "Rainfall_mm": 550.0,
        "Temperature_Celsius": 27.5,
        "Fertilizer_Used": True,
        "Irrigation_Used": True,
        "Weather_Condition": "Sunny",
    }])

    prediction = float(model.predict(example)[0])
    explanation = explain_prediction(model, example)
    assert abs(explanation["prediction"] - prediction) < 1e-8
    assert explanation["reconstruction_error"] < 0.01
    assert len(explanation["table"]) == 8
    sensitivity_baseline, scenario_table = compare_one_feature_at_a_time(model, example)
    assert abs(sensitivity_baseline - prediction) < 1e-8
    assert len(scenario_table) == 8
    assert scenario_table["Change vs current (t/ha)"].notna().all()
    crop_table = compare_supported_crops(model, example.iloc[0].to_dict())
    assert len(crop_table) == 6
    wheat = crop_table.set_index("Crop").loc["Wheat", "Estimated yield (t/ha)"]
    assert abs(float(wheat) - prediction) < 1e-8
    print("PASS: six-crop comparison on real saved Model B")
    print("PASS: lightweight sensitivity on real Model B")
    print("PASS: real saved model prediction:", prediction)
    print("PASS: reconstruction error:", explanation["reconstruction_error"])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python tests/test_release_model.py /path/to/model.joblib")
    main(sys.argv[1])
