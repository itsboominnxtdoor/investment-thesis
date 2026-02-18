FROM python:3.12-slim

WORKDIR /app

# Copy everything first (needed for pip install to find the app package)
COPY . .

# Install the project and its dependencies (including psycopg2-binary)
RUN pip install --no-cache-dir ".[dev]"

# Make startup script executable
RUN chmod +x start.sh

# Run migrations and start server
CMD ["./start.sh"]
