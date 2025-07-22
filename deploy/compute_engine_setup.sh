#!/bin/bash
# Google Compute Engine Setup Script for Tropical Cloud Detection
# This script sets up the entire environment on a fresh Ubuntu VM

set -e

# Configuration
PROJECT_ID=${1:-"tropical-cloud-detection"}
INSTANCE_NAME=${2:-"tropical-cloud-app"}
ZONE=${3:-"asia-southeast1-a"}
MACHINE_TYPE=${4:-"e2-standard-8"}  # 8 vCPUs, 32GB RAM - optimized for 50-100MB file processing
DISK_SIZE=${5:-"50GB"}

echo "🚀 Setting up Google Compute Engine deployment..."
echo "Project: $PROJECT_ID"
echo "Instance: $INSTANCE_NAME"
echo "Zone: $ZONE"
echo "Machine Type: $MACHINE_TYPE"

# Create firewall rules for HTTP/HTTPS traffic
echo "🔥 Creating firewall rules..."
gcloud compute firewall-rules create allow-http-8080 \
    --allow tcp:8080 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTP traffic on port 8080" \
    --project=$PROJECT_ID || echo "Firewall rule already exists"

gcloud compute firewall-rules create allow-https-443 \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTPS traffic on port 443" \
    --project=$PROJECT_ID || echo "Firewall rule already exists"

gcloud compute firewall-rules create allow-http-80 \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTP traffic on port 80" \
    --project=$PROJECT_ID || echo "Firewall rule already exists"

# Create the VM instance
echo "🖥️  Creating Compute Engine instance..."
gcloud compute instances create $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account=default \
    --scopes=https://www.googleapis.com/auth/devstorage.read_write,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
    --tags=http-server,https-server \
    --create-disk=auto-delete=yes,boot=yes,device-name=$INSTANCE_NAME,image=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20231213,mode=rw,size=$DISK_SIZE,type=projects/$PROJECT_ID/zones/$ZONE/diskTypes/pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=environment=production,app=tropical-cloud-detection \
    --reservation-affinity=any \
    --metadata-from-file startup-script=deploy/vm_startup.sh

echo "✅ Compute Engine instance created successfully!"
echo "🌐 Getting external IP..."

# Get the external IP
EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME \
    --zone=$ZONE \
    --project=$PROJECT_ID \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo "🎉 Setup complete!"
echo "📍 Instance: $INSTANCE_NAME"
echo "🌐 External IP: $EXTERNAL_IP"
echo "🔗 Application URL: http://$EXTERNAL_IP:8080"
echo ""
echo "📝 Next steps:"
echo "1. Wait for the startup script to complete (5-10 minutes)"
echo "2. SSH to the instance: gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID"
echo "3. Check application status: sudo systemctl status tropical-cloud-detection"
echo "4. View logs: sudo journalctl -u tropical-cloud-detection -f"
echo ""
echo "🔧 To update the application later:"
echo "   gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID"
echo "   cd /opt/tropical-cloud-detection && sudo ./deploy/update_app.sh" 