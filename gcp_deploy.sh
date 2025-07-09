#!/bin/bash
# Google Cloud Platform Deployment Script
# This script sets up and deploys the Tropical Cloud Detection app to GCP

set -e

echo "🚀 Starting Google Cloud Platform Deployment..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK not found. Please install it first:"
    echo "https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with Google Cloud. Please run:"
    echo "gcloud auth login"
    exit 1
fi

# Set project variables
PROJECT_ID="tropical-cloud-detection"
REGION="us-central1"
ZONE="us-central1-a"
INSTANCE_NAME="tropical-cloud-vm"
DB_INSTANCE_NAME="tropical-cloud-db"

echo "📋 Project Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Zone: $ZONE"
echo "  VM Instance: $INSTANCE_NAME"
echo "  Database Instance: $DB_INSTANCE_NAME"

# Set the project
echo "🔧 Setting up Google Cloud project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable compute.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable appengine.googleapis.com

# Create PostgreSQL instance
echo "🗄️ Creating PostgreSQL instance..."
gcloud sql instances create $DB_INSTANCE_NAME \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB \
    --backup-start-time="02:00" \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=02

# Create database
echo "📊 Creating database..."
gcloud sql databases create tropical_cloud_db \
    --instance=$DB_INSTANCE_NAME

# Create database user
echo "👤 Creating database user..."
gcloud sql users create cloud_user \
    --instance=$DB_INSTANCE_NAME \
    --password=cloudpass123

# Get database connection info
DB_HOST=$(gcloud sql instances describe $DB_INSTANCE_NAME --format="value(connectionName)")
echo "📡 Database host: $DB_HOST"

# Create Compute Engine instance
echo "🖥️ Creating Compute Engine instance..."
gcloud compute instances create $INSTANCE_NAME \
    --zone=$ZONE \
    --machine-type=e2-standard-2 \
    --image-family=debian-11 \
    --image-project=debian-cloud \
    --boot-disk-size=50GB \
    --boot-disk-type=pd-standard \
    --tags=http-server,https-server \
    --metadata=startup-script='#! /bin/bash
# Install required packages
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx postgresql-client

# Create application directory
mkdir -p /opt/tropical-cloud
cd /opt/tropical-cloud

# Clone or copy application files here
# (You would need to upload your code or clone from a repository)

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'cloudadmin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell

# Set up Gunicorn service
cat > /etc/systemd/system/tropical-cloud.service << EOF
[Unit]
Description=Tropical Cloud Detection App
After=network.target

[Service]
User=root
WorkingDirectory=/opt/tropical-cloud
Environment="PATH=/opt/tropical-cloud/venv/bin"
ExecStart=/opt/tropical-cloud/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 cloud_detection_portal.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start the service
systemctl enable tropical-cloud
systemctl start tropical-cloud

# Configure Nginx
cat > /etc/nginx/sites-available/tropical-cloud << EOF
server {
    listen 80;
    server_name _;

    location /static/ {
        alias /opt/tropical-cloud/staticfiles/;
    }

    location /media/ {
        alias /opt/tropical-cloud/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/tropical-cloud /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx'

# Create firewall rules
echo "🔥 Creating firewall rules..."
gcloud compute firewall-rules create allow-http \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server

gcloud compute firewall-rules create allow-https \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --target-tags https-server

# Get instance external IP
EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --format="value(networkInterfaces[0].accessConfigs[0].natIP)")

echo "✅ Deployment completed!"
echo ""
echo "🌐 Your application is available at:"
echo "  http://$EXTERNAL_IP"
echo ""
echo "📊 Database connection details:"
echo "  Host: $DB_HOST"
echo "  Database: tropical_cloud_db"
echo "  User: cloud_user"
echo "  Password: cloudpass123"
echo ""
echo "🔧 Next steps:"
echo "  1. Upload your application code to the VM"
echo "  2. Update settings.py with database connection"
echo "  3. Set up environment variables"
echo "  4. Restart the application service"
echo ""
echo "📝 To connect to the VM:"
echo "  gcloud compute ssh $INSTANCE_NAME --zone=$ZONE" 