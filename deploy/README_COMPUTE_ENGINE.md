# Google Compute Engine Deployment Guide

This guide helps you migrate your Tropical Cloud Detection application from Google Cloud Run to Google Compute Engine to process **50-100MB files in 30-40 seconds** without memory limitations.

## 🎯 Optimized Configuration

**Your application is now optimized for:**
- **File Size**: Up to 200MB (handles your 50-100MB files comfortably)
- **Processing Time**: 30-40 seconds with 10-minute timeout for safety
- **Machine Type**: `e2-standard-8` (8 vCPUs, 32GB RAM) for fast processing
- **Workers**: 6 Gunicorn workers for parallel processing
- **Memory**: No more 32MB Cloud Run limitations!

## 🔧 Prerequisites

1. **Google Cloud SDK** installed and configured
2. **Project setup** with billing enabled
3. **Required APIs enabled**:
   ```bash
   gcloud services enable compute.googleapis.com
   gcloud services enable storage.googleapis.com
   ```

## 🚀 Quick Deployment

### Step 1: Create and Configure VM (Windows - PowerShell)

```powershell
# Run the migration script with optimized settings for your use case
.\deploy\migrate_to_compute_engine.ps1

# Or with custom project settings:
.\deploy\migrate_to_compute_engine.ps1 -ProjectId "your-project-id"
```

### Step 2: Alternative - Manual Steps (Linux/Mac)

```bash
# Make scripts executable
chmod +x deploy/*.sh

# Create VM instance with optimized settings
./deploy/compute_engine_setup.sh

# Deploy your application
./deploy/deploy_to_vm.sh
```

## ⚡ Performance Specifications

### Optimized Machine Configuration

| Component | Specification | Purpose |
|-----------|---------------|---------|
| **vCPUs** | 8 cores | Fast parallel processing of large files |
| **Memory** | 32GB RAM | Handle 50-100MB files + scientific computing |
| **Workers** | 6 Gunicorn workers | Process multiple files simultaneously |
| **Timeout** | 600 seconds | 10x safety margin for 30-40s processing |
| **Upload Limit** | 200MB | 2x your max file size for safety |

### Processing Capabilities

| Metric | Cloud Run | Compute Engine (Optimized) |
|--------|-----------|----------------------------|
| **File Size Limit** | 32MB | 200MB |
| **Processing Time** | 60 min max | Unlimited |
| **Target Processing** | Not suitable | **30-40 seconds** |
| **Memory Available** | Limited | 32GB RAM |
| **CPU Cores** | Limited | 8 dedicated cores |
| **Parallel Processing** | Limited | 6 concurrent workers |

## 🔍 Environment Configuration

The deployment automatically creates an optimized `.env` file:

```env
ENVIRONMENT=production
DEBUG=False

# Optimized for 50-100MB file processing
FILE_UPLOAD_MAX_MEMORY_SIZE=209715200  # 200MB
DATA_UPLOAD_MAX_MEMORY_SIZE=209715200  # 200MB
FILE_UPLOAD_TIMEOUT=300                # 5 minutes

# High-performance worker settings
GUNICORN_WORKERS=6
GUNICORN_TIMEOUT=600
GUNICORN_MAX_REQUESTS=100
```

## 🌐 Access Your Application

After deployment:
- **Main Application**: `http://<VM_IP>:8080`
- **Admin Panel**: `http://<VM_IP>:8080/admin/`
- **Health Check**: `http://<VM_IP>:8080/health/`

## 📊 Monitoring and Management

### Check Performance

```bash
# SSH to your instance
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a

# Monitor real-time performance
htop

# Check memory usage during processing
free -h

# Monitor application logs
sudo journalctl -u tropical-cloud-detection -f

# Check worker processes
ps aux | grep gunicorn
```

### Performance Optimization Commands

```bash
# Check application status
sudo systemctl status tropical-cloud-detection

# Restart for configuration changes
sudo systemctl restart tropical-cloud-detection

# Monitor nginx performance
sudo systemctl status nginx
```

## 🔧 Processing Workflow Optimization

### For Your 50-100MB Files:

1. **Upload**: Files up to 200MB supported
2. **Processing**: 6 workers handle requests in parallel
3. **Memory**: 32GB available for scientific computations
4. **Timeout**: 10 minutes safety buffer for 30-40s processing
5. **CPU**: 8 cores for intensive calculations

### Recommended File Processing Strategy:

```python
# Example optimization in your processing code
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

def process_large_file(file_path):
    # Your existing processing logic
    # Now has access to much more memory and CPU
    pass

# Use multiple cores for even faster processing
def parallel_process(file_chunks):
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = executor.map(process_large_file, file_chunks)
    return list(results)
```

## 🛠️ Troubleshooting

### Performance Issues

#### 1. **Processing takes longer than 30-40 seconds**
```bash
# Check CPU usage
top
# Check memory usage during processing
watch -n 1 free -h
# Optimize your algorithms or increase machine size
```

#### 2. **Memory issues with large files**
```bash
# Monitor memory during upload/processing
sudo journalctl -u tropical-cloud-detection -f | grep -i memory
# Consider upgrading to e2-highmem-8 for more RAM
```

#### 3. **Upload timeouts**
```bash
# Check nginx logs
sudo tail -f /var/log/nginx/error.log
# Verify file size limits
curl -X POST -F "file=@large_file.dat" http://your-ip:8080/upload/
```

### Quick Fixes

```bash
# Restart services
sudo systemctl restart tropical-cloud-detection nginx

# Check disk space
df -h

# Monitor real-time processing
sudo tail -f /opt/tropical-cloud-detection/logs/django.log
```

## 📈 Scaling for Even Better Performance

### Option 1: Upgrade Machine Type
```bash
# Stop instance
gcloud compute instances stop tropical-cloud-app --zone=us-central1-a

# Change machine type for more power
gcloud compute instances set-machine-type tropical-cloud-app \
    --machine-type=e2-highmem-8 \
    --zone=us-central1-a

# Start instance
gcloud compute instances start tropical-cloud-app --zone=us-central1-a
```

### Option 2: Add GPU Acceleration (for ML workloads)
```bash
# Create GPU-enabled instance for AI/ML processing
gcloud compute instances create tropical-cloud-gpu \
    --zone=us-central1-a \
    --machine-type=n1-standard-4 \
    --accelerator=type=nvidia-tesla-t4,count=1
```

## 💰 Cost Estimation

**Monthly cost for e2-standard-8 (us-central1):**
- **Running 24/7**: ~$200-250/month
- **Running 8hrs/day**: ~$65-85/month
- **Running only when needed**: ~$0.30/hour

**Cost comparison vs Cloud Run:**
- Much more predictable costs
- Better performance for your use case
- No cold start delays

## 🔐 Security & Production Readiness

### Recommended for Production:

1. **Enable HTTPS**:
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

2. **Set up monitoring**:
   ```bash
   # Install monitoring agent
   curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
   sudo bash add-google-cloud-ops-agent-repo.sh --also-install
   ```

3. **Regular backups**:
   ```bash
   # Backup application data
   gcloud compute disks snapshot tropical-cloud-app \
       --zone=us-central1-a \
       --snapshot-names=backup-$(date +%Y%m%d)
   ```

## 🎯 Your Migration Benefits

| Aspect | Before (Cloud Run) | After (Compute Engine) |
|--------|-------------------|------------------------|
| **File Size** | 32MB limit ❌ | 200MB capacity ✅ |
| **Processing Speed** | Slow, limited resources ❌ | **30-40 seconds** ✅ |
| **Memory** | Very limited ❌ | 32GB available ✅ |
| **CPU Power** | Shared, limited ❌ | 8 dedicated cores ✅ |
| **Reliability** | Cold starts ❌ | Always warm ✅ |
| **Cost Predictability** | Variable ❌ | Fixed hourly rate ✅ |

## 📞 Support

Your application is now optimized for processing 50-100MB files in 30-40 seconds! 

If you need further optimization:
1. Monitor actual processing times
2. Check resource usage during peak loads
3. Consider GPU acceleration for ML workloads
4. Scale machine type up or down based on actual needs

🎉 **Enjoy your high-performance cloud detection processing!** 