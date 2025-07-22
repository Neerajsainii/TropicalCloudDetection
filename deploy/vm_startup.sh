#!/bin/bash
# VM Startup Script for Tropical Cloud Detection
# This script runs automatically when the VM starts

set -e

# Logging setup
exec > >(tee /var/log/startup-script.log)
exec 2>&1

echo "🚀 Starting VM setup for Tropical Cloud Detection..."
echo "Timestamp: $(date)"

# Update system packages
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required system packages
echo "🔧 Installing system dependencies..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    nginx \
    supervisor \
    build-essential \
    libhdf5-dev \
    libnetcdf-dev \
    pkg-config \
    postgresql-client \
    curl \
    unzip

# Install Google Cloud SDK if not present
if ! command -v gcloud &> /dev/null; then
    echo "☁️  Installing Google Cloud SDK..."
    curl https://sdk.cloud.google.com | bash
    exec -l $SHELL
    source /root/google-cloud-sdk/path.bash.inc
fi

# Create application directory
echo "📁 Setting up application directory..."
mkdir -p /opt/tropical-cloud-detection
cd /opt/tropical-cloud-detection

# Clone or update the application (you'll need to replace with your repo)
echo "📥 Setting up application code..."
# For now, we'll create a placeholder - you'll need to replace this with your actual repo
# git clone https://github.com/your-username/TropicalCloudDetection.git .

# For demo purposes, we'll copy from a mounted disk or expect the code to be uploaded
# You can upload your code manually or set up a git repository

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Create application directory structure
mkdir -p media staticfiles logs
touch logs/django.log logs/nginx.log

# Create environment file
echo "⚙️  Setting up environment configuration..."
cat > .env << EOF
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
ALLOWED_HOSTS=localhost,127.0.0.1,$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")
CORS_ALLOWED_ORIGINS=http://$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google"):8080
CSRF_TRUSTED_ORIGINS=http://$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google"):8080
GCS_BUCKET_NAME=tropical-cloud-detection-uploads
GOOGLE_CLOUD_PROJECT=$(curl -s http://metadata.google.internal/computeMetadata/v1/project/project-id -H "Metadata-Flavor: Google")
EOF

# When you upload your code, uncomment these lines:
# pip install -r requirements.txt
# python manage.py collectstatic --noinput
# python manage.py migrate

# Create systemd service
echo "🔧 Setting up systemd service..."
cat > /etc/systemd/system/tropical-cloud-detection.service << EOF
[Unit]
Description=Tropical Cloud Detection Django Application
After=network.target

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/opt/tropical-cloud-detection
Environment=PATH=/opt/tropical-cloud-detection/venv/bin
EnvironmentFile=/opt/tropical-cloud-detection/.env
ExecStart=/opt/tropical-cloud-detection/venv/bin/gunicorn \\
    --bind 127.0.0.1:8000 \\
    --workers 6 \\
    --worker-class sync \\
    --timeout 600 \\
    --max-requests 100 \\
    --max-requests-jitter 10 \\
    --preload \\
    --access-logfile /opt/tropical-cloud-detection/logs/django.log \\
    --error-logfile /opt/tropical-cloud-detection/logs/django.log \\
    cloud_detection_portal.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo "🌐 Setting up Nginx configuration..."
cat > /etc/nginx/sites-available/tropical-cloud-detection << EOF
server {
    listen 8080;
    server_name _;
    
    client_max_body_size 200M;
    client_body_timeout 600s;
    proxy_read_timeout 600s;
    proxy_connect_timeout 60s;
    proxy_send_timeout 600s;
    
    # Serve static files
    location /static/ {
        alias /opt/tropical-cloud-detection/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Serve media files
    location /media/ {
        alias /opt/tropical-cloud-detection/media/;
        expires 30d;
    }
    
    # Proxy all other requests to Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }
    
    # Health check endpoint
    location /health/ {
        proxy_pass http://127.0.0.1:8000/health/;
        access_log off;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/tropical-cloud-detection /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Create update script
echo "📝 Creating update script..."
cat > /opt/tropical-cloud-detection/deploy/update_app.sh << 'EOF'
#!/bin/bash
# Update script for the application

set -e

echo "🔄 Updating Tropical Cloud Detection application..."

cd /opt/tropical-cloud-detection

# Activate virtual environment
source venv/bin/activate

# Pull latest changes (uncomment when using git)
# git pull origin main

# Install/update dependencies
# pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Restart services
systemctl restart tropical-cloud-detection
systemctl reload nginx

echo "✅ Application updated successfully!"
EOF

chmod +x /opt/tropical-cloud-detection/deploy/update_app.sh

# Set proper permissions
chown -R root:root /opt/tropical-cloud-detection
chmod -R 755 /opt/tropical-cloud-detection

# Enable and start services
echo "🚀 Starting services..."
systemctl daemon-reload
systemctl enable tropical-cloud-detection
systemctl enable nginx

# Note: We'll start the service after the code is uploaded
# systemctl start tropical-cloud-detection
systemctl start nginx

# Create a simple status page until the app is deployed
cat > /var/www/html/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Tropical Cloud Detection - Setting Up</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        .status { background: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px; }
    </style>
</head>
<body>
    <h1>🌴 Tropical Cloud Detection</h1>
    <div class="status">
        <h2>VM Setup Complete!</h2>
        <p>The server is ready. Please upload your application code to complete the deployment.</p>
        <p>Server IP: $(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")</p>
        <p>Time: $(date)</p>
    </div>
</body>
</html>
EOF

echo "✅ VM startup script completed!"
echo "📊 Setup Summary:"
echo "  - System packages installed"
echo "  - Python environment configured"
echo "  - Nginx configured and running on port 8080"
echo "  - Systemd service created (ready to start after code upload)"
echo "  - Application directory: /opt/tropical-cloud-detection"
echo ""
echo "📝 Next steps:"
echo "  1. Upload your application code to /opt/tropical-cloud-detection"
echo "  2. Install dependencies: pip install -r requirements.txt"
echo "  3. Run migrations: python manage.py migrate"
echo "  4. Collect static files: python manage.py collectstatic --noinput"
echo "  5. Start the application: systemctl start tropical-cloud-detection"
echo ""
echo "🔗 Access your application at: http://$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google"):8080" 