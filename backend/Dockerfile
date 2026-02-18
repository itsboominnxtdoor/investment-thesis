FROM python:3.12-slim

WORKDIR /app

# Copy dependency definition first for layer caching
COPY . .

# Install the project and its dependencies
RUN pip install --no-cache-dir .

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
