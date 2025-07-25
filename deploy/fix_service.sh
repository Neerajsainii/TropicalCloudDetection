#!/bin/bash
# Fix systemd service configuration

echo "🔧 Fixing systemd service configuration..."

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

# Reload systemd and restart service
sudo systemctl daemon-reload
sudo systemctl restart tropical-cloud-detection

echo "✅ Service configuration fixed!"
echo "🔧 Service status:"
sudo systemctl status tropical-cloud-detection --no-pager 