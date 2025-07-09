#!/usr/bin/env python3
"""
Google Cloud Platform Setup Script
This script helps configure the Django app for GCP deployment
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def create_env_file():
    """Create .env file with GCP configuration"""
    env_content = """# Google Cloud Platform Configuration
ENVIRONMENT=production
DEBUG=False

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://cloud_user:cloudpass123@/tropical_cloud_db?host=/cloudsql/PROJECT_ID:REGION:DB_INSTANCE_NAME

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-vm-ip,localhost,127.0.0.1

# CORS Settings
CORS_ALLOWED_ORIGINS=https://your-domain.com,http://your-vm-ip

# CSRF Settings
CSRF_TRUSTED_ORIGINS=https://your-domain.com,http://your-vm-ip

# SSL Settings
SECURE_SSL_REDIRECT=False
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ Created .env file with GCP configuration")

def update_settings_for_gcp():
    """Update settings.py for GCP deployment"""
    settings_file = Path('cloud_detection_portal/settings.py')
    
    if not settings_file.exists():
        print("❌ settings.py not found")
        return
    
    # Read current settings
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Add Google Cloud Storage configuration
    gcs_config = """
# Google Cloud Storage Configuration
if ENVIRONMENT == 'production':
    # Use Google Cloud Storage for media files
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME = config('GS_BUCKET_NAME', default='tropical-cloud-media')
    GS_DEFAULT_ACL = 'publicRead'
    GS_FILE_OVERWRITE = False
    
    # Static files configuration
    STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_STATIC_BUCKET_NAME = config('GS_STATIC_BUCKET_NAME', default='tropical-cloud-static')
"""
    
    # Add the configuration before the logging section
    if 'LOGGING = {' in content and 'GS_BUCKET_NAME' not in content:
        content = content.replace('LOGGING = {', gcs_config + '\n# Logging configuration\nLOGGING = {')
        
        with open(settings_file, 'w') as f:
            f.write(content)
        print("✅ Updated settings.py with Google Cloud Storage configuration")

def create_dockerfile():
    """Create Dockerfile for container deployment"""
    dockerfile_content = """# Use Python 3.9 slim image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations
RUN python manage.py migrate

# Create superuser
RUN python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'cloudadmin123')
"

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "300", "cloud_detection_portal.wsgi:application"]
"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    print("✅ Created Dockerfile for container deployment")

def create_cloudbuild_yaml():
    """Create Cloud Build configuration"""
    cloudbuild_content = """steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/tropical-cloud-detection', '.']
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/tropical-cloud-detection']
  
  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'tropical-cloud-detection'
      - '--image'
      - 'gcr.io/$PROJECT_ID/tropical-cloud-detection'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--memory'
      - '2Gi'
      - '--cpu'
      - '1'
      - '--timeout'
      - '300'
      - '--concurrency'
      - '80'
      - '--max-instances'
      - '10'

images:
  - 'gcr.io/$PROJECT_ID/tropical-cloud-detection'
"""
    
    with open('cloudbuild.yaml', 'w') as f:
        f.write(cloudbuild_content)
    print("✅ Created cloudbuild.yaml for automated deployment")

def main():
    """Main setup function"""
    print("🚀 Setting up Google Cloud Platform deployment...")
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Please run this script from the Django project root directory")
        sys.exit(1)
    
    # Create configuration files
    create_env_file()
    update_settings_for_gcp()
    create_dockerfile()
    create_cloudbuild_yaml()
    
    print("\n✅ GCP setup completed!")
    print("\n📋 Next steps:")
    print("1. Update the .env file with your actual values")
    print("2. Create a Google Cloud Storage bucket for media files")
    print("3. Set up your PostgreSQL database")
    print("4. Deploy using one of these methods:")
    print("   - App Engine: gcloud app deploy")
    print("   - Cloud Run: gcloud run deploy")
    print("   - Compute Engine: Use the gcp_deploy.sh script")
    print("   - Cloud Build: gcloud builds submit")

if __name__ == "__main__":
    main() 