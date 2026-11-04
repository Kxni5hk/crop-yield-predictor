# CropCast AI v6 — product workspace navigation and two-model research

## Design delivery

A custom, original agri-tech research workspace built on the existing Streamlit runtime. A fixed-access navigation rail and six launch cards replace the flat seven-tab view. All navigation controls are native Streamlit buttons/radio controls (keyboard accessible), not inert HTML.

- Overview home with illustrated hero, feature launchers, original verified historical model metrics and visual workflows
- Yield Predictor: the existing checksum-verified eight-feature **original Model B** inference
- Crop Scenarios: six crop comparisons and optional one-at-a-time model sensitivity
- Model A Research: true nine-feature Model A metrics, 1M-row Model A/B comparison and crop-wise harvest-duration distributions
- Batch Studio: bounded 50-row upload, real Model B inference and CSV export
- Weather Context: user-requested five-day city weather, never used as trained-model input
- Session History: temporary history, CSV export, delete
- Research & About: model evidence and project limitations

## Crucial ML separation

**Do not claim full-dataset Model A is deployed.** The complete 999,769-row Model A/B comparison was a separately recorded experiment. Model A includes Days_to_Harvest and scored R² 0.911347; B scored R² 0.911109 under the same training parameters. These results do NOT describe the old deployed B artifact, which was trained on the original 50k sample and evaluated on 10k test rows.

A 9-feature full-data-trained Model A research artifact was generated offline with scikit-learn 1.8.0. Production Render uses scikit-learn 1.6.1 and a 512 MiB free plan that previously suffered memory OOM. Both compatibility and memory usage must be validated before enabling Model A inference; no placeholder predictions or fake toggles.

Model A research CSV outputs and detailed methodology reside in the user's Google Drive Crop_Yield_ML_Project/Validation_Reports/Full_Dataset_Evaluation_2026 directory.

## Design inspiration

MotionSites/21st.dev/Lovable were examined for navigation and motion patterns. No proprietary source or UI assets were copied. Original rail CSS, motion accessibility via reduced-motion preferences, responsive sidebar and clickable Streamlit launcher cards provide a coherent product interface within the existing stable Python architecture.

## Acceptance and QA

GitHub Action must pass Python compilation, UI route contracts, dataset comparison validity, validation, weather and other unit tests, and the SHA256-verified original Model B integration test. After merging, confirm Render's deployment and server boot; browser-level keyboard/mobile navigation, model prediction, CSV batch and weather should be checked independently.
