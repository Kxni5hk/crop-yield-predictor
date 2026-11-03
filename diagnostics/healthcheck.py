"""Public-access diagnostic for CropCast Streamlit Community Cloud."""
import streamlit as st
from datetime import datetime, timezone

st.set_page_config(page_title="CropCast Deployment Check",page_icon="✅")
st.title("✅ CropCast deployment check")
st.success("This diagnostic app loaded successfully.")
st.write("This page deliberately does not load the crop-yield model or SHAP.")
st.caption("UTC time at rendering: " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
st.write("If this page works in Incognito and on another laptop, the basic deployment is accessible.")
