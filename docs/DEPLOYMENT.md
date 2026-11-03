# CropCast AI — Deployment and Maintenance Guide

**Status:** Public academic prototype (tested working by the project owner on Streamlit Community Cloud).  
**Source:** https://github.com/Kxni5hk/crop-yield-predictor  
**Public app:** `https://cropcast-yield-ai.streamlit.app/`  
**Deployment target:** Streamlit Community Cloud, `main` branch, `app.py` entry point.  
**Last documentation review:** 2026-11-03.

## 1. What this website does

CropCast predicts crop yield in **tons/hectare** from eight user-selected fields: `Region`, `Soil_Type`, `Crop`, `Rainfall_mm`, `Temperature_Celsius`, `Fertilizer_Used`, `Irrigation_Used`, and `Weather_Condition`. A trained **Random Forest Regressor (Model B)** produces the numeric result; the app also provides model-evaluation information and CSV download of a prediction.

This is an **educational research prototype**, not a field-validated agricultural forecasting service. Predictions use hypothetical/scenario values entered by the visitor. No live weather or soil API is currently connected.

## 2. Running deployment architecture

```text
Visitor browser
   ↓
Streamlit Community Cloud (app.py on main)
   ↓  on first inference
GitHub Release v1.0.1 (.joblib model asset)
   ↓
SHA-256 verification → joblib loads trusted model
   ↓
8 inputs → preprocessing + Random Forest → predicted yield (t/ha)
   ↓
Result card / CSV download
```

**Current model release asset (as referenced in the reviewed source):**

`https://github.com/Kxni5hk/crop-yield-predictor/releases/download/v1.0.1/crop_yield_model_b_for_release.joblib`

**Pinned SHA-256:**

`2e3605235e16dd13c382c2c1493e575d4225ad0ee0342f96d22ae5ab358f932b`

The reviewed `app.py` sets the model download URL and checksum directly in the prediction handler. **It does not currently require `MODEL_URL` or `MODEL_SHA256` in Streamlit Secrets for the main prediction path.** Earlier UI messages mentioning Secrets can be misleading after the code-side fix. Don't add or change Secrets unless you intentionally refactor model configuration.

## 3. Re-deploy from GitHub (only when needed)

1. Sign in at https://share.streamlit.io/ with an account authorized for the repository.
2. Create an app from `Kxni5hk/crop-yield-predictor`, branch `main`, main file `app.py`.
3. Select **Python 3.12** in Advanced settings if asked (the app pins `scikit-learn==1.6.1`).
4. Choose an available subdomain; capture its actual final URL. Do not put a GitHub link in the App URL field.
5. Deploy; verify UI opens, the model is fetched, and a prediction is generated.

**Avoid deleting the currently working deployment just to update code.** Streamlit detects commits to `main` and updates the running app. The Python version is a separate deployment setting.

## 4. Local development (Windows)

1. Clone/download the GitHub repository to a folder.
2. Install Python 3.12 and open a terminal inside the repository folder.
3. Create an optional virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The current app downloads the GitHub Release model on first prediction. A trusted `crop_yield_model_b.joblib` placed beside `app.py` is an alternative for local testing. Never run untrusted joblib/pickle files.

## 5. Minimum release QA

- [ ] Website opens in an incognito browser without owner login.
- [ ] All eight inputs appear, with legible labels and mobile-friendly layout.
- [ ] Wheat/Loam/North/550 mm/27.5 °C/Sunny/Fertilizer yes/Irrigation yes yields approximately **6.16 t/ha** with the unchanged model and preprocessing.
- [ ] Different crop choice still returns a finite result.
- [ ] Prediction CSV downloads and contains the selected inputs and yield.
- [ ] Model Performance and About tabs render.
- [ ] New app URL works from GitHub README.
- [ ] No runtime traceback or GitHub model-asset download errors.

Model metrics reported from the project's original random holdout: Model B R² **0.9031**, RMSE **0.5233 t/ha**, MAE **0.4175 t/ha**. These are not independent real-world accuracy guarantees.

## 6. Safe update and troubleshooting

| Symptom | Check |
|---|---|
| Python `IndentationError` | Inspect recent edit in `app.py`; revert bad commit if needed, then recommit syntax-checked code. |
| `MODEL_URL must start with https://` | Confirm running GitHub commit; current reviewed code uses the direct HTTPS release URL. Old code or empty placeholder settings may still be deployed. |
| GitHub 404/model missing | Inspect tag `v1.0.1`, asset spelling, release visibility, and network access. |
| SHA-256 mismatch | Do not disable verification. Confirm the asset is the exact trusted model; if intentionally replaced, review it and update checksum together with the URL. |
| Build fails on scikit-learn | Confirm deployed Python version and pinned `requirements.txt`; match supported versions rather than silently upgrading the trained model environment. |
| Updated app looks unchanged | Verify recent GitHub commit on `main`, check Streamlit deployment logs, then rerun/refresh. |

**Rollback without deleting the app:** Restore the last known-good version of `app.py` using GitHub history/revert; commit to `main`, then verify live behavior. Keep a copy of the known-good commit hash in your project notes.

## 7. Security and data ethics

- Do not commit passwords, API keys, tokens, private farm datasets, or Streamlit `secrets.toml`.
- A `.joblib` file contains pickle serialization; only load known/trusted model artifacts after integrity checks.
- Do not claim actual weather API access, certified forecasting, or farmer-level accuracy until validated.
- Verify original dataset authorship, provenance, permitted use, and proper attribution before redistribution.