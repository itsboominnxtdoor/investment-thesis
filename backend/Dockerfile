FROM python:3.12-slim

WORKDIR /app

# Copy dependency definition first for layer caching
COPY pyproject.toml .

# Install the project and its dependencies (including psycopg2-binary)
RUN pip install --no-cache-dir ".[dev]"

# Copy the rest of the application
COPY . .

# Run migrations and start server
CMD ["sh", "-c", "python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
