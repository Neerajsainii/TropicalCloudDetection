#!/bin/bash

# Cloud Run Deployment Script for Tropical Cloud Detection
# This script deploys the application to Google Cloud Run with high-performance settings

set -e

echo "🚀 Deploying Tropical Cloud Detection to Cloud Run"
echo "=================================================="

# Configuration
PROJECT_ID="tropical-cloud-detection"
SERVICE_NAME="tropical-cloud-detection"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com

# Create GCS bucket if it doesn't exist
echo "📦 Setting up Google Cloud Storage..."
BUCKET_NAME="tropical-cloud-detection-uploads"
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME 2>/dev/null || echo "Bucket already exists"

# Make bucket public for uploads
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

# Build and deploy to Cloud Run
echo "🏗️ Building and deploying application..."

# Deploy with high-performance configuration
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --cpu 4 \
  --memory 16Gi \
  --concurrency 1 \
  --min-instances 1 \
  --max-instances 10 \
  --timeout 900 \
  --set-env-vars ENVIRONMENT=production,DEBUG=False,GCS_BUCKET_NAME=$BUCKET_NAME,GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
  --port 8080

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "✅ Deployment complete!"
echo "🌐 Your application is live at: $SERVICE_URL"
echo ""
echo "📊 Performance Configuration:"
echo "   - CPU: 4 vCPUs"
echo "   - Memory: 16GB"
echo "   - Concurrency: 1 (CPU-intensive processing)"
echo "   - Min instances: 1 (always ready)"
echo "   - Max instances: 10 (auto-scaling)"
echo "   - Timeout: 15 minutes"
echo ""
echo "💾 Storage:"
echo "   - GCS Bucket: gs://$BUCKET_NAME"
echo "   - Upload limit: 32MB per request (use GCS for larger files)"
echo ""
echo "🔧 Next steps:"
echo "   1. Test the application at: $SERVICE_URL"
echo "   2. Monitor performance in Cloud Console"
echo "   3. Set up custom domain if needed"
echo "   4. Configure monitoring and alerts" 