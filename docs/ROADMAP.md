# CropCast AI — Advanced Development Roadmap

**Purpose:** Turn a working educational ML demo into a more reliable research prototype, then optionally into a usable agricultural decision-support product. **This is a plan, not a list of features already implemented.**

## Phase 0 — Preserve the working version (now)

- Record current live URL, known-good GitHub commit, model release tag `v1.0.1`, SHA-256 checksum, and runtime Python/scikit-learn versions.
- Save one known-good desktop/mobile screenshot and one successful prediction CSV (without private user information).
- Add simple smoke tests for model loading and finite, numeric predictions. Keep all tests off the production model's public URL as much as possible.

**Acceptance:** Working app remains accessible and one-click rollback instructions exist.

## Phase 1 — Data integrity and honest evaluation (highest priority)

1. Identify the exact Kaggle dataset page, license, and whether records are simulated, synthetic, or field-observed.
2. Audit duplicated or near-duplicated records, target leakage, outliers, feature types and time-of-prediction availability.
3. Introduce separate train / validation / untouched final-test partitions; do not repeatedly tune on test data.
4. If date and location identifiers exist, evaluate held-out seasons/farms/regions using proper group/time splits. If unavailable, explicitly state that the dataset cannot support such tests.
5. Report overall and crop-specific RMSE/MAE/R² and confidence/uncertainty limits; compare to simple baselines.

**Acceptance:** Reproducible evaluation notebook + transparent limitations + no unsupported real-world accuracy claims.

## Phase 2 — Explainable and robust predictions

- Show feature contribution explanations (e.g., permutation importance or SHAP) carefully, describing association rather than causation.
- Warn on out-of-training-range inputs and unknown categories. Preserve measurement units.
- Explore calibrated prediction intervals using proper validation methods, not guessed ± percentages.
- Add automated tests for feature order, pipeline compatibility, file integrity, and CSV export.

**Acceptance:** A visitor sees the prediction, a clear uncertainty/limitations note, and meaningful input validation.

## Phase 3 — Weather and soil integration

- Add a reliable weather source for **forecast scenarios** with location/date, units, source, and update timestamp.
- Provide manual override and a visible distinction between historical measured weather, forecast weather, and user-selected hypothetical scenarios.
- Add farmer-provided soil test readings only if data and training features support them. Do not inject unsupported fields into the existing model and claim they affect predictions.
- Retrain and independently re-evaluate the model when feature schema or data sources change.

**Acceptance:** Source and forecast horizon are visible; no misleading 'automatic accuracy' claims.

## Phase 4 — Product engineering and responsible piloting

- Modularize application into `app.py`, `model_loader.py`, `predictor.py`, `tests/`, and docs.
- Add GitHub Actions lint/unit tests and versioned release notes, with no secrets in public logs.
- Add uptime checks and privacy-safe error logs; do not collect users' personal farm data unnecessarily.
- Test accessibility, smaller screens, weak internet, and Hindi/English UI labels.
- Run an expert-reviewed small pilot with permission and explicitly document when model predictions are unreliable.

**Acceptance:** Reliable, maintainable service with a documented field-validation and user-feedback process.

## Priority order (do not skip)

1. Dataset source + license confirmation.
2. Independent/generalization validation.
3. Regression and smoke tests.
4. Clear uncertainty and out-of-range handling.
5. External forecast integration only after testing feature suitability.
6. Scale features (accounts, dashboards, APIs) **after** accuracy and data provenance are addressed.

## Avoid misleading marketing

Don't describe the current random-split R² of 0.9031 as '90.31% accurate on real farms'. The current model is a **proof of concept** and cannot guarantee harvest yield. Real agricultural decisions should involve local agronomy expertise and measured field conditions.