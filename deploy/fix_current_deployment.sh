#!/bin/bash
# Fix Current Deployment Script
# This script fixes the current deployment by setting up proper systemd service

set -e

echo "🔧 Fixing current deployment..."

cd /opt/tropical-cloud-detection

# Stop any existing gunicorn processes
sudo pkill -f gunicorn || true
sleep 2

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/tropical-cloud-detection.service > /dev/null << 'EOF'
[Unit]
Description=Tropical Cloud Detection Django Application
After=network.target

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/opt/tropical-cloud-detection
Environment=PATH=/opt/tropical-cloud-detection/venv/bin
EnvironmentFile=/opt/tropical-cloud-detection/.env
ExecStart=/opt/tropical-cloud-detection/venv/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 2 \
    --worker-class sync \
    --timeout 600 \
    --max-requests 100 \
    --max-requests-jitter 10 \
    --preload \
    --access-logfile /opt/tropical-cloud-detection/logs/django.log \
    --error-logfile /opt/tropical-cloud-detection/logs/django-error.log \
    cloud_detection_portal.wsgi:application
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create logs directory
sudo mkdir -p /opt/tropical-cloud-detection/logs
sudo chmod 755 /opt/tropical-cloud-detection/logs

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable tropical-cloud-detection

# Start the service
sudo systemctl start tropical-cloud-detection

# Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 10

# Check service status
echo "🔧 Service status:"
sudo systemctl status tropical-cloud-detection --no-pager

# Create health check script
sudo tee /opt/tropical-cloud-detection/health_check.sh > /dev/null << 'EOF'
#!/bin/bash
if ! curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
  echo "$(date): Health check failed, restarting service..."
  sudo systemctl restart tropical-cloud-detection
fi
EOF

sudo chmod +x /opt/tropical-cloud-detection/health_check.sh

# Add health check to crontab (remove existing first)
sudo crontab -l 2>/dev/null | grep -v "health_check.sh" | sudo crontab -
echo "*/5 * * * * /opt/tropical-cloud-detection/health_check.sh" | sudo crontab -

echo "✅ Deployment fixed!"
echo "🔧 Service is now managed by systemd and will auto-restart"
echo "📊 Check logs with: sudo journalctl -u tropical-cloud-detection -f"
echo "🔧 Check status with: sudo systemctl status tropical-cloud-detection" 