# Tropical Cloud Detection - Google Cloud Platform Deployment

This guide will help you deploy the Tropical Cloud Detection application on Google Cloud Platform with PostgreSQL database.

## 🚀 Quick Start

### Prerequisites

1. **Google Cloud Account** with free credits
2. **Google Cloud SDK** installed and configured
3. **Python 3.9+** for local development
4. **PostgreSQL** (handled by Google Cloud SQL)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd TropicalCloudDetection
   ```

2. **Set up local environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure for GCP**
   ```bash
   python gcp_setup.py
   ```

## 🗄️ Database Setup

### Option 1: Google Cloud SQL (Recommended)

1. **Create PostgreSQL instance**
   ```bash
   gcloud sql instances create tropical-cloud-db \
       --database-version=POSTGRES_14 \
       --tier=db-f1-micro \
       --region=us-central1 \
       --storage-type=SSD \
       --storage-size=20GB
   ```

2. **Create database and user**
   ```bash
   gcloud sql databases create tropical_cloud_db --instance=tropical-cloud-db
   gcloud sql users create cloud_user --instance=tropical-cloud-db --password=your-secure-password
   ```

3. **Get connection details**
   ```bash
   gcloud sql instances describe tropical-cloud-db --format="value(connectionName)"
   ```

### Option 2: Local PostgreSQL (Development)

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create database**
   ```bash
   sudo -u postgres createdb tropical_cloud_db
   sudo -u postgres createuser cloud_user
   sudo -u postgres psql -c "ALTER USER cloud_user PASSWORD 'your-password';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE tropical_cloud_db TO cloud_user;"
   ```

## 🌐 Deployment Options

### Option 1: Google Cloud Run (Recommended)

1. **Build and deploy**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/tropical-cloud-detection
   gcloud run deploy tropical-cloud-detection \
    --image gcr.io/PROJECT_ID/tropical-cloud-detection \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 3Gi \
    --cpu 2 \
    --timeout 300
   ```

### Option 2: Google App Engine

1. **Deploy to App Engine**
   ```bash
   gcloud app deploy app.yaml
   ```

### Option 3: Compute Engine VM

1. **Run the deployment script**
   ```bash
   chmod +x gcp_deploy.sh
   ./gcp_deploy.sh
   ```

2. **Upload your code to the VM**
   ```bash
   gcloud compute scp --recurse . INSTANCE_NAME:/opt/tropical-cloud --zone=ZONE
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Environment
ENVIRONMENT=production
DEBUG=False

# Database
DATABASE_URL=postgresql://cloud_user:password@host:5432/tropical_cloud_db

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,your-vm-ip

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com

# CSRF
CSRF_TRUSTED_ORIGINS=https://your-domain.com

# Google Cloud Storage (optional)
GS_BUCKET_NAME=tropical-cloud-media
GS_STATIC_BUCKET_NAME=tropical-cloud-static
```

### Google Cloud Storage Setup (Optional)

For better performance with large satellite files:

1. **Create storage buckets**
   ```bash
   gsutil mb gs://tropical-cloud-media
   gsutil mb gs://tropical-cloud-static
   ```

2. **Make buckets public**
   ```bash
   gsutil iam ch allUsers:objectViewer gs://tropical-cloud-media
   gsutil iam ch allUsers:objectViewer gs://tropical-cloud-static
   ```

## 📊 Monitoring and Logging

### Cloud Logging

The application automatically logs to Google Cloud Logging:

```bash
# View application logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# View database logs
gcloud logging read "resource.type=cloudsql_database" --limit=50
```

### Monitoring

Set up monitoring in Google Cloud Console:

1. **Enable Cloud Monitoring API**
2. **Create custom dashboards**
3. **Set up alerts for errors**

## 🔒 Security

### SSL/TLS

- **Cloud Run**: Automatic SSL termination
- **App Engine**: Automatic SSL termination
- **Compute Engine**: Configure Nginx with Let's Encrypt

### Database Security

1. **Use Cloud SQL Proxy for local development**
   ```bash
   gcloud sql connect tropical-cloud-db --user=cloud_user
   ```

2. **Restrict database access**
   ```bash
   gcloud sql instances patch tropical-cloud-db \
       --authorized-networks=YOUR_VM_IP/32
   ```

## 🚀 Performance Optimization

### Database Optimization

1. **Enable connection pooling**
2. **Use read replicas for heavy queries**
3. **Optimize indexes for satellite data queries**

### Application Optimization

1. **Enable caching with Redis**
2. **Use CDN for static files**
3. **Implement file upload chunking for large files**

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check DATABASE_URL format
   - Verify network connectivity
   - Ensure database user permissions

2. **File Upload Timeouts**
   - Increase timeout settings
   - Use chunked uploads
   - Consider Google Cloud Storage

3. **Memory Issues**
   - Increase instance memory
   - Optimize image processing
   - Use streaming for large files

### Debug Commands

```bash
# Check application status
gcloud app logs tail -s default

# Check database connectivity
gcloud sql connect tropical-cloud-db

# Monitor resource usage
gcloud compute instances describe INSTANCE_NAME --zone=ZONE
```

## 📈 Scaling

### Horizontal Scaling

- **Cloud Run**: Automatic scaling based on requests
- **App Engine**: Automatic scaling with custom settings
- **Compute Engine**: Manual scaling with load balancer

### Vertical Scaling

- **Database**: Upgrade to higher tier
- **Application**: Increase CPU/memory allocation
- **Storage**: Use Cloud Storage for large files

## 💰 Cost Optimization

### Free Tier Usage

- **Cloud Run**: 2 million requests/month free
- **Cloud SQL**: db-f1-micro instance free
- **Cloud Storage**: 5GB free storage
- **App Engine**: 28 instance hours/day free

### Cost Monitoring

```bash
# View current costs
gcloud billing accounts list

# Set up billing alerts
gcloud alpha billing budgets create
```

## 📚 Additional Resources

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Django on Google Cloud](https://cloud.google.com/python/django)
- [PostgreSQL on Cloud SQL](https://cloud.google.com/sql/docs/postgres)
- [Cloud Run Best Practices](https://cloud.google.com/run/docs/best-practices)

## 🤝 Support

For issues specific to this deployment:

1. Check the troubleshooting section above
2. Review Google Cloud logs
3. Test locally with the same configuration
4. Contact the development team

---

**Note**: This deployment is optimized for Google Cloud Platform's free tier and production workloads. Adjust resource allocations based on your specific needs and usage patterns. 