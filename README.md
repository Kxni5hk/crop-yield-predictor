# CropCast — Crop Yield Prediction Website

Modern Streamlit interface powered by the actual trained Random Forest Model B.

## Deployment: Streamlit Community Cloud + GitHub Release

### Why a GitHub Release?
The .joblib model is approximately 147 MB, exceeding GitHub's usual 100 MB limit for repository files. GitHub Release assets permit a much larger file, so the source repository stays small.

1. Create a **public GitHub repository** named `crop-yield-predictor`.
2. Upload these files to the repository root: `app.py`, `requirements.txt`, `README.md`, `.streamlit/config.toml`, and the whole `assets` folder. Do not upload the .joblib model as a regular repository file.
3. In the repository, click **Releases → Draft a new release**, add tag `v1.0`, and attach your trusted model file `crop_yield_model_b.joblib` (provided separately). Publish release.
4. Copy the actual asset download URL from the published release (your username will be in it). Format: `https://github.com/<username>/crop-yield-predictor/releases/download/v1.0/crop_yield_model_b.joblib`
5. Visit https://share.streamlit.io/ and sign in with GitHub. Choose the repository, main branch, and entrypoint `app.py`. In Advanced settings, choose Python 3.11 if offered, and add a Secret:

   ```toml
   MODEL_URL = "https://github.com/<username>/crop-yield-predictor/releases/download/v1.0/crop_yield_model_b.joblib"
   MODEL_SHA256 = "2e3605235e16dd13c382c2c1493e575d4225ad0ee0342f96d22ae5ab358f932b"
   ```

   The SHA256 above matches the model extracted from the supplied project ZIP. **If you use another model file (such as a retrained final model), remove MODEL_SHA256 or replace it with the new file's actual checksum.**

6. Click **Deploy** and then test a prediction. The service downloads the ~147 MB model on first inference; subsequent requests use the cached model while the app stays running.

## Local testing

Place the trusted `crop_yield_model_b.joblib` next to `app.py` or set `MODEL_URL`, then run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Use Python 3.11 and scikit-learn 1.6.1 for best compatibility with the saved model.

## Responsible-use notes

This is a research/education demonstration; data realism, provenance, seasonal forecasting performance, and generalization to external farms are not established. Do not use the model as the sole basis for farming decisions. Public release assets and public repos are visible to everyone. Upload only materials you have rights to publish.
