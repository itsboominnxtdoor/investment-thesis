FROM python:3.12-slim

WORKDIR /app

# Copy dependency definition first for layer caching
COPY pyproject.toml .

# Install the project and its dependencies
RUN pip install --no-cache-dir .

# Copy the rest of the application
COPY . .

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
