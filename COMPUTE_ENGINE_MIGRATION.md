# 🚀 Compute Engine Migration Guide

## Overview
Migrating from Cloud Run to Compute Engine E2-Standard-4 to eliminate 32MB upload limits and improve performance.

## 💰 Cost Comparison
- **Cloud Run**: ~$50-100/month (variable based on usage)
- **Compute Engine E2-Standard-4**: $97.83/month (fixed cost)
- **Benefits**: No upload limits, better performance, predictable costs

## 🔧 Migration Steps

### Step 1: Create VM Instance
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Open **Cloud Shell** (terminal icon in top bar)
3. Upload and run the setup script:

```bash
# Upload vm-setup.sh to Cloud Shell
# Then run:
chmod +x vm-setup.sh
./vm-setup.sh
```

### Step 2: Deploy Application
1. SSH into the new VM:
```bash
gcloud compute ssh tropical-cloud-vm --zone=us-central1-a
```

2. Clone your repository:
```bash
cd /opt/tropical-cloud-detection
git clone https://github.com/yourusername/TropicalCloudDetection.git .
```

3. Run the application setup:
```bash
chmod +x app-setup.sh
./app-setup.sh
```

### Step 3: Configure Environment
Edit the `.env` file with your actual values:
```bash
sudo nano /opt/tropical-cloud-detection/.env
```

Update these values:
```env
SECRET_KEY=your-actual-secret-key
ALLOWED_HOSTS=your-domain.com,your-vm-ip
CORS_ALLOWED_ORIGINS=https://your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

### Step 4: Update DNS
1. Get your VM's external IP:
```bash
gcloud compute instances describe tropical-cloud-vm --zone=us-central1-a --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```

2. Update your domain's DNS A record to point to this IP

### Step 5: Set Up SSL (Optional but Recommended)
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🎯 Key Advantages After Migration

### ✅ **Upload Improvements**
- **No 32MB limit**: Upload files of any size directly
- **Better performance**: No need for GCS workaround
- **Simpler code**: Remove complex signed URL logic

### ✅ **Performance Benefits**
- **4 vCPUs**: Better processing power
- **16GB RAM**: Handle multiple concurrent uploads
- **Persistent storage**: 100GB SSD for files
- **Predictable performance**: No cold starts

### ✅ **Cost Benefits**
- **Fixed monthly cost**: $97.83/month
- **No per-request charges**: Unlimited requests
- **Better value**: More resources for sustained workloads

## 🔄 Code Changes Required

### 1. Simplify Upload Logic
Remove the complex GCS upload logic and use direct file uploads:

```python
# In views.py - Simplify upload_file view
def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            # Direct file handling - no size limits!
            satellite_data = SatelliteData.objects.create(
                file=uploaded_file,
                # ... other fields
            )
            # Process directly
            return JsonResponse({'success': True})
```

### 2. Update Frontend
Remove progress bar complexity for large files:

```javascript
// Simplified upload - no need for signed URLs
const formData = new FormData();
formData.append('file', selectedFile);

fetch('/upload/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    // Handle success
});
```

### 3. Nginx Configuration
The nginx config automatically handles large uploads:
```nginx
client_max_body_size 0;  # No upload limit
```

## 📊 Monitoring and Maintenance

### Check Application Status
```bash
# Check if app is running
sudo supervisorctl status tropical-cloud-detection

# View logs
sudo tail -f /var/log/tropical-cloud-detection.log

# Restart app
sudo supervisorctl restart tropical-cloud-detection
```

### System Monitoring
```bash
# Check disk usage
df -h

# Check memory usage
free -h

# Check CPU usage
top
```

### Updates and Maintenance
```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade

# Update Python packages
cd /opt/tropical-cloud-detection
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Restart services
sudo supervisorctl restart tropical-cloud-detection
```

## 🔒 Security Considerations

### Firewall Rules
- Only ports 80 (HTTP) and 443 (HTTPS) are open
- SSH access through Google Cloud Console

### Regular Updates
- Set up automatic security updates
- Monitor for vulnerabilities
- Keep dependencies updated

### Backup Strategy
```bash
# Create backup script
sudo crontab -e
# Add: 0 2 * * * /opt/tropical-cloud-detection/backup.sh
```

## 🚨 Troubleshooting

### Common Issues

**App not starting:**
```bash
sudo supervisorctl tail tropical-cloud-detection
```

**Nginx errors:**
```bash
sudo nginx -t
sudo systemctl status nginx
```

**Permission issues:**
```bash
sudo chown -R www-data:www-data /opt/tropical-cloud-detection
```

**Database issues:**
```bash
cd /opt/tropical-cloud-detection
source venv/bin/activate
python manage.py migrate
```

## 📋 Migration Checklist

- [ ] VM instance created
- [ ] Application deployed
- [ ] Environment configured
- [ ] DNS updated
- [ ] SSL certificate installed
- [ ] Upload functionality tested
- [ ] Processing queue tested
- [ ] Monitoring set up
- [ ] Backup configured
- [ ] Old Cloud Run service stopped

## 🎉 Success Metrics

After migration, you should see:
- ✅ Files of any size upload successfully
- ✅ No 413 errors or timeout issues
- ✅ Faster processing times
- ✅ More predictable performance
- ✅ Lower complexity in code

## 📞 Support

If you encounter issues:
1. Check the logs: `sudo tail -f /var/log/tropical-cloud-detection.log`
2. Verify services: `sudo supervisorctl status`
3. Test nginx: `sudo nginx -t`
4. Check firewall: `gcloud compute firewall-rules list`

Your tropical cloud detection app will be much more robust and performant on Compute Engine! 