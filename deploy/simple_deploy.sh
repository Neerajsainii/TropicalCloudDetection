#!/bin/bash
set -e
set -x

echo "🚀 Starting simple deployment..."

# Get VM external IP
EXTERNAL_IP=$(gcloud compute instances describe tropical-cloud-app --zone=asia-southeast1-a --format="value(networkInterfaces[0].accessConfigs[0].natIP)")

echo "📦 Creating deployment package..."
tar -czf app.tar.gz --exclude='.git' --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env*' --exclude='db.sqlite3*' --exclude='media' --exclude='staticfiles' --exclude='key.json' --exclude='gcp-github-actions*' --warning=no-file-changed .

echo "📤 Uploading to VM..."
gcloud compute scp app.tar.gz tropical-cloud-app:/tmp/app.tar.gz --zone=asia-southeast1-a

echo "🔧 Setting up VM..."
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="sudo mkdir -p /opt/tropical-cloud-detection"

echo "📂 Extracting files..."
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="cd /opt/tropical-cloud-detection && sudo tar -xzf /tmp/app.tar.gz"

echo "🐍 Installing Python dependencies..."
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv nginx build-essential libhdf5-dev libnetcdf-dev pkg-config"

echo "🔧 Creating virtual environment..."
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="cd /opt/tropical-cloud-detection && sudo python3 -m venv venv"

echo "📦 Installing Python packages..."
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="cd /opt/tropical-cloud-detection && source venv/bin/activate && sudo venv/bin/pip install -r requirements.txt"

echo "🗄️ Running database migrations..."
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="cd /opt/tropical-cloud-detection && source venv/bin/activate && sudo venv/bin/python manage.py migrate"

echo "📁 Collecting static files..."
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="cd /opt/tropical-cloud-detection && source venv/bin/activate && sudo venv/bin/python manage.py collectstatic --noinput"

echo "🛑 Stopping any existing processes..."
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="sudo pkill -f gunicorn || true"

echo "🚀 Starting Gunicorn..."
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="cd /opt/tropical-cloud-detection && source venv/bin/activate && nohup sudo venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 600 cloud_detection_portal.wsgi:application > gunicorn.log 2>&1 &"

echo "⏳ Waiting for Gunicorn to start..."
sleep 10

echo "🔍 Checking if Gunicorn is running..."
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="ps aux | grep gunicorn"

echo "🌐 Setting up Nginx..."
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="echo 'server {
    listen 8080;
    server_name _;
    client_max_body_size 200M;
    
    location /static/ {
        alias /opt/tropical-cloud-detection/staticfiles/;
    }
    
    location /media/ {
        alias /opt/tropical-cloud-detection/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}' | sudo tee /etc/nginx/sites-available/tropical-cloud-detection"

echo "🔗 Enabling Nginx site..."
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="sudo ln -sf /etc/nginx/sites-available/tropical-cloud-detection /etc/nginx/sites-enabled/"

echo "🗑️ Removing default Nginx site..."
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="sudo rm -f /etc/nginx/sites-enabled/default"

echo "🔄 Restarting Nginx..."
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="sudo systemctl restart nginx"

echo "⏳ Waiting for services to start..."
sleep 5

echo "🔍 Testing application..."
curl -f http://$EXTERNAL_IP:8080/ || echo "❌ Application not responding"

echo "✅ Deployment completed!"
echo "🌐 Application URL: http://$EXTERNAL_IP:8080"
echo "📊 Gunicorn logs: ssh tropical-cloud-app 'tail -f /opt/tropical-cloud-detection/gunicorn.log'" 