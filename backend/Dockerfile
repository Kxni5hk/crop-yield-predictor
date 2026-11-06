FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home cropcast
COPY main.py .
# Verify and bake the pinned model once so idle wake-ups do not download it.
ENV MODEL_PATH=/opt/cropcast/model_b.joblib
RUN python -c "from main import load_model; load_model()" && chmod 0444 "$MODEL_PATH"
USER cropcast
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --no-access-log"]
