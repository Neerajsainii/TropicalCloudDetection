#!/bin/bash

# Tropical Cloud Detection VM Setup Script
# Run this in Google Cloud Shell or on a machine with gcloud CLI

set -e

echo "🚀 Setting up Tropical Cloud Detection VM..."

# Configuration
PROJECT_ID="tropical-cloud-detection"
ZONE="us-central1-a"
VM_NAME="tropical-cloud-vm"
MACHINE_TYPE="e2-standard-4"
DISK_SIZE="100GB"
SERVICE_ACCOUNT="1065844967286-compute@developer.gserviceaccount.com"

# Create VM instance
echo "📦 Creating VM instance..."
gcloud compute instances create $VM_NAME \
    --project=$PROJECT_ID \
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

# Create firewall rules if they don't exist
echo "🔥 Setting up firewall rules..."
gcloud compute firewall-rules create allow-http-8000 \
    --project=$PROJECT_ID \
    --allow tcp:8000 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server \
    --description "Allow HTTP traffic on port 8000" || true

gcloud compute firewall-rules create allow-https-443 \
    --project=$PROJECT_ID \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --target-tags https-server \
    --description "Allow HTTPS traffic on port 443" || true

# Get external IP
EXTERNAL_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)")

echo "✅ VM created successfully!"
echo "🌐 External IP: $EXTERNAL_IP"
echo "🔧 Next steps:"
echo "1. SSH into the VM: gcloud compute ssh $VM_NAME --zone=$ZONE"
echo "2. Run the application setup script"
echo "3. Configure domain to point to $EXTERNAL_IP"

# Create application setup script
cat > app-setup.sh << 'EOF'
#!/bin/bash

# Application Setup Script - Run this ON the VM

set -e

echo "🔧 Setting up Tropical Cloud Detection application..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and dependencies
sudo apt-get install -y python3 python3-pip python3-venv git nginx supervisor
sudo apt-get install -y build-essential libhdf5-dev libnetcdf-dev pkg-config postgresql-client

# Create application directory
sudo mkdir -p /opt/tropical-cloud-detection
sudo chown $USER:$USER /opt/tropical-cloud-detection
cd /opt/tropical-cloud-detection

# Clone repository (you'll need to provide the git URL)
echo "📥 Please clone your repository here:"
echo "git clone <your-repo-url> ."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
cat > .env << 'ENVEOF'
ENVIRONMENT=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=*
DEBUG=False
CORS_ALLOWED_ORIGINS=*
CSRF_TRUSTED_ORIGINS=*
GOOGLE_CLOUD_PROJECT=tropical-cloud-detection
GCS_BUCKET_NAME=tropical-cloud-detection-uploads
ENVEOF

# Set up database
python manage.py migrate
python manage.py collectstatic --noinput

# Create nginx configuration
sudo tee /etc/nginx/sites-available/tropical-cloud-detection << 'NGINXEOF'
server {
    listen 80;
    server_name _;
    client_max_body_size 0;  # No upload limit
    
    location /static/ {
        alias /opt/tropical-cloud-detection/staticfiles/;
    }
    
    location /media/ {
        alias /opt/tropical-cloud-detection/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
}
NGINXEOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/tropical-cloud-detection /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Create supervisor configuration for Django
sudo tee /etc/supervisor/conf.d/tropical-cloud-detection.conf << 'SUPERVISOREOF'
[program:tropical-cloud-detection]
directory=/opt/tropical-cloud-detection
command=/opt/tropical-cloud-detection/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 cloud_detection_portal.wsgi:application
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/tropical-cloud-detection.log
environment=PATH="/opt/tropical-cloud-detection/venv/bin"
SUPERVISOREOF

# Start services
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start tropical-cloud-detection

echo "✅ Application setup complete!"
echo "🌐 Your app should be accessible at http://$(curl -s ifconfig.me)"
echo "📝 Check logs: sudo tail -f /var/log/tropical-cloud-detection.log"
echo "🔧 Manage service: sudo supervisorctl status tropical-cloud-detection"

EOF

echo "📋 Application setup script created: app-setup.sh"
echo "🚀 VM setup complete! Next steps:"
echo "1. SSH into the VM: gcloud compute ssh $VM_NAME --zone=$ZONE"
echo "2. Run: chmod +x app-setup.sh && ./app-setup.sh" 