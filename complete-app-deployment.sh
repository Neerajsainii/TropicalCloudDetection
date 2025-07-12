#!/bin/bash

# Complete Application Deployment Script
# Run this ON the VM after basic setup is complete

set -e

echo "🚀 Deploying Tropical Cloud Detection Application"
echo "================================================"

# Navigate to application directory
cd /opt/tropical-cloud-detection

# Activate virtual environment
source venv/bin/activate

# Get your actual repository (you'll need to replace with your repo URL)
echo "📥 Cloning your repository..."
# For now, we'll create the structure manually since we have the code

# Create Django project structure
echo "📁 Creating Django project structure..."

# Create manage.py
cat > manage.py << 'MANAGEEOF'
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

if __name__ == '__main__':
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_detection_portal.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
MANAGEEOF

# Create project directory
mkdir -p cloud_detection_portal
mkdir -p cloud_detection
mkdir -p templates
mkdir -p static
mkdir -p media

# Create basic Django settings
cat > cloud_detection_portal/settings.py << 'SETTINGSEOF'
import os
from pathlib import Path
from decouple import config, Csv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-temp-key-change-this')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'cloud_detection',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cloud_detection_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cloud_detection_portal.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='*', cast=Csv())
CORS_ALLOW_ALL_ORIGINS = True

# CSRF settings
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='*', cast=Csv())

# File upload settings - NO LIMITS!
FILE_UPLOAD_MAX_MEMORY_SIZE = None
DATA_UPLOAD_MAX_MEMORY_SIZE = None
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Google Cloud Storage settings
GCS_BUCKET_NAME = config('GCS_BUCKET_NAME', default='tropical-cloud-detection-uploads')
GOOGLE_CLOUD_PROJECT = config('GOOGLE_CLOUD_PROJECT', default='tropical-cloud-detection')
SETTINGSEOF

# Create basic URLs
cat > cloud_detection_portal/urls.py << 'URLSEOF'
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cloud_detection.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
URLSEOF

# Create WSGI configuration
cat > cloud_detection_portal/wsgi.py << 'WSGIEOF'
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cloud_detection_portal.settings')
application = get_wsgi_application()
WSGIEOF

# Create __init__.py files
touch cloud_detection_portal/__init__.py
touch cloud_detection/__init__.py

# Create basic cloud_detection app
cat > cloud_detection/models.py << 'MODELSEOF'
from django.db import models
from django.contrib.auth.models import User
import uuid

class SatelliteData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='satellite_data/')
    original_filename = models.CharField(max_length=255)
    satellite_name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=100)
    file_size = models.BigIntegerField()
    upload_date = models.DateTimeField(auto_now_add=True)
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    def __str__(self):
        return f"{self.original_filename} - {self.satellite_name}"
MODELSEOF

# Create basic views
cat > cloud_detection/views.py << 'VIEWSEOF'
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import SatelliteData
import json

def home(request):
    return render(request, 'cloud_detection/home.html')

@csrf_exempt
@require_http_methods(["POST"])
def upload_file(request):
    try:
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        # Create satellite data record
        satellite_data = SatelliteData.objects.create(
            file=uploaded_file,
            original_filename=uploaded_file.name,
            satellite_name=request.POST.get('satellite_name', 'Unknown'),
            data_type=request.POST.get('data_type', 'Unknown'),
            file_size=uploaded_file.size,
        )
        
        return JsonResponse({
            'success': True,
            'message': 'File uploaded successfully',
            'file_id': str(satellite_data.id),
            'filename': uploaded_file.name,
            'size': uploaded_file.size
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def processing_status(request):
    files = SatelliteData.objects.all().order_by('-upload_date')
    return render(request, 'cloud_detection/processing_status.html', {'files': files})
VIEWSEOF

# Create basic URLs for the app
cat > cloud_detection/urls.py << 'APPURLSEOF'
from django.urls import path
from . import views

app_name = 'cloud_detection'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('processing/', views.processing_status, name='processing_status'),
]
APPURLSEOF

# Create basic admin
cat > cloud_detection/admin.py << 'ADMINEOF'
from django.contrib import admin
from .models import SatelliteData

@admin.register(SatelliteData)
class SatelliteDataAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'satellite_name', 'data_type', 'file_size', 'upload_date', 'processing_status']
    list_filter = ['satellite_name', 'data_type', 'processing_status', 'upload_date']
    search_fields = ['original_filename', 'satellite_name']
    readonly_fields = ['id', 'upload_date', 'file_size']
ADMINEOF

# Create basic template directory
mkdir -p templates/cloud_detection

# Create basic home template
cat > templates/cloud_detection/home.html << 'HOMEEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tropical Cloud Detection</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .upload-area {
            border: 2px dashed #007bff;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background-color: #f8f9fa;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .upload-area:hover {
            border-color: #0056b3;
            background-color: #e9ecef;
        }
        .upload-area.dragover {
            border-color: #28a745;
            background-color: #d4edda;
        }
        .progress-container {
            margin-top: 20px;
            display: none;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background-color: #007bff;
            width: 0%;
            transition: width 0.3s ease;
        }
        .btn {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        .btn:hover {
            background-color: #0056b3;
        }
        .success {
            color: #28a745;
            margin-top: 10px;
        }
        .error {
            color: #dc3545;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌴 Tropical Cloud Detection</h1>
        <p>Upload your satellite data files - No size limits!</p>
        
        <form id="uploadForm" enctype="multipart/form-data">
            {% csrf_token %}
            <div class="upload-area" id="uploadArea">
                <h3>📁 Drag & Drop Files Here</h3>
                <p>or click to browse</p>
                <input type="file" id="fileInput" name="file" style="display: none;" accept=".h5,.hdf5,.nc,.netcdf">
            </div>
            
            <div style="margin-top: 20px;">
                <label for="satellite_name">Satellite Name:</label>
                <input type="text" id="satellite_name" name="satellite_name" required style="width: 100%; padding: 8px; margin-top: 5px;">
            </div>
            
            <div style="margin-top: 10px;">
                <label for="data_type">Data Type:</label>
                <input type="text" id="data_type" name="data_type" required style="width: 100%; padding: 8px; margin-top: 5px;">
            </div>
            
            <button type="submit" class="btn">Upload & Process</button>
        </form>
        
        <div class="progress-container" id="progressContainer">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <p id="progressText">0%</p>
        </div>
        
        <div id="message"></div>
        
        <div style="margin-top: 30px;">
            <a href="/processing/" class="btn">View Processing Status</a>
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const uploadForm = document.getElementById('uploadForm');
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const message = document.getElementById('message');

        // Click to upload
        uploadArea.addEventListener('click', () => fileInput.click());

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateUploadArea(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                updateUploadArea(e.target.files[0]);
            }
        });

        function updateUploadArea(file) {
            uploadArea.innerHTML = `
                <h3>✅ File Selected</h3>
                <p><strong>${file.name}</strong></p>
                <p>Size: ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
            `;
        }

        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(uploadForm);
            const file = fileInput.files[0];
            
            if (!file) {
                message.innerHTML = '<div class="error">Please select a file</div>';
                return;
            }

            progressContainer.style.display = 'block';
            message.innerHTML = '';

            try {
                const xhr = new XMLHttpRequest();
                
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        progressFill.style.width = percentComplete + '%';
                        progressText.textContent = Math.round(percentComplete) + '%';
                    }
                });

                xhr.addEventListener('load', () => {
                    if (xhr.status === 200) {
                        const response = JSON.parse(xhr.responseText);
                        message.innerHTML = '<div class="success">✅ File uploaded successfully!</div>';
                        uploadForm.reset();
                        uploadArea.innerHTML = `
                            <h3>📁 Drag & Drop Files Here</h3>
                            <p>or click to browse</p>
                        `;
                        setTimeout(() => {
                            window.location.href = '/processing/';
                        }, 2000);
                    } else {
                        throw new Error('Upload failed');
                    }
                });

                xhr.addEventListener('error', () => {
                    message.innerHTML = '<div class="error">❌ Upload failed</div>';
                });

                xhr.open('POST', '/upload/');
                xhr.send(formData);

            } catch (error) {
                message.innerHTML = '<div class="error">❌ Upload failed: ' + error.message + '</div>';
            }
        });
    </script>
</body>
</html>
HOMEEOF

# Create processing status template
cat > templates/cloud_detection/processing_status.html << 'STATUSEOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Processing Status - Tropical Cloud Detection</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #007bff;
            color: white;
        }
        .status-pending { color: #ffc107; }
        .status-processing { color: #17a2b8; }
        .status-completed { color: #28a745; }
        .status-failed { color: #dc3545; }
        .btn {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌴 Processing Status</h1>
        
        <a href="/" class="btn">← Back to Upload</a>
        
        {% if files %}
            <table>
                <thead>
                    <tr>
                        <th>Filename</th>
                        <th>Satellite</th>
                        <th>Data Type</th>
                        <th>Size</th>
                        <th>Upload Date</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for file in files %}
                    <tr>
                        <td>{{ file.original_filename }}</td>
                        <td>{{ file.satellite_name }}</td>
                        <td>{{ file.data_type }}</td>
                        <td>{{ file.file_size|filesizeformat }}</td>
                        <td>{{ file.upload_date|date:"Y-m-d H:i" }}</td>
                        <td class="status-{{ file.processing_status }}">
                            {{ file.get_processing_status_display }}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <p>No files uploaded yet.</p>
        {% endif %}
    </div>
</body>
</html>
STATUSEOF

# Create apps.py
cat > cloud_detection/apps.py << 'APPSEOF'
from django.apps import AppConfig

class CloudDetectionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cloud_detection'
APPSEOF

# Make manage.py executable
chmod +x manage.py

# Update .env with better settings
cat > .env << 'ENVEOF'
ENVIRONMENT=production
SECRET_KEY=django-insecure-change-this-in-production-please
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=*
DEBUG=False
CORS_ALLOWED_ORIGINS=*
CSRF_TRUSTED_ORIGINS=*
GOOGLE_CLOUD_PROJECT=tropical-cloud-detection
GCS_BUCKET_NAME=tropical-cloud-detection-uploads
ENVEOF

# Install additional requirements
pip install dj-database-url

# Run Django setup
echo "🔧 Setting up Django..."
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser (optional)
echo "👤 Creating superuser..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell

# Fix permissions
sudo chown -R www-data:www-data /opt/tropical-cloud-detection

# Restart services
echo "🔄 Restarting services..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart tropical-cloud-detection
sudo systemctl restart nginx

echo ""
echo "🎉 APPLICATION DEPLOYED SUCCESSFULLY!"
echo "================================================"
echo "🌐 Your app is now running at: http://$(curl -s ifconfig.me)"
echo "👤 Admin login: admin / admin123"
echo "📝 Logs: sudo tail -f /var/log/tropical-cloud-detection.log"
echo ""
echo "✅ KEY FEATURES:"
echo "• No upload size limits!"
echo "• Direct file uploads (no GCS workaround needed)"
echo "• Nginx handles large files efficiently"
echo "• Persistent storage on VM"
echo "• Better performance with dedicated resources"
echo ""
echo "🔧 To customize further:"
echo "1. Update SECRET_KEY in .env"
echo "2. Configure your domain in ALLOWED_HOSTS"
echo "3. Set up SSL with certbot"
echo "4. Add your actual processing logic"
echo ""
echo "🎊 Migration complete! Your app is ready!" 