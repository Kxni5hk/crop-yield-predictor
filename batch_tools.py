"""Validated, resource-bounded CSV inference for the public CropCast demo.

Uploaded bytes are processed in memory, never written to disk or to a
database. The caller passes the existing, checksum-verified cached Model B.
"""
from __future__ import annotations

from io import BytesIO
import numpy as np
import pandas as pd

from cropcast_v2 import FEATURE_COLUMNS, validate_conditions

MAX_CSV_BYTES = 128 * 1024
MAX_CSV_ROWS = 50

EXAMPLES = [
    {
        "Region": "North", "Soil_Type": "Loam", "Crop": "Wheat",
        "Rainfall_mm": 550, "Temperature_Celsius": 27.5,
        "Fertilizer_Used": True, "Irrigation_Used": True,
        "Weather_Condition": "Sunny",
    },
    {
        "Region": "South", "Soil_Type": "Clay", "Crop": "Rice",
        "Rainfall_mm": 750, "Temperature_Celsius": 30,
        "Fertilizer_Used": True, "Irrigation_Used": False,
        "Weather_Condition": "Rainy",
    },
]


def csv_template() -> bytes:
    """Two clearly illustrative rows. No fake prediction outputs."""
    return pd.DataFrame(EXAMPLES, columns=FEATURE_COLUMNS).to_csv(index=False).encode("utf-8")


def _bool(value, name):
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if pd.isna(value):
        raise ValueError(f"{name} is missing.")
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    text = str(value).strip().lower()
    if text in ("true", "yes", "1"):
        return True
    if text in ("false", "no", "0"):
        return False
    raise ValueError(f"{name} must be true/false or yes/no.")


def read_validated_csv(blob: bytes):
    """Return a validated input DataFrame plus row-level validation errors."""
    if not isinstance(blob, bytes) or not blob:
        raise ValueError("Upload a nonempty CSV file.")
    if len(blob) > MAX_CSV_BYTES:
        raise ValueError("CSV exceeds 128 KB. Please use at most 50 rows.")
    try:
        raw = pd.read_csv(BytesIO(blob), encoding="utf-8-sig")
    except (UnicodeError, pd.errors.ParserError, ValueError) as exc:
        raise ValueError("Could not read UTF-8 CSV. Check the template and file encoding.") from exc
    if raw.empty or len(raw) > MAX_CSV_ROWS:
        raise ValueError("CSV must contain between 1 and 50 data rows.")
    missing = [col for col in FEATURE_COLUMNS if col not in raw.columns]
    if missing:
        raise ValueError("CSV is missing required columns: " + ", ".join(missing))

    accepted, row_numbers, errors = [], [], []
    for i, raw_row in enumerate(raw.to_dict(orient="records"), start=2):
        try:
            item = {name: raw_row[name] for name in FEATURE_COLUMNS}
            item["Fertilizer_Used"] = _bool(item["Fertilizer_Used"], "Fertilizer_Used")
            item["Irrigation_Used"] = _bool(item["Irrigation_Used"], "Irrigation_Used")
            validated = validate_conditions(item)
            accepted.append(validated)
            row_numbers.append(i)
        except (ValueError, TypeError, KeyError) as exc:
            errors.append({"CSV line": i, "Validation problem": str(exc)})
    frame = pd.DataFrame(accepted, columns=FEATURE_COLUMNS)
    if frame.empty:
        frame = pd.DataFrame(columns=FEATURE_COLUMNS)
    return frame, row_numbers, pd.DataFrame(errors, columns=["CSV line", "Validation problem"])


def predict_csv_batch(model, blob: bytes):
    """Return actual model results and explicit rejected rows."""
    frame, row_numbers, errors = read_validated_csv(blob)
    if frame.empty:
        return pd.DataFrame(columns=["CSV line", *FEATURE_COLUMNS, "Predicted yield (t/ha)"]), errors
    predicted = np.asarray(model.predict(frame), dtype=float).reshape(-1)
    if len(predicted) != len(frame) or not np.isfinite(predicted).all():
        raise ValueError("Model returned non-finite or incomplete predictions.")
    results = frame.copy()
    results.insert(0, "CSV line", row_numbers)
    results["Predicted yield (t/ha)"] = predicted
    results["Predicted yield (kg/ha)"] = predicted * 1000.0
    return results, errors
