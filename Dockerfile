# Use Python 3.9 slim image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV DATABASE_URL=sqlite:///db.sqlite3
ENV PORT=8080

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with retry logic
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 300 --retries 3 -r requirements.txt || \
    pip install --no-cache-dir --timeout 600 --retries 5 -r requirements.txt

# Copy project
COPY . .

# Collect static files (with fallback database)
RUN python manage.py collectstatic --noinput || true

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Running migrations..."\n\
python manage.py migrate\n\
echo "Starting gunicorn on port $PORT..."\n\
exec gunicorn --bind 0.0.0.0:$PORT --workers 3 --timeout 300 cloud_detection_portal.wsgi:application\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 8080

# Run startup script
CMD ["/app/start.sh"] 