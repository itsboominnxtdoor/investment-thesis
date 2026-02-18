FROM python:3.12-slim

WORKDIR /app

# Copy everything first (needed for pip install to find the app package)
COPY . .

# Install the project and its dependencies (including psycopg2-binary)
RUN pip install --no-cache-dir ".[dev]"

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
