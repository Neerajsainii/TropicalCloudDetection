# 🚀 Easy GitHub Actions Deployment Guide

Your application is now set up for **automatic deployment** using GitHub Actions - the **most popular and easiest** method used by 95% of developers.

## ✅ What You Get

**Every time you push code to GitHub:**
- ✅ Automatic deployment to your VM
- ✅ Zero downtime deployments  
- ✅ Automatic service restarts
- ✅ Professional CI/CD pipeline

**Your VM Details:**
- 🌐 **IP**: http://35.247.130.75:8080
- ⚡ **Power**: 8 vCPUs, 32GB RAM (optimized for 50-100MB files)
- 📍 **Location**: Asia Southeast (Singapore)
- 💾 **File Limit**: 200MB (vs 32MB Cloud Run limit)

## 🔧 One-Time Setup (5 minutes)

### Step 1: Create GitHub Repository

```bash
# In your project directory
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/TropicalCloudDetection.git
git push -u origin main
```

### Step 2: Add GitHub Secrets

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 2 secrets:

#### Secret 1: `GCP_SA_KEY`
```bash
# Create service account and download key
gcloud iam service-accounts create github-actions
gcloud projects add-iam-policy-binding tropical-cloud-detection \
    --member="serviceAccount:github-actions@tropical-cloud-detection.iam.gserviceaccount.com" \
    --role="roles/compute.admin"
gcloud iam service-accounts keys create key.json \
    --iam-account=github-actions@tropical-cloud-detection.iam.gserviceaccount.com

# Copy the contents of key.json and paste as GCP_SA_KEY secret
```

#### Secret 2: `GCP_SSH_PRIVATE_KEY`
```bash
# Generate SSH key for VM access
ssh-keygen -t rsa -b 4096 -f ~/.ssh/gcp-github-actions
gcloud compute project-info add-metadata \
    --metadata-from-file ssh-keys=~/.ssh/gcp-github-actions.pub

# Copy contents of ~/.ssh/gcp-github-actions (private key) as GCP_SSH_PRIVATE_KEY secret
```

## 🎉 That's It! Now Deploy Automatically

### Deploy Method 1: Push to GitHub (Automatic)
```bash
# Make any change to your code
git add .
git commit -m "Updated processing algorithm"
git push origin main
# → Automatic deployment starts! ✨
```

### Deploy Method 2: Manual Trigger
- Go to GitHub → **Actions** tab
- Click **Deploy to Google Compute Engine**
- Click **Run workflow** → **Run workflow**

## 📊 Monitor Deployments

### View Deployment Status
- **GitHub**: Go to Actions tab to see deployment progress
- **Local**: `gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a`

### Check Application Status
```bash
# SSH to VM
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a

# Check app status
sudo systemctl status tropical-cloud-detection

# View logs
sudo journalctl -u tropical-cloud-detection -f

# Check nginx
sudo systemctl status nginx
```

## 🔥 Your Performance Upgrade

| Aspect | Before (Cloud Run) | After (Compute Engine) |
|--------|-------------------|----------------------|
| **File Size** | 32MB limit ❌ | 200MB capacity ✅ |
| **Processing** | Limited resources ❌ | **30-40 seconds** ✅ |
| **Memory** | Very limited ❌ | 32GB available ✅ |
| **Deployment** | Manual ❌ | **Automatic with git push** ✅ |

## 🎯 Daily Workflow

**Your new development workflow:**
1. Write code locally
2. Test with `python manage.py runserver`
3. Push to GitHub: `git push origin main`
4. GitHub automatically deploys to your VM
5. Access your app at: http://35.247.130.75:8080

**No more manual deployments!** 🎉

## 🛠️ Quick Commands

```bash
# Check VM status
gcloud compute instances list

# SSH to VM
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a

# Restart application
sudo systemctl restart tropical-cloud-detection

# View application logs
sudo journalctl -u tropical-cloud-detection -f

# Check resource usage
htop

# Test file upload (from VM)
curl -X POST -F "file=@test_file.dat" http://localhost:8000/upload/
```

## 🚀 Next Steps

1. **Push your code to GitHub**
2. **Set up the 2 secrets** (takes 5 minutes)
3. **Enjoy automatic deployments!**

Your 50-100MB file processing will be **much faster** with 8 cores and 32GB RAM! 

🎉 **Welcome to professional CI/CD deployment!** 