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
from batch_tools import MAX_CSV_BYTES, MAX_CSV_ROWS, csv_template, predict_csv_batch
from weather_context import fetch_city_weather

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

from premium_ui import STYLES, brand_banner, hero_banner, metric_cards, workflow_cards, section_heading, result_card, footer

st.markdown(STYLES, unsafe_allow_html=True)

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


st.markdown(brand_banner(), unsafe_allow_html=True)
st.markdown(hero_banner(), unsafe_allow_html=True)
st.markdown('<div id="workspace" class="cc-workspace-anchor" aria-hidden="true"></div>', unsafe_allow_html=True)

predict_tab, compare_tab, bulk_tab, weather_tab, history_tab, performance_tab, about_tab = st.tabs([
    "🌱  Predictor", "🌾  Compare Crops", "📑  Bulk CSV",
    "☁️  Weather Context", "🗂️  Session", "📊  Model Evidence", "🧭  About"
])

with predict_tab:
    st.markdown(section_heading("01 / Your farm profile", "Build a yield scenario", "Choose the agricultural conditions for Model B. Future climate inputs are hypothetical scenarios, not live forecasts."), unsafe_allow_html=True)
    st.markdown(
        '<div class="cc-step-row" role="list">'
        '<div class="cc-step" role="listitem"><b>01</b> Select farm conditions</div>'
        '<div class="cc-step" role="listitem"><b>02</b> Generate prediction</div>'
        '<div class="cc-step" role="listitem"><b>03</b> Compare scenarios</div>'
        '</div>', unsafe_allow_html=True
    )
    with st.form("yield_form"):
        a,b = st.columns(2,gap="large")
        with a:
            crop = st.selectbox("Crop", CROPS, index=0, help="Choose one of the six crop types supported by the trained model.")
            soil = st.selectbox("Soil type", SOILS, index=0, help="Select a supported soil category from the research dataset.")
            region = st.selectbox("Dataset region", REGIONS, index=0, help="North/South/East/West are dataset categories, not precise GPS locations.")
            fertilizer = st.selectbox("Fertilizer used / planned", [True,False], format_func=lambda v: "Yes" if v else "No")
        with b:
            rainfall = st.number_input("Rainfall scenario (mm)", min_value=100.0, max_value=1000.0, value=550.0, step=10.0, help="Enter the rainfall quantity corresponding to the model scenario; do not copy a 5-day weather forecast here.")
            temperature = st.number_input("Temperature scenario (°C)", min_value=15.0, max_value=40.0, value=27.5, step=0.5, help="Model input for your hypothetical conditions; not automatically filled from live weather.")
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
            st.info("The application uses the verified Model B GitHub release. If predictions fail repeatedly, review the Render server logs or retry later.")

    result = st.session_state.get("last_prediction")
    if result:
        pred = result["yield"]
        if pred < 0:
            st.warning("The model predicted a negative yield. This is not physically meaningful; review the input and model limitations.")
        st.markdown(result_card(result["crop"], result["region"], pred), unsafe_allow_html=True)
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

    else:
        st.caption("Your prediction will appear here after you submit the form. The verified Model B is loaded on first use; no API key or model upload is needed.")


with compare_tab:
    st.markdown(section_heading("02 / Comparative intelligence", "Explore your crop options", "Compare model predictions for six supported crops with other inputs held constant. This is not suitability or profitability advice."), unsafe_allow_html=True)
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


with bulk_tab:
    st.markdown(section_heading(
        "03 / Research workflows", "Bulk crop yield analysis",
        "Upload up to 50 validated farm-condition scenarios and receive real Model B predictions in a downloadable table. Uploaded CSV data is not stored on the server."
    ), unsafe_allow_html=True)
    st.download_button(
        "⬇ Download CSV template",
        data=csv_template(), file_name="cropcast_input_template.csv",
        mime="text/csv", key="batch_template_download"
    )
    st.caption(
        "Required columns: Region, Soil_Type, Crop, Rainfall_mm, Temperature_Celsius, "
        "Fertilizer_Used, Irrigation_Used, Weather_Condition. Boolean inputs accept Yes/No or True/False."
    )
    uploaded = st.file_uploader(
        "Choose your agricultural scenarios CSV", type=["csv"],
        help="Up to 50 data rows and 128 KB. Invalid rows are reported separately.",
        key="batch_csv_upload"
    )
    if uploaded is not None:
        if uploaded.size > MAX_CSV_BYTES:
            st.warning("Upload limit is 128 KB. Reduce the file size before continuing.")
        elif st.button("Run verified batch predictions", key="batch_predict"):
            try:
                blob = uploaded.getvalue()
                batch_model = load_model(
                    "https://github.com/Kxni5hk/crop-yield-predictor/releases/download/v1.0.1/crop_yield_model_b_for_release.joblib",
                    "2e3605235e16dd13c382c2c1493e575d4225ad0ee0342f96d22ae5ab358f932b",
                )
                with st.spinner("Evaluating CSV scenarios…"):
                    batch_results, batch_errors = predict_csv_batch(batch_model, blob)
                st.session_state["batch_results"] = batch_results
                st.session_state["batch_errors"] = batch_errors
                st.session_state["batch_file_name"] = uploaded.name
            except (ValueError, RuntimeError) as exc:
                st.error(str(exc))
            except Exception:
                st.error("Bulk prediction is temporarily unavailable. Single prediction still works.")
        if st.session_state.get("batch_file_name") == uploaded.name:
            results = st.session_state.get("batch_results")
            errors = st.session_state.get("batch_errors")
            if results is not None:
                st.metric("Valid farm scenarios processed", len(results))
                if not results.empty:
                    st.dataframe(results, hide_index=True, width="stretch")
                    st.download_button(
                        "⬇ Download batch results CSV",
                        results.to_csv(index=False).encode("utf-8"),
                        file_name="cropcast_batch_predictions.csv",
                        mime="text/csv", key="batch_results_download",
                    )
                if errors is not None and not errors.empty:
                    st.warning(f"{len(errors)} CSV rows could not be used. Fix the reported values and retry.")
                    st.dataframe(errors, hide_index=True, width="stretch")
    st.caption(
        "Predictions are experimental model estimates, not verified agronomic guidance. "
        "Do not include sensitive personal information in uploaded CSV files."
    )

with weather_tab:
    st.markdown(section_heading(
        "04 / Weather intelligence", "Understand your local weather",
        "View current conditions and a 5-day forecast from Open-Meteo. "
        "These observations are informational and are NOT fed into the trained Model B input fields."
    ), unsafe_allow_html=True)
    st.caption("Enter a city manually. No GPS permission, account sign-in or personal-location storage is required.")
    city = st.text_input("City name", placeholder="e.g. Jaipur", max_chars=80, key="forecast_city")
    if st.button("Get city weather context", key="forecast_lookup"):
        if not city or len(city.strip()) < 2:
            st.warning("Please enter a city name with at least two characters.")
        else:
            try:
                with st.spinner("Loading weather source…"):
                    info = fetch_city_weather(city)
                st.session_state["weather_context"] = info
            except ValueError as exc:
                st.warning(str(exc))
    weather = st.session_state.get("weather_context")
    if weather:
        st.markdown(f"#### {weather['location']}")
        st.caption(f"Source: {weather['source']} · observed {weather['as_of']} ({weather['timezone']})")
        w1, w2, w3 = st.columns(3)
        with w1:
            st.metric("Current temperature", f"{weather['temperature_c']:.1f} °C")
        with w2:
            st.metric("Humidity", f"{weather['humidity_pct']:.0f}%")
        with w3:
            st.metric("Wind", f"{weather['wind_kmh']:.1f} km/h")
        st.write(f"**Current sky conditions:** {weather['conditions']}")
        forecast_table = pd.DataFrame(weather["forecast"])
        st.dataframe(forecast_table, hide_index=True, width="stretch")
        st.bar_chart(forecast_table.set_index("Date")["Precipitation (mm)"])
        st.caption(
            "5-day forecast precipitation is NOT the seasonal Rainfall_mm variable used to train the crop-yield model. "
            "Enter your own agricultural scenario separately in the Predictor tab."
        )

with history_tab:
    st.markdown(section_heading("05 / Temporary workspace", "Your session timeline", "Browse up to 25 predictions from this session, export CSV or clear results. No login or persistent user database is connected."), unsafe_allow_html=True)
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
    st.markdown(metric_cards(), unsafe_allow_html=True)
    st.markdown(section_heading("06 / Research integrity", "See the evidence", "Recorded metrics from the original random test split with 10,000 held-out examples. No independent farm validation is claimed."), unsafe_allow_html=True)
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
    st.markdown(workflow_cards(), unsafe_allow_html=True)
    st.markdown(section_heading("07 / The methodology", "Built on research, not guesses", "Explore the underlying pipeline, supported inputs, evaluation methodology and limitations."), unsafe_allow_html=True)
    st.markdown("""
    **Pipeline:** Agricultural CSV → Cleaning → One-hot encoding + imputation → Random Forest Regressor → Model B prediction.

    **Target:** `Yield_tons_per_hectare` (tons per hectare). **Inputs:** 8 fields including 6 crop options and 6 soil types.

    **Why Model B?** It excludes `Days_to_Harvest` for easier scenario-based use; this does not mean its predictions are independently validated future forecasts.

    **Limitations:** Dataset provenance and field realism require independent verification. Rainfall, temperature and weather may not be known before a season, so treat inputs as projected conditions. No financial or crop-management recommendations are inferred from the model.

    **Model disclosure:** Predictive results come from the trained scikit-learn pipeline. The public site may sleep on a free hosting tier; its first request can take longer.
    """)

st.markdown(footer(), unsafe_allow_html=True)
