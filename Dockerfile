FROM python:3.10-slim

RUN apt-get update && apt-get install -y gcc libpq-dev openssl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8443

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/certs

RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /app/certs/key.pem \
    -out /app/certs/cert.pem \
    -subj "/C=CO/ST=Bogota/L=Bogota/O=MiApp/OU=Dev/CN=localhost"

VOLUME ["/app/certs"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8443", "--ssl-keyfile", "/app/certs/key.pem", "--ssl-certfile", "/app/certs/cert.pem"]
