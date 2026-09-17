FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends mupdf-tools && command -v mutool && mutool -v && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["sh", "-c", "exec gunicorn app:app --bind 0.0.0.0:${PORT:-10000}"]
