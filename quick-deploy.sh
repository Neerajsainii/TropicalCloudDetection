#!/bin/bash

# Quick Deploy Script for Tropical Cloud Detection
# Run this in Google Cloud Shell

set -e

echo "🚀 Quick Deploy: Tropical Cloud Detection to Compute Engine"
echo "=================================================="

# Configuration
PROJECT_ID="tropical-cloud-detection"
ZONE="us-central1-a"
VM_NAME="tropical-cloud-vm"
MACHINE_TYPE="e2-standard-4"
DISK_SIZE="100"
SERVICE_ACCOUNT="1065844967286-compute@developer.gserviceaccount.com"

# Set project
gcloud config set project $PROJECT_ID

# Create VM instance
echo "📦 Creating VM instance..."
gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account=$SERVICE_ACCOUNT \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=http-server,https-server \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=$DISK_SIZE \
    --boot-disk-type=pd-ssd \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=app=tropical-cloud-detection \
    --reservation-affinity=any

echo "✅ VM created successfully!"

# Create firewall rules
echo "🔥 Setting up firewall rules..."
gcloud compute firewall-rules create allow-http-8000 \
    --allow tcp:8000 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server \
    --description "Allow HTTP traffic on port 8000" 2>/dev/null || echo "Firewall rule already exists"

gcloud compute firewall-rules create allow-https-443 \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --target-tags https-server \
    --description "Allow HTTPS traffic on port 443" 2>/dev/null || echo "Firewall rule already exists"

# Get external IP
EXTERNAL_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)")

echo "✅ Firewall rules configured!"
echo "🌐 External IP: $EXTERNAL_IP"

# Create the application setup script on the VM
echo "📝 Creating application setup script..."
cat > vm-app-setup.sh << 'EOF'
#!/bin/bash

# Application Setup Script - Runs ON the VM
set -e

echo "🔧 Setting up Tropical Cloud Detection application..."

# Update system
sudo apt-get update -y
sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install -y \
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
    wget \
    unzip

# Create application directory
sudo mkdir -p /opt/tropical-cloud-detection
sudo chown $USER:$USER /opt/tropical-cloud-detection
cd /opt/tropical-cloud-detection

# Create a simple Django project structure for now
echo "📁 Setting up project structure..."
python3 -m venv venv
source venv/bin/activate

# Install basic Django and dependencies
pip install --upgrade pip
pip install django gunicorn psycopg2-binary python-decouple django-cors-headers whitenoise

# Create basic requirements.txt
cat > requirements.txt << 'REQEOF'
Django>=4.2.0
gunicorn>=21.2.0
psycopg2-binary>=2.9.0
python-decouple>=3.8
django-cors-headers>=4.0.0
whitenoise>=6.5.0
h5py>=3.8.0
netCDF4>=1.6.0
numpy>=1.24.0
scikit-image>=0.21.0
psutil>=5.9.0
google-cloud-storage>=2.10.0
REQEOF

pip install -r requirements.txt

# Create basic environment file
cat > .env << 'ENVEOF'
ENVIRONMENT=production
SECRET_KEY=django-insecure-temp-key-change-this-in-production
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=*
DEBUG=False
CORS_ALLOWED_ORIGINS=*
CSRF_TRUSTED_ORIGINS=*
GOOGLE_CLOUD_PROJECT=tropical-cloud-detection
GCS_BUCKET_NAME=tropical-cloud-detection-uploads
ENVEOF

# Create nginx configuration
sudo tee /etc/nginx/sites-available/tropical-cloud-detection << 'NGINXEOF'
server {
    listen 80;
    server_name _;
    client_max_body_size 0;  # No upload limit - this is the key!
    
    location /static/ {
        alias /opt/tropical-cloud-detection/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /opt/tropical-cloud-detection/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 600;
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        client_max_body_size 0;  # No upload limit here too
    }
}
NGINXEOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/tropical-cloud-detection /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Create supervisor configuration
sudo tee /etc/supervisor/conf.d/tropical-cloud-detection.conf << 'SUPERVISOREOF'
[program:tropical-cloud-detection]
directory=/opt/tropical-cloud-detection
command=/opt/tropical-cloud-detection/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 --timeout 600 cloud_detection_portal.wsgi:application
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/tropical-cloud-detection.log
stderr_logfile=/var/log/tropical-cloud-detection-error.log
environment=PATH="/opt/tropical-cloud-detection/venv/bin"
SUPERVISOREOF

# Create media and static directories
mkdir -p media staticfiles
sudo chown -R www-data:www-data /opt/tropical-cloud-detection

echo "✅ Basic setup complete!"
echo "🌐 Your VM is ready at: http://$(curl -s ifconfig.me)"
echo ""
echo "🔧 Next steps:"
echo "1. Clone your repository: git clone <your-repo-url> /tmp/app && cp -r /tmp/app/* /opt/tropical-cloud-detection/"
echo "2. Install your requirements: source venv/bin/activate && pip install -r requirements.txt"
echo "3. Run migrations: python manage.py migrate"
echo "4. Collect static files: python manage.py collectstatic --noinput"
echo "5. Start services: sudo supervisorctl reread && sudo supervisorctl update && sudo supervisorctl start tropical-cloud-detection"
echo ""
echo "📝 Check logs: sudo tail -f /var/log/tropical-cloud-detection.log"
echo "🔧 Manage service: sudo supervisorctl status tropical-cloud-detection"

EOF

# Copy the setup script to the VM
echo "📤 Copying setup script to VM..."
gcloud compute scp vm-app-setup.sh $VM_NAME:/tmp/vm-app-setup.sh --zone=$ZONE

# Run the setup script on the VM
echo "🚀 Running setup script on VM..."
gcloud compute ssh $VM_NAME --zone=$ZONE --command="chmod +x /tmp/vm-app-setup.sh && /tmp/vm-app-setup.sh"

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "=================================================="
echo "🌐 Your VM is accessible at: http://$EXTERNAL_IP"
echo "🔧 SSH into VM: gcloud compute ssh $VM_NAME --zone=$ZONE"
echo ""
echo "📋 Final steps to complete:"
echo "1. SSH into the VM and clone your actual repository"
echo "2. Update the .env file with your actual SECRET_KEY"
echo "3. Run Django migrations and collect static files"
echo "4. Start the application service"
echo ""
echo "💡 Your app will now support unlimited file uploads!"
echo "No more 32MB limits! 🎊" 