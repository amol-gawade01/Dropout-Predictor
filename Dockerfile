FROM python:3.12-slim

WORKDIR /app


# XGBoost commonly needs OpenMP.
RUN apt-get update \
    && apt-get install -y \
        --no-install-recommends \
        gcc \
        g++ \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*


# Install uv.
RUN pip install \
    --no-cache-dir \
    uv


# Copy dependency files first.
COPY pyproject.toml uv.lock ./


# Install dependencies.
RUN uv sync \
    --frozen \
    --no-dev


# Copy application code.
COPY . .


# Use the uv virtual environment.
ENV PATH="/app/.venv/bin:$PATH"


EXPOSE 8000


CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
