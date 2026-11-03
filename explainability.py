"""SHAP explanations for CropCast Model B predictions."""
import numpy as np
import pandas as pd
import shap

FEATURES = [
    "Region", "Soil_Type", "Crop", "Rainfall_mm", "Temperature_Celsius",
    "Fertilizer_Used", "Irrigation_Used", "Weather_Condition",
]


def explain_prediction(model, input_row):
    """Explain one prediction; SHAP values are model attributions, not causal effects."""
    if isinstance(input_row, dict):
        input_row = pd.DataFrame([input_row])
    if not isinstance(input_row, pd.DataFrame) or len(input_row) != 1:
        raise ValueError("Provide one input row as a DataFrame or dictionary.")
    missing = [col for col in FEATURES if col not in input_row.columns]
    if missing:
        raise ValueError(f"Missing input features: {missing}")
    x = input_row[FEATURES].copy()

    preprocessor = model[:-1]
    forest = model.steps[-1][1]
    encoded = preprocessor.transform(x)
    if hasattr(encoded, "toarray"):
        encoded = encoded.toarray()
    encoded = np.asarray(encoded)
    names = list(preprocessor.get_feature_names_out())
    if encoded.shape != (1, len(names)):
        raise ValueError("Transformed input and feature names do not match.")

    explainer = shap.TreeExplainer(
        forest, feature_perturbation="tree_path_dependent"
    )
    values = np.asarray(explainer.shap_values(encoded))
    if values.ndim == 3 and values.shape[-1] == 1:
        values = values[:, :, 0]
    if values.shape != encoded.shape:
        raise ValueError(f"Unexpected SHAP output shape: {values.shape}")

    baseline = float(np.asarray(explainer.expected_value).reshape(-1)[0])
    prediction = float(model.predict(x)[0])
    contributions = {feature: 0.0 for feature in FEATURES}

    for encoded_name, value in zip(names, values[0]):
        clean = str(encoded_name).split("__", 1)[-1]
        matches = [
            feature for feature in FEATURES
            if clean == feature or clean.startswith(feature + "_")
        ]
        if not matches:
            raise ValueError(f"Unmapped encoded feature: {encoded_name}")
        original_feature = max(matches, key=len)
        contributions[original_feature] += float(value)

    reconstruction_error = abs(prediction - (baseline + sum(contributions.values())))
    if not np.isfinite(reconstruction_error) or reconstruction_error > 0.01:
        raise ValueError(f"SHAP reconstruction check failed: {reconstruction_error:.6f}")

    rows = []
    for feature, value in contributions.items():
        rows.append({
            "Feature": feature,
            "Input": str(x.iloc[0][feature]),
            "Contribution (t/ha)": value,
            "Absolute impact": abs(value),
        })
    table = pd.DataFrame(rows).sort_values(
        "Absolute impact", ascending=False
    ).reset_index(drop=True)

    return {
        "prediction": prediction,
        "baseline": baseline,
        "reconstruction_error": reconstruction_error,
        "table": table,
    }
