#!/bin/bash

# Simple Deploy Script for Tropical Cloud Detection
# Uses Debian (always available) instead of Ubuntu

set -e

echo "🚀 Simple Deploy: Tropical Cloud Detection to Compute Engine"
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

# Create VM instance with Debian (always available)
echo "📦 Creating VM instance with Debian..."
gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --image-family=debian-11 \
    --image-project=debian-cloud \
    --boot-disk-size=$DISK_SIZE \
    --boot-disk-type=pd-ssd \
    --service-account=$SERVICE_ACCOUNT \
    --scopes=https://www.googleapis.com/auth/cloud-platform \
    --tags=http-server,https-server \
    --metadata=startup-script='#!/bin/bash
    apt-get update
    apt-get install -y python3 python3-pip python3-venv git curl
    echo "Basic setup complete" > /tmp/setup-done.txt'

echo "✅ VM created successfully!"

# Create firewall rules
echo "🔥 Setting up firewall rules..."
gcloud compute firewall-rules create allow-http-80 \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server \
    --description "Allow HTTP traffic on port 80" 2>/dev/null || echo "HTTP firewall rule already exists"

gcloud compute firewall-rules create allow-https-443 \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --target-tags https-server \
    --description "Allow HTTPS traffic on port 443" 2>/dev/null || echo "HTTPS firewall rule already exists"

# Get external IP
EXTERNAL_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)")

echo "✅ Firewall rules configured!"
echo "🌐 External IP: $EXTERNAL_IP"

# Wait for VM to be ready
echo "⏳ Waiting for VM to be ready..."
sleep 30

echo ""
echo "🎉 VM CREATED SUCCESSFULLY!"
echo "=================================================="
echo "🌐 VM External IP: $EXTERNAL_IP"
echo "🔧 SSH into VM: gcloud compute ssh $VM_NAME --zone=$ZONE"
echo ""
echo "📋 Next steps:"
echo "1. SSH into the VM"
echo "2. Run the application setup commands"
echo ""
echo "💡 Your VM is ready for Django deployment!" 