#!/bin/bash
# Deploy application to Google Compute Engine
# This script uploads your code and configures the application

set -e

# Configuration
PROJECT_ID=${1:-"tropical-cloud-detection"}
INSTANCE_NAME=${2:-"tropical-cloud-app"}
ZONE=${3:-"asia-southeast1-a"}

echo "🚀 Deploying Tropical Cloud Detection to Compute Engine..."
echo "Project: $PROJECT_ID"
echo "Instance: $INSTANCE_NAME"
echo "Zone: $ZONE"

# Check if instance exists
if ! gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID &>/dev/null; then
    echo "❌ Instance $INSTANCE_NAME not found in zone $ZONE"
    echo "Please run the setup script first: ./deploy/compute_engine_setup.sh"
    exit 1
fi

# Get instance IP
EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME \
    --zone=$ZONE \
    --project=$PROJECT_ID \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo "🌐 Instance IP: $EXTERNAL_IP"

# Create temporary deployment package
echo "📦 Creating deployment package..."
TEMP_DIR=$(mktemp -d)
rsync -av --progress \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='db.sqlite3' \
    --exclude='media/*' \
    --exclude='staticfiles/*' \
    --exclude='temp_gcs_credentials.json' \
    ./ $TEMP_DIR/

# Create production environment file
echo "⚙️  Creating production environment file..."
cat > $TEMP_DIR/.env.production << EOF
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
ALLOWED_HOSTS=localhost,127.0.0.1,$EXTERNAL_IP
CORS_ALLOWED_ORIGINS=http://$EXTERNAL_IP:8080
CSRF_TRUSTED_ORIGINS=http://$EXTERNAL_IP:8080
GCS_BUCKET_NAME=tropical-cloud-detection-uploads
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
# File upload settings - optimized for 50-100MB files
FILE_UPLOAD_MAX_MEMORY_SIZE=209715200
DATA_UPLOAD_MAX_MEMORY_SIZE=209715200
DATA_UPLOAD_MAX_NUMBER_FIELDS=1000
FILE_UPLOAD_TIMEOUT=300
EOF

echo "📤 Uploading application to VM..."
gcloud compute scp --recurse $TEMP_DIR/* $INSTANCE_NAME:/opt/tropical-cloud-detection/ \
    --zone=$ZONE \
    --project=$PROJECT_ID

echo "🔧 Setting up application on VM..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID --command="
    set -e
    cd /opt/tropical-cloud-detection
    
    # Copy production environment
    cp .env.production .env
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/update dependencies
    echo '📦 Installing Python dependencies...'
    pip install --no-cache-dir -r requirements.txt
    
    # Set proper permissions
    chown -R root:root /opt/tropical-cloud-detection
    chmod -R 755 /opt/tropical-cloud-detection
    
    # Run Django setup
    echo '🗄️  Running database migrations...'
    python manage.py migrate
    
    echo '📁 Collecting static files...'
    python manage.py collectstatic --noinput
    
    # Start the application
    echo '🚀 Starting application service...'
    systemctl restart tropical-cloud-detection
    systemctl reload nginx
    
    # Check service status
    sleep 5
    systemctl status tropical-cloud-detection --no-pager
    
    echo '✅ Application deployed and running!'
"

# Cleanup
rm -rf $TEMP_DIR

echo ""
echo "🎉 Deployment complete!"
echo "🔗 Application URL: http://$EXTERNAL_IP:8080"
echo ""
echo "📊 Useful commands:"
echo "  SSH to instance: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID"
echo "  Check logs: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID --command='sudo journalctl -u tropical-cloud-detection -f'"
echo "  Check status: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID --command='sudo systemctl status tropical-cloud-detection'"
echo "  Update app: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID --command='cd /opt/tropical-cloud-detection && sudo ./deploy/update_app.sh'"
echo ""
echo "🔧 To redeploy after code changes, run this script again." 