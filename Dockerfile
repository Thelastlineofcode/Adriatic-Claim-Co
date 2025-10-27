# Multi-stage Dockerfile for backend
FROM python:3.11-slim

WORKDIR /app

# Copy backend files
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Create instance directory for SQLite (if used)
RUN mkdir -p instance

# Expose port
EXPOSE 8080

# Run with gunicorn
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
