"""Research facts from the verified full-million-row holdout experiment.

No inference here. This page must not pretend that Model A is deployed.
The stored production model remains the checksum-verified eight-feature Model B.
"""
from __future__ import annotations

import pandas as pd

SOURCE_DESCRIPTION = (
    "999,769 non-negative-yield records; 799,815 train / 199,954 held-out test; "
    "random_state=42; 100 trees, max_depth=20, min_samples_leaf=2, "
    "max_samples=0.25 per tree."
)

MODELS = [
    {"Model": "A · Harvest-duration research", "Inputs": 9, "R²": 0.9113472304144254,
     "RMSE (t/ha)": 0.5046694514876343, "MAE (t/ha)": 0.40254702688351574,
     "Live availability": "Research only"},
    {"Model": "B · Early-stage scenarios", "Inputs": 8, "R²": 0.9111086793033772,
     "RMSE (t/ha)": 0.5053479896781428, "MAE (t/ha)": 0.40316280401150345,
     "Live availability": "Earlier Model B version live"},
]

HARVEST_DURATION = [
    ("Barley", 166727, 69, 104, 140),
    ("Cotton", 166548, 69, 105, 141),
    ("Maize", 166785, 69, 105, 141),
    ("Rice", 166754, 69, 104, 141),
    ("Soybean", 166315, 68, 105, 140),
    ("Wheat", 166640, 69, 105, 140),
]


def evaluation_table():
    return pd.DataFrame(MODELS)


def harvest_duration_table():
    return pd.DataFrame(
        HARVEST_DURATION,
        columns=["Crop", "Dataset records", "10th percentile (days)",
                 "Median (days)", "90th percentile (days)"],
    )


def model_a_status():
    return (
        "Model A is evaluated on the full dataset but its research artifact is not "
        "deployed in the Render Free service. The current live predictor uses the "
        "original eight-feature Model B trained in the earlier 50k-row experiment. "
        "The 1M-row metrics shown above do not describe that older deployed artifact."
    )
