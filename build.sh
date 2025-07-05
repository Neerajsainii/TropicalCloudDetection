#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Convert static asset files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
echo "Running database migrations..."
python manage.py makemigrations --no-input
python manage.py migrate --no-input

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'cloudadmin123')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"

echo "Build completed successfully!" 