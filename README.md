# 🌾 CropCast AI — Crop Yield Prediction

A public educational machine-learning website that estimates crop yield under user-selected agricultural conditions. Built with **Python, Streamlit, and a trained scikit-learn Random Forest Regressor**.

## 🌐 Live website

**[Open CropCast AI](https://cropcast-yield-ai.streamlit.app/)**

> **URL maintenance:** This is the original verified public URL. If the Streamlit subdomain is renamed in **App settings → General → App URL**, update the link above to your *actual new working URL*.

## ✅ Features

- Interactive inputs for **crop**, **soil type**, **region**, **rainfall**, **temperature**, **weather condition**, **fertilizer use**, and **irrigation use**.
- Crop yield prediction in **tons per hectare** and **kg per hectare** using the trained model (not hardcoded output).
- A performance tab with comparison of two model variants and error plots.
- An explanation of the project pipeline, model assumptions, and limitations.
- CSV export of prediction inputs and results.
- Dark, responsive UI with improved high-contrast labels and navigation tabs.

## 🧠 ML approach

- **Learning task:** Supervised regression
- **Algorithm:** Random Forest Regressor
- **Target:** `Yield_tons_per_hectare`
- **Original records loaded:** 336,776 (10 columns)
- **Records after excluding negative targets:** 336,698
- **Development sample:** 50,000 rows
- **Training/test split:** 40,000 / 10,000 (random split)
- **Model A:** 9 features, including `Days_to_Harvest`
- **Model B (deployed):** 8 features; excludes `Days_to_Harvest`

### Evaluation on the held-out random test split

| Metric | Model A | Model B (website) |
|---|---:|---:|
| RMSE (tons/hectare) | 0.5211 | 0.5233 |
| MAE (tons/hectare) | 0.4156 | 0.4175 |
| R² | 0.9039 | 0.9031 |

These values come from the original project experiment. **R² is not the same as percentage prediction accuracy**, and scores from a random split do not establish performance on new farms or future seasons.

## 🛠️ Technology

- Python, pandas, NumPy
- scikit-learn 1.6.1 (model serialization compatibility)
- Streamlit Community Cloud
- GitHub Releases for the large trusted `.joblib` model asset

## 📁 Repository layout

```text
crop-yield-predictor/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── assets/
│   ├── model_comparison.csv
│   ├── crop_wise_performance.png
│   └── residual_analysis.png
└── .streamlit/
    └── config.toml
```

## 🚀 Run locally

Use a Python version compatible with the pinned dependencies (for example Python 3.12).

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The deployed `app.py` downloads the trusted pretrained Model B from the pinned public GitHub Release `v1.0.1` on first inference, checks its SHA-256, then loads it with `joblib`. A local test can also load a trusted file called `crop_yield_model_b.joblib` placed beside `app.py`.

**Model release:** [CropCast Model B v1.0.1](https://github.com/Kxni5hk/crop-yield-predictor/releases/tag/v1.0.1)

> Never load `.joblib` files from untrusted sources. The model contains Python pickle data. Avoid uploading raw private farm or user data to the public repository.

## ⚠️ Limitations & responsible use

This is an **academic research prototype**, not a certified agricultural forecasting system. The dataset's original provenance and field realism still require independent verification. Rainfall and temperature values are inputs or scenarios, not automatically retrieved weather forecasts. The model has **not been independently validated** on new farms, climates, or growing seasons. Do not use it as the sole basis for crop-management or financial decisions.

## 📌 Roadmap

- Confirm and cite original Kaggle dataset source and license
- Evaluate generalization on independent seasons and regions
- Integrate reliable weather forecasts and soil measurements
- Add documented prediction uncertainty and model monitoring

---

**Project:** CropCast AI · Crop Yield Prediction Research Prototype
