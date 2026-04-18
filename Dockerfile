FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app

# Redirect model caches to /app so they can be persisted via volume mounts
ENV TORCH_HOME=/app/.cache/torch
ENV HF_HOME=/app/.cache/huggingface

# Install system dependencies:
#   git         — required to fetch the kanade-tokenizer git dependency
#   espeak-ng   — required by misaki's EspeakG2P for phoneme conversion
#   libsndfile1 — required by the soundfile Python package
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    espeak-ng \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests first for better layer caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies using the lockfile for reproducible builds
RUN uv sync --frozen --no-dev

# Copy application source
COPY app.py inference.py cli.py ./
COPY core/ ./core/

# model/ and voice/ are intentionally excluded — they are downloaded at
# runtime from HuggingFace. Mount host directories to persist them:
#   -v $(pwd)/model:/app/model
#   -v $(pwd)/voice:/app/voice

EXPOSE 7860

CMD ["uv", "run", "python", "app.py"]
