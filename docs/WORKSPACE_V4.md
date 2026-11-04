# CropCast AI — Advanced Public Workspace v4

## New verified features

- **Bulk Prediction Studio:** Download a CSV template, upload up to 50 farm-condition scenarios (max 128 KiB), validate each row, perform authentic batch inference with the existing checksum-verified Model B, see invalid row explanations, and export the predictions to CSV. The app does not store the uploaded CSV on disk or in a user database.
- **Weather Context:** Optional manually entered city lookup using Open-Meteo geocoding and current weather/5-day daily forecast. Explicitly kept separate from Model B's eight training variables. The five-day forecast is **not** equivalent to seasonal rainfall.
- **Existing features retained:** Premium responsive agri-tech UI, 8-field prediction, crop comparisons, lightweight sensitivity, area conversion, session-only history, CSV exports, evaluation and model limitations.

## Environment and privacy

- Uses the existing requests, pandas, NumPy, scikit-learn, Streamlit dependencies; no new dependency or model file.
- Only the user-entered city is transmitted to a third-party weather endpoint when they choose to fetch data. Open-Meteo's license, attribution and usage restrictions must be respected.
- If the weather API fails, the model prediction and other tools continue working.
- Dataset provenance is not independently verified; experimental model estimates are not crop suitability or financial advice.
- Render Free has a 512 MiB memory limit and previously experienced OOM events. No heavy SHAP runs are added to the website.
- Uploads are limited by the batch app to 50 rows and 128 KiB. Avoid uploading private user information.

## Accounts/authentication

Secure login and permanent prediction history require a configured identity provider and database. They are **not implemented** here. Do not add fake login controls or claim that session history is permanent.

## Release gates

1. GitHub Action: syntax compilation; unit tests; model SHA-256 verification; actual Model B prediction.
2. After merge, Render deployment must be Live.
3. Browser interactions (batch upload/export, city forecast, mobile UI) must be checked on the actual hosted site; successful build alone does not prove them.

## Design sources

Original CSS/Streamlit visual system inspired by contemporary product design principles. No proprietary source code from MotionSites or 21st.dev was copied.
