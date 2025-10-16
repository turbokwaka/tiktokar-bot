# Dockerfile

FROM python:3.11-slim-bookworm as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    gallery-dl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN pip install --no-cache-dir .

FROM python:3.11-slim-bookworm as final

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    gallery-dl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY bot.py .
COPY tools ./tools/

CMD ["python", "bot.py"]