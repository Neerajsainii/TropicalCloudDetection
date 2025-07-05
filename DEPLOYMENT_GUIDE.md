# Tropical Cloud Detection System - Render Deployment Guide

This guide will help you deploy your Django-based tropical cloud detection system to Render.

## Prerequisites

- A Render account (free tier available)
- Your code pushed to a GitHub repository
- Basic knowledge of environment variables

## Step 1: Prepare Your Repository

1. **Push your code to GitHub** (if not already done)
2. **Ensure all files are committed**, including:
   - `requirements.txt` (updated with production dependencies)
   - `build.sh` (build script)
   - `render.yaml` (configuration file)
   - Updated `settings.py` (production-ready)

## Step 2: Create a Render Account

1. Go to [render.com](https://render.com)
2. Sign up for a free account
3. Connect your GitHub account

## Step 3: Generate a Secret Key

Run the secret key generator:

```bash
python generate_secret_key.py
```

Copy the generated key - you'll need it for environment variables.

## Step 4: Create a PostgreSQL Database

1. In your Render dashboard, click "New +"
2. Select "PostgreSQL"
3. Configure:
   - **Name**: `tropical-cloud-detection-db`
   - **Database**: `tropical_cloud_detection`
   - **User**: `cloud_user`
   - **Plan**: Free (or paid for production)
4. Click "Create Database"
5. **Important**: Copy the "External Database URL" - you'll need this

## Step 5: Create Web Service

1. In your Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repository
4. Configure the service:

### Basic Settings
- **Name**: `tropical-cloud-detection`
- **Environment**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn cloud_detection_portal.wsgi:application`

### Environment Variables
Add these environment variables in the Render dashboard:

```
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=your-postgresql-url-from-step-4
CORS_ALLOWED_ORIGINS=https://your-app-name.onrender.com
```

**Replace**:
- `your-generated-secret-key-here` with the key from Step 3
- `your-app-name.onrender.com` with your actual Render URL
- `your-postgresql-url-from-step-4` with the database URL from Step 4

## Step 6: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Install dependencies
   - Collect static files
   - Run database migrations
   - Create a superuser (admin/cloudadmin123)
   - Start the application

## Step 7: Access Your Application

1. Once deployment is complete, you'll get a URL like: `https://tropical-cloud-detection.onrender.com`
2. Visit your application
3. Access admin panel at: `https://your-app.onrender.com/admin/`
   - Username: `admin`
   - Password: `cloudadmin123`

## Step 8: Test Your Application

1. **Upload a satellite data file** (HDF5 format)
2. **Verify cloud detection processing** works
3. **Test download functionality**
4. **Check that modals work properly**

## Important Notes

### File Uploads
- Render has disk space limitations on free tier
- Large satellite files may need external storage (AWS S3)
- Consider implementing file cleanup for old uploads

### Database
- Free PostgreSQL has storage limits
- Monitor database usage in Render dashboard
- Consider upgrading for production use

### Performance
- Free tier has limited CPU/memory
- Application may sleep after 15 minutes of inactivity
- Consider upgrading for production use

### Security
- Change default superuser password immediately
- Use strong, unique passwords
- Enable 2FA on your Render account

## Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify all dependencies in `requirements.txt`
- Ensure `build.sh` is executable

### Database Connection Issues
- Verify DATABASE_URL is correct
- Check database is running
- Confirm database credentials

### Static Files Not Loading
- Ensure `STATIC_ROOT` is set correctly
- Check WhiteNoise configuration
- Verify `collectstatic` runs successfully

### Application Errors
- Check application logs in Render
- Verify environment variables are set
- Check Django settings configuration

## Maintenance

### Regular Updates
- Keep dependencies updated
- Monitor security patches
- Review logs regularly

### Backup
- Export data regularly
- Store backups securely
- Test restore procedures

### Monitoring
- Set up error monitoring
- Monitor application performance
- Track usage patterns

## Support

For issues specific to:
- **Render Platform**: Check Render documentation
- **Django Configuration**: Review Django docs
- **Application Features**: Review your code and logs

## Success Checklist

- [ ] Repository pushed to GitHub
- [ ] PostgreSQL database created
- [ ] Environment variables configured
- [ ] Web service deployed successfully
- [ ] Application accessible via URL
- [ ] File upload functionality working
- [ ] Cloud detection processing working
- [ ] Admin panel accessible
- [ ] Download functionality working
- [ ] Modals working properly

Congratulations! Your tropical cloud detection system is now deployed on Render! 🎉 