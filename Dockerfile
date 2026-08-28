FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install via python3 -m pip
COPY v3/backend/requirements.txt /app/requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . /app

ENV PYTHONPATH=/app/v3

EXPOSE 8000

CMD ["uvicorn", "v3.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
