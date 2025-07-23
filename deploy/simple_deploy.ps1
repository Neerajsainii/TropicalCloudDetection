# PowerShell deployment script
Write-Host "🚀 Starting simple deployment..." -ForegroundColor Green

# Get VM external IP
$EXTERNAL_IP = gcloud compute instances describe tropical-cloud-app --zone=asia-southeast1-a --format="value(networkInterfaces[0].accessConfigs[0].natIP)"
Write-Host "📦 Creating deployment package..." -ForegroundColor Yellow

# Create deployment package
tar -czf app.tar.gz --exclude='.git' --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env*' --exclude='db.sqlite3*' --exclude='media' --exclude='staticfiles' --exclude='key.json' --exclude='gcp-github-actions*' --warning=no-file-changed .

Write-Host "📤 Uploading to VM..." -ForegroundColor Yellow
gcloud compute scp app.tar.gz tropical-cloud-app:/tmp/app.tar.gz --zone=asia-southeast1-a

Write-Host "🔧 Setting up VM..." -ForegroundColor Yellow
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="sudo mkdir -p /opt/tropical-cloud-detection"

Write-Host "📂 Extracting files..." -ForegroundColor Yellow
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="cd /opt/tropical-cloud-detection && sudo tar -xzf /tmp/app.tar.gz"

Write-Host "🐍 Installing Python dependencies..." -ForegroundColor Yellow
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv nginx build-essential libhdf5-dev libnetcdf-dev pkg-config"

Write-Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="cd /opt/tropical-cloud-detection && sudo python3 -m venv venv"

Write-Host "📦 Installing Python packages..." -ForegroundColor Yellow
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="cd /opt/tropical-cloud-detection && source venv/bin/activate && sudo venv/bin/pip install -r requirements.txt"

Write-Host "🗄️ Running database migrations..." -ForegroundColor Yellow
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="cd /opt/tropical-cloud-detection && source venv/bin/activate && sudo venv/bin/python manage.py migrate"

Write-Host "📁 Collecting static files..." -ForegroundColor Yellow
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="cd /opt/tropical-cloud-detection && source venv/bin/activate && sudo venv/bin/python manage.py collectstatic --noinput"

Write-Host "🛑 Stopping any existing processes..." -ForegroundColor Yellow
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="sudo pkill -f gunicorn || true"

Write-Host "🚀 Starting Gunicorn..." -ForegroundColor Yellow
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="cd /opt/tropical-cloud-detection && source venv/bin/activate && nohup sudo venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 600 cloud_detection_portal.wsgi:application > gunicorn.log 2>&1 &"

Write-Host "⏳ Waiting for Gunicorn to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "🔍 Checking if Gunicorn is running..." -ForegroundColor Yellow
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="ps aux | grep gunicorn"

Write-Host "🌐 Setting up Nginx..." -ForegroundColor Yellow
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="echo 'server { listen 8080; server_name _; client_max_body_size 200M; location /static/ { alias /opt/tropical-cloud-detection/staticfiles/; } location /media/ { alias /opt/tropical-cloud-detection/media/; } location / { proxy_pass http://127.0.0.1:8000; proxy_set_header Host \$host; proxy_set_header X-Real-IP \$remote_addr; proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for; } }' | sudo tee /etc/nginx/sites-available/tropical-cloud-detection"

Write-Host "🔗 Enabling Nginx site..." -ForegroundColor Yellow
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="sudo ln -sf /etc/nginx/sites-available/tropical-cloud-detection /etc/nginx/sites-enabled/"

Write-Host "🗑️ Removing default Nginx site..." -ForegroundColor Yellow
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="sudo rm -f /etc/nginx/sites-enabled/default"

Write-Host "🔄 Restarting Nginx..." -ForegroundColor Yellow
gcloud compute ssh tropical-cloud-app --zone=asia-southeast1-a --command="sudo systemctl restart nginx"

Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "🔍 Testing application..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://$EXTERNAL_IP:8080/" -UseBasicParsing
    Write-Host "✅ Application is responding!" -ForegroundColor Green
} catch {
    Write-Host "❌ Application not responding" -ForegroundColor Red
}

Write-Host "✅ Deployment completed!" -ForegroundColor Green
Write-Host "🌐 Application URL: http://$EXTERNAL_IP:8080" -ForegroundColor Cyan
Write-Host "📊 Gunicorn logs: ssh tropical-cloud-app 'tail -f /opt/tropical-cloud-detection/gunicorn.log'" -ForegroundColor Cyan 