FROM python:3.15-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STATE_FILE=/app/scraped/seen.txt

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements.txt

COPY notifier ./notifier

# COPY keeps host file modes, so make the code readable whatever the clone's umask was
RUN chmod -R a+rX /app/notifier \
    && useradd --uid 1000 --no-create-home app \
    && mkdir -p /app/scraped && chown app /app/scraped
USER app

CMD ["python", "-m", "notifier", "--loop"]
