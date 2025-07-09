# Use Python 3.9 slim image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV PORT=8080

# Set work directory
WORKDIR /app

# Install system dependencies required for h5py, netCDF4, and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libhdf5-dev \
    libnetcdf-dev \
    pkg-config \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=cloud_detection_portal.settings

# Create database tables for SQLite (fallback)
RUN python manage.py migrate --settings=cloud_detection_portal.settings || echo "Migration failed, continuing..."

# Expose port
EXPOSE 8080

# Start the application directly
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 300 --access-logfile - --error-logfile - cloud_detection_portal.wsgi:application 