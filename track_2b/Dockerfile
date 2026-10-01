FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 INBREV_HOME=/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-deu tesseract-ocr-fra tesseract-ocr-ita \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install ".[ocr,eval,dev]"

COPY data ./data
COPY tests ./tests
COPY scripts ./scripts

RUN useradd --create-home inbrev && mkdir -p /app/runs && chown inbrev /app/runs
USER inbrev

EXPOSE 8000
CMD ["python", "-m", "inbrev", "serve", "--host", "0.0.0.0", "--port", "8000"]
