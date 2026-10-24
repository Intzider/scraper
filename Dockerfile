FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STATE_FILE=/app/scraped/seen.txt

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements.txt

COPY notifier ./notifier

RUN useradd --uid 1000 --no-create-home app && mkdir -p /app/scraped && chown app /app/scraped
USER app

CMD ["python", "-m", "notifier", "--loop"]
