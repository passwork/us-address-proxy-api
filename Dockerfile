FROM docker.1ms.run/library/python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
