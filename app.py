"""CropCast | ML crop-yield predictor. Run with streamlit run app.py.

This project provides a public educational demonstration. It loads a trusted,
user-supplied scikit-learn model from the local filesystem or a release asset.
"""
from pathlib import Path
import hashlib
import os
import tempfile

import joblib
import numpy as np
import pandas as pd
import requests
import streamlit as st
from cropcast_v2 import (model_input_frame, compare_supported_crops,
    calculate_area_estimate, prediction_record)

st.set_page_config(
    page_title="CropCast | AI Yield Intelligence",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).resolve().parent
LOCAL_MODEL = ROOT / "crop_yield_model_b.joblib"
CACHE_PATH = Path(tempfile.gettempdir()) / "cropcast_model_b_v1.joblib"
FEATURES = [
    "Region", "Soil_Type", "Crop", "Rainfall_mm", "Temperature_Celsius",
    "Fertilizer_Used", "Irrigation_Used", "Weather_Condition",
]

# These values are read from the provided crop-yield CSV's categorical columns.
REGIONS = ["North", "South", "East", "West"]
SOILS = ["Loam", "Clay", "Sandy", "Silt", "Peaty", "Chalky"]
CROPS = ["Wheat", "Rice", "Maize", "Barley", "Cotton", "Soybean"]
WEATHER = ["Sunny", "Cloudy", "Rainy"]

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
:root { color-scheme: dark; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: linear-gradient(150deg,#08151a 1%,#101d21 47%,#0a161a 100%); color: #e7f2eb; }
.block-container { padding-top: 2rem; max-width: 1250px; padding-bottom: 3rem; }
[data-testid="stHeader"] { background-color: transparent; }
h1,h2,h3 { font-family: 'Outfit', sans-serif; letter-spacing: -.03em; }
h1 { font-weight: 800!important; }
.hero { border: 1px solid rgba(154,224,170,.18); border-radius: 24px; padding: 34px 38px 37px; background: radial-gradient(circle at 82% 18%,rgba(109,194,128,.17),transparent 40%),linear-gradient(120deg,#122b24,#102021 74%); margin-bottom: 24px; }
.eyebrow { color:#9bdfaf; font-size:.78rem; text-transform:uppercase; letter-spacing:.16em; font-weight:700; }
.hero-title { color:#f3fff5; font-size:clamp(2.4rem,5vw,4.2rem); line-height:1.08; font-weight:800; font-family:'Outfit',sans-serif; margin:14px 0; letter-spacing:-.055em; }
.hero-title .accent {color:#adf1a0;}
.hero-sub { color:#bacdc3; font-size:1.04rem; line-height:1.7; max-width:730px; }
.chip { display:inline-block; border:1px solid #345b48; border-radius:25px; padding:6px 11px; font-size:.78rem; color:#bdeac6; margin-right:7px; margin-top:13px; background:#1a372c; }
.panel {background: #12252a; border:1px solid #284139; border-radius:17px; padding:19px 22px; margin:9px 0 18px; }
.panel small {color:#a6bdb0;}
.section-tag {color:#9bd5a2;letter-spacing:.12em;text-transform:uppercase;font-size:.76rem;font-weight:700;}
.stat-tile {background:linear-gradient(135deg,#142b29,#132127);border:1px solid #29433b;border-radius:16px;padding:20px 23px;min-height:135px}
.stat-label {color:#a0baae;font-size:.85rem;}
.stat-value {font-family:'Outfit',sans-serif;color:#edffef;font-size:2.05rem;font-weight:700;line-height:1.35;}
.stat-foot {font-size:.76rem;color:#8ea99a;}
.result {padding:25px 28px;border:1px solid #6dae8a;border-radius:18px;background:linear-gradient(135deg,#174b38,#18332d);margin:12px 0 18px;}
.result-title {color:#a9e5bb;text-transform:uppercase;letter-spacing:.13em;font-size:.78rem;}
.result-number {font-family:'Outfit',sans-serif;font-size:3.2rem;font-weight:800;color:#f5fff3;letter-spacing:-.035em;}
.result-unit {color:#c4e6ca;font-size:1rem;}
[data-testid="stForm"] {border:1px solid #29433b;background:#102328;border-radius:20px;padding:20px 22px;}
.stButton>button[kind="primary"],.stFormSubmitButton>button {background:#a8efa6!important;color:#14321f!important;border:0;border-radius:10px;font-weight:700;}
.stButton>button:hover,.stFormSubmitButton>button:hover {filter:brightness(1.07)}
[data-testid="stMetric"]{background:#142629;padding:16px;border-radius:15px;border:1px solid #2b4740;}
[data-testid="stMetricValue"] {color:#dfffe1;}
[data-testid="stTabs"] button {font-weight:600;}
.stAlert {border-radius:14px;}
footer {visibility:hidden;}
/* High-contrast accessibility patch for the dark Streamlit interface. */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stForm"] label,
[data-testid="stForm"] label p {
  color: #edf9f0 !important;
  opacity: 1 !important;
  font-weight: 600 !important;
}
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
  color: #bcd7c7 !important;
  opacity: 1 !important;
}
button[data-baseweb="tab"],
[data-testid="stTabs"] button[role="tab"] {
  color: #dceee1 !important;
  opacity: 1 !important;
}
button[data-baseweb="tab"][aria-selected="true"],
[data-testid="stTabs"] button[aria-selected="true"] {
  color: #b7f5aa !important;
  font-weight: 700 !important;
}
/* Keep focus borders visible for keyboard users. */
[data-testid="stForm"] :focus-visible {
  outline: 2px solid #a8efa6 !important;
  outline-offset: 2px;
}
</style>"""
st.markdown(CSS, unsafe_allow_html=True)


def setting(name: str) -> str:
    # Streamlit secrets work in deployed Streamlit Community Cloud apps.
    try:
        value = st.secrets.get(name, "")
        if value:
            return str(value).strip()
    except (FileNotFoundError, KeyError):
        pass
    return os.environ.get(name, "").strip()


@st.cache_resource(show_spinner="Loading the trained Random Forest model…")
def load_model(model_url: str, expected_digest: str):
    if LOCAL_MODEL.exists():
        path = LOCAL_MODEL
    elif model_url:
        if not model_url.startswith("https://"):
            raise ValueError("MODEL_URL must start with https://")
        if not CACHE_PATH.is_file():
            temp = CACHE_PATH.with_suffix(".part")
            try:
                with requests.get(model_url, stream=True, timeout=(20,120), allow_redirects=True) as resp:
                    resp.raise_for_status()
                    with temp.open("wb") as fp:
                        for part in resp.iter_content(chunk_size=1024*1024):
                            if part:
                                fp.write(part)
                if temp.stat().st_size < 1_000_000:
                    raise RuntimeError("The download appears incomplete; verify the release asset URL.")
                temp.replace(CACHE_PATH)
            finally:
                temp.unlink(missing_ok=True)
        path = CACHE_PATH
    else:
        raise FileNotFoundError("Configure MODEL_URL in Streamlit Secrets, or place the model locally.")
    if expected_digest:
        sha = hashlib.sha256()
        with path.open("rb") as file:
            while chunk := file.read(1024*1024):
                sha.update(chunk)
        if sha.hexdigest().lower() != expected_digest.lower():
            # Avoid loading untrusted or accidentally changed pickle files.
            if path == CACHE_PATH:
                path.unlink(missing_ok=True)
            raise ValueError("Model checksum mismatch. Check MODEL_SHA256 and release asset.")
    # joblib uses pickle: ONLY load the user's own/trusted model assets.
    loaded = joblib.load(path)
    return loaded


st.markdown("""
<div class="hero">
  <div class="eyebrow">🌾 CropCast &nbsp; / &nbsp; AGRICULTURAL INTELLIGENCE</div>
  <div class="hero-title">Grow smarter with<br><span class="accent">AI-powered yield insights.</span></div>
  <div class="hero-sub">Estimate crop productivity from rainfall, temperature, soil, farming practices and weather. Powered by a real trained Random Forest model—not hardcoded predictions.</div>
  <div><span class="chip">✦ Random Forest ML</span><span class="chip">✦ 6 Crops</span><span class="chip">✦ 8 Agronomic Inputs</span></div>
</div>
""", unsafe_allow_html=True)

x,y,z = st.columns(3)
with x:
    st.markdown('<div class="stat-tile"><div class="stat-label">Model B · Test R²</div><div class="stat-value">0.9031</div><div class="stat-foot">Held-out random test split</div></div>',unsafe_allow_html=True)
with y:
    st.markdown('<div class="stat-tile"><div class="stat-label">Model B · RMSE</div><div class="stat-value">0.5233</div><div class="stat-foot">tons / hectare</div></div>',unsafe_allow_html=True)
with z:
    st.markdown('<div class="stat-tile"><div class="stat-label">Training examples</div><div class="stat-value">40,000</div><div class="stat-foot">from 50,000 sampled records</div></div>',unsafe_allow_html=True)

st.write("")
predict_tab, compare_tab, history_tab, performance_tab, about_tab = st.tabs([
    "🌱  Yield Predictor", "🌾  Compare Crops", "🗂️  This Session",
    "📊  Model Performance", "🧭  About the System"
])

with predict_tab:
    st.markdown("### Farm conditions")
    st.caption("Select conditions based on your farm or planned season. Future weather inputs should be treated as scenarios or forecasts.")
    with st.form("yield_form"):
        a,b = st.columns(2,gap="large")
        with a:
            crop = st.selectbox("Crop variety", CROPS, index=0)
            soil = st.selectbox("Soil type", SOILS, index=0)
            region = st.selectbox("Agricultural region", REGIONS, index=0)
            fertilizer = st.selectbox("Fertilizer used / planned", [True,False], format_func=lambda v: "Yes" if v else "No")
        with b:
            rainfall = st.number_input("Rainfall (mm)", min_value=100.0, max_value=1000.0, value=550.0, step=10.0)
            temperature = st.number_input("Temperature (°C)", min_value=15.0, max_value=40.0, value=27.5, step=0.5)
            weather = st.selectbox("Weather conditions", WEATHER)
            irrigation = st.selectbox("Irrigation used / planned", [True,False], format_func=lambda v: "Yes" if v else "No")
        submitted = st.form_submit_button("✨  Predict crop yield", width="stretch", type="primary")

    if submitted:
        input_row = pd.DataFrame([{
            "Region": region, "Soil_Type": soil, "Crop": crop,
            "Rainfall_mm": float(rainfall), "Temperature_Celsius": float(temperature),
            "Fertilizer_Used": bool(fertilizer), "Irrigation_Used": bool(irrigation),
            "Weather_Condition": weather,
        }], columns=FEATURES)
        # Validate the same exact input schema used in training.
        try:
            input_row = model_input_frame(input_row.iloc[0].to_dict())
        except ValueError as validation_error:
            st.error(str(validation_error))
            st.stop()
        # Public release model. The SHA-256 below was verified against the user's Model B file.
        url = "https://github.com/Kxni5hk/crop-yield-predictor/releases/download/v1.0.1/crop_yield_model_b_for_release.joblib"
        digest = "2e3605235e16dd13c382c2c1493e575d4225ad0ee0342f96d22ae5ab358f932b"
        try:
            model = load_model(url, digest)
            pred = float(model.predict(input_row)[0])
            if not np.isfinite(pred):
                raise ValueError("Model returned a non-finite prediction.")
            st.session_state["show_what_if"] = False
            st.session_state.pop("crop_comparison", None)
            st.session_state["last_prediction"]={"yield": pred,"crop":crop,"region":region,"inputs":input_row}
            # Session-only demo history: no account, no persistent storage.
            record = prediction_record(input_row.iloc[0].to_dict(), pred)
            st.session_state.setdefault("demo_history", []).append(record)
            st.session_state["demo_history"] = st.session_state["demo_history"][-25:]
        except Exception as exc:
            st.error("Could not generate a prediction. Check model configuration and deployment logs.")
            st.code(str(exc))
            st.info("On Streamlit Cloud, open App settings → Secrets and set MODEL_URL to the public GitHub Release .joblib asset URL. For a local test, put the model next to app.py.")

    result = st.session_state.get("last_prediction")
    if result:
        pred = result["yield"]
        if pred < 0:
            st.warning("The model predicted a negative yield. This is not physically meaningful; review the input and model limitations.")
        st.markdown(f"""<div class="result"><div class="result-title">Estimated yield • {result['crop']}</div><div class="result-number">{pred:,.2f} <span class="result-unit">tons / hectare</span></div><div class="result-unit">≈ {pred*1000:,.0f} kg per hectare &nbsp; · &nbsp; {result['region']} region</div></div>""", unsafe_allow_html=True)
        st.caption("⚠️ Educational model estimate. Not a guarantee, and not independently validated for real farms or future seasons.")
        st.download_button("⬇ Download input and result as CSV", data=result["inputs"].assign(Predicted_Yield_tons_per_hectare=pred).to_csv(index=False), file_name="cropcast_prediction.csv", mime="text/csv")
        with st.expander("📏 Land area & total production · optional", expanded=False):
            st.caption("Simple area conversion based on the model's t/ha estimate; not another ML forecast.")
            area_unit = st.selectbox("Area unit", ["hectares", "acres"], key="area_unit")
            area_size = st.number_input("Cultivated area", min_value=0.01, max_value=100000.0,
                                        value=1.0, step=0.5, key="area_size")
            area_result = calculate_area_estimate(pred, area_size, area_unit)
            st.metric("Estimated total production", f"{area_result['production_tonnes']:,.2f} tonnes")
            st.caption(f"Equivalent area: {area_result['area_hectares']:,.3f} hectares; scenario-based estimate only.")

        with st.expander("🔎 Explore prediction sensitivity · lightweight", expanded=False):
            st.caption(
                "Optional one-feature-at-a-time model scenarios. This is not SHAP, "
                "an attribution of the actual yield, or evidence of causal farming effects."
            )
            if st.checkbox("Show what-if comparisons", key="show_what_if", value=False):
                try:
                    from sensitivity import compare_one_feature_at_a_time
                    scenario_model = load_model(
                        "https://github.com/Kxni5hk/crop-yield-predictor/releases/download/v1.0.1/crop_yield_model_b_for_release.joblib",
                        "2e3605235e16dd13c382c2c1493e575d4225ad0ee0342f96d22ae5ab358f932b",
                    )
                    current_yield, scenarios = compare_one_feature_at_a_time(
                        scenario_model, result["inputs"]
                    )
                    st.write(f"**Current prediction:** {current_yield:.3f} t/ha")
                    st.dataframe(
                        scenarios.style.format({
                            "Scenario yield (t/ha)": "{:.3f}",
                            "Change vs current (t/ha)": "{:+.3f}",
                        }),
                        hide_index=True,
                        width="stretch",
                    )
                    st.caption(
                        "Each row changes only the indicated input to the displayed "
                        "alternative; other inputs remain fixed. This is a model "
                        "sensitivity test, not a recommended farming action."
                    )
                except Exception as exc:
                    st.warning("Sensitivity comparison unavailable; your yield prediction remains valid.")
                    st.code(str(exc))

    elif not LOCAL_MODEL.exists() and not setting("MODEL_URL"):
        st.info("Website design is ready. Add a model-release URL in Streamlit Cloud Secrets to activate live predictions. The app never substitutes fake results.")


with compare_tab:
    st.markdown("### 🌾 Compare the six supported crops")
    st.caption("Experimental comparison: uses the real Model B. These are scenario outputs, not crop suitability, profitability, or farming recommendations.")
    result_for_comparison = st.session_state.get("last_prediction")
    if not result_for_comparison:
        st.info("Generate a yield prediction on the Predictor tab first. The comparison reuses those farm conditions.")
    else:
        st.write("**Farm conditions:**", result_for_comparison["region"],
                 "·", result_for_comparison["inputs"].iloc[0]["Soil_Type"])
        if st.button("Compare all 6 crops with current conditions", key="compare_all_crops"):
            try:
                comparison_model = load_model(
                    "https://github.com/Kxni5hk/crop-yield-predictor/releases/download/v1.0.1/crop_yield_model_b_for_release.joblib",
                    "2e3605235e16dd13c382c2c1493e575d4225ad0ee0342f96d22ae5ab358f932b",
                )
                comparison = compare_supported_crops(
                    comparison_model, result_for_comparison["inputs"].iloc[0].to_dict()
                )
                st.session_state["crop_comparison"] = comparison
            except Exception as exc:
                st.error("Crop comparison unavailable; normal predictions still work.")
                st.code(str(exc))
        comparison = st.session_state.get("crop_comparison")
        if comparison is not None:
            st.bar_chart(comparison.set_index("Crop")["Estimated yield (t/ha)"])
            st.dataframe(comparison.style.format({
                "Estimated yield (t/ha)": "{:.3f}",
                "Estimated yield (kg/ha)": "{:,.0f}",
            }), hide_index=True, width="stretch")
            st.download_button(
                "⬇ Export crop comparison CSV",
                comparison.to_csv(index=False),
                file_name="cropcast_crop_comparison.csv",
                mime="text/csv", key="export_crop_comparison"
            )
            st.caption("All eight input fields remain fixed except Crop. Model performance in other seasons and fields is unverified.")

with history_tab:
    st.markdown("### 🗂️ Prediction history — this browser session only")
    st.caption("Demo-only session history (maximum 25 records). This is NOT an authenticated or persistent account feature.")
    history = st.session_state.get("demo_history", [])
    if history:
        history_frame = pd.DataFrame(history)
        st.dataframe(history_frame, hide_index=True, width="stretch")
        st.download_button("⬇ Download session history CSV",
                           history_frame.to_csv(index=False), "cropcast_session_history.csv",
                           mime="text/csv", key="history_download")
        if st.button("Clear session history", key="history_clear"):
            st.session_state["demo_history"] = []
            st.rerun()
    else:
        st.info("Your predictions made in this session will appear here. Refresh or server restart may clear them.")

with performance_tab:
    st.markdown("### Evidence from model evaluation")
    st.caption("Values are from the previously supplied project report (random test split; 10,000 test rows).")
    table=pd.DataFrame({"Model": ["A · All features", "B · Without harvest days"], "RMSE (t/ha)":[0.5211,0.5233],"MAE (t/ha)":[0.4156,0.4175],"R²":[0.9039,0.9031]})
    st.dataframe(table,hide_index=True,width="stretch")
    st.markdown("#### Crop-wise prediction errors")
    chart=ROOT / "assets" / "crop_wise_performance.png"
    if chart.exists():st.image(str(chart),width="stretch")
    st.markdown("#### Error diagnostics")
    residual = ROOT / "assets" / "residual_analysis.png"
    if residual.exists():st.image(str(residual),width="stretch")
    st.info("Model A scores slightly better, while Model B avoids the Days_to_Harvest feature. Accuracy on different farms and future seasons is still untested.")

with about_tab:
    st.markdown("### Built for an academic ML project")
    st.markdown("""
    **Pipeline:** Agricultural CSV → Cleaning → One-hot encoding + imputation → Random Forest Regressor → Model B prediction.

    **Target:** `Yield_tons_per_hectare` (tons per hectare). **Inputs:** 8 fields including 6 crop options and 6 soil types.

    **Why Model B?** It excludes `Days_to_Harvest` for easier scenario-based use; this does not mean its predictions are independently validated future forecasts.

    **Limitations:** Dataset provenance and field realism require independent verification. Rainfall, temperature and weather may not be known before a season, so treat inputs as projected conditions. No financial or crop-management recommendations are inferred from the model.

    **Model disclosure:** Predictive results come from the trained scikit-learn pipeline. The public site may sleep on a free hosting tier; its first request can take longer.
    """)

st.markdown('<div style="color:#759488;font-size:.78rem;padding:24px 0 3px;text-align:center">CropCast · Crop Yield Prediction Research Prototype · Powered by Python & Random Forest</div>',unsafe_allow_html=True)
