# CropCast AI v2 — Tested Public Dashboard Extension

This release adds a **public, no-login** dashboard extension to the existing Streamlit application. It does **not** retrain the Random Forest pipeline or change the trusted Model B release checksum.

## New demonstrated features

- Strict eight-input validation shared with Model B.
- Multi-crop experimental comparison using the *actual same saved model* (six supported crops, other inputs fixed).
- Downloadable crop-comparison CSV.
- Optional area-based production arithmetic in hectares or acres (not an additional ML model).
- Session-only prediction history (up to 25 records) with CSV export and clear control.
- Dedicated navigation tabs for comparison and history.
- Existing sensitivity analysis, performance charts, base predictions and original research explainability code remain.

## Important limitations

- The session history is not an authenticated account or a persistent database. It may disappear on refresh, service restart, or session expiration.
- No real sign-in, user profiles, password management or cloud database has been configured. These must **not** be represented as implemented.
- No live weather or climate API is included.
- Crop comparison estimates are only predictions generated when changing the Crop input. They are **not** verified suitability, profitability, fertilizer, water-use or crop-management advice.
- Dataset provenance and generalization to real-world future seasons remain unverified.
- Deployment on Render Free is resource-constrained (approximately 512 MB); avoid interactive SHAP or loading the full training dataset.

## Validation

Tests under `tests/test_cropcast_v2.py` check schema validation, actual model-call semantics using a controlled mock, unit conversions, and session-record structure.

The release-model test downloads the owner's signed-off Model B asset, verifies its SHA-256, and checks that crop comparison for Wheat matches a direct model prediction using the same inputs.

GitHub Actions is the release gate. Review the workflow outcome before merging into `main`. After merge, verify the Render deployment, prediction UI, export, memory behavior and public accessibility.

## Google Colab notebook

A separate development notebook named `Crop_Yield_Prediction_Random_Forest_V2_Development.ipynb` has been saved in the Google Drive `Colab Notebooks` folder. Its original 91 cells are preserved and five development/verification cells appended. Colab execution and GitHub/Render deployment are separate processes. The new cells are for read-only source audit and tests; they do not modify the original experiment.

## Additional requirements for secure accounts

To build login, durable history and multi-user dashboards, configure an OIDC identity provider and a managed persistence service with server-side authorization. Implement only after credentials and access controls are available, and verify users cannot access one another's saved predictions. Do not put secrets into Colab notebooks, source files or GitHub.
