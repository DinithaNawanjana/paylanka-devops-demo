FROM python:3.12-slim

# Create non-root user
RUN useradd -m appuser

WORKDIR /app

# Copy and install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY app/ ./app/

# Create a writable data dir for SQLite and give ownership to appuser
RUN mkdir -p /data && chown -R appuser:appuser /data

# Run as non-root
USER appuser

# App will put its DB here (writable)
ENV DB_FILE=/data/transactions.db

EXPOSE 8000

# JSON-form CMD prevents signal issues & "command not found" errors
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app.app:app"]
