# PowerShell script for Windows users to migrate to Google Compute Engine
# Run this script from the project root directory

param(
    [string]$ProjectId = "tropical-cloud-detection",
    [string]$InstanceName = "tropical-cloud-app", 
    [string]$Zone = "asia-southeast1-a",
    [string]$MachineType = "e2-standard-8",
    [string]$DiskSize = "50GB"
)

Write-Host "🚀 Starting migration to Google Compute Engine..." -ForegroundColor Green
Write-Host "Project: $ProjectId" -ForegroundColor Cyan
Write-Host "Instance: $InstanceName" -ForegroundColor Cyan
Write-Host "Zone: $Zone" -ForegroundColor Cyan
Write-Host "Machine Type: $MachineType" -ForegroundColor Cyan

# Check if gcloud is installed
try {
    $null = Get-Command gcloud -ErrorAction Stop
    Write-Host "✅ Google Cloud SDK found" -ForegroundColor Green
} catch {
    Write-Host "❌ Google Cloud SDK not found. Please install it first:" -ForegroundColor Red
    Write-Host "   https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Check if scripts exist
$setupScript = "deploy/compute_engine_setup.sh"
$deployScript = "deploy/deploy_to_vm.sh"

if (!(Test-Path $setupScript)) {
    Write-Host "❌ Setup script not found: $setupScript" -ForegroundColor Red
    exit 1
}

if (!(Test-Path $deployScript)) {
    Write-Host "❌ Deploy script not found: $deployScript" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📋 Migration Steps:" -ForegroundColor Yellow
Write-Host "1. Create firewall rules and VM instance" -ForegroundColor White
Write-Host "2. Configure the VM with startup script" -ForegroundColor White
Write-Host "3. Deploy application code to VM" -ForegroundColor White
Write-Host ""

$confirmation = Read-Host "Do you want to proceed? (y/N)"
if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
    Write-Host "Migration cancelled." -ForegroundColor Yellow
    exit 0
}

# Step 1: Create VM instance
Write-Host ""
Write-Host "🖥️ Step 1: Creating VM instance..." -ForegroundColor Green
try {
    bash $setupScript $ProjectId $InstanceName $Zone $MachineType $DiskSize
    if ($LASTEXITCODE -ne 0) {
        throw "Setup script failed"
    }
    Write-Host "✅ VM instance created successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create VM instance. Check the error above." -ForegroundColor Red
    exit 1
}

# Wait for VM to be ready
Write-Host ""
Write-Host "⏳ Waiting for VM startup script to complete (this may take 5-10 minutes)..." -ForegroundColor Yellow
Write-Host "   You can monitor progress with:" -ForegroundColor Gray
Write-Host "   gcloud compute ssh $InstanceName --zone=$Zone --command='tail -f /var/log/startup-script.log'" -ForegroundColor Gray

# Give startup script time to begin
Start-Sleep -Seconds 30

# Check if VM is ready by testing SSH
$maxAttempts = 20
$attempt = 0
do {
    $attempt++
    Write-Host "   Checking VM readiness... (attempt $attempt/$maxAttempts)" -ForegroundColor Gray
    
    try {
        $result = gcloud compute ssh $InstanceName --zone=$Zone --project=$ProjectId --command="echo 'VM Ready'" 2>$null
        if ($result -match "VM Ready") {
            Write-Host "✅ VM is ready for deployment!" -ForegroundColor Green
            break
        }
    } catch {
        # SSH not ready yet
    }
    
    if ($attempt -eq $maxAttempts) {
        Write-Host "⚠️ VM may still be initializing. Proceeding with deployment..." -ForegroundColor Yellow
        break
    }
    
    Start-Sleep -Seconds 30
} while ($attempt -lt $maxAttempts)

# Step 2: Deploy application
Write-Host ""
Write-Host "📤 Step 2: Deploying application..." -ForegroundColor Green
try {
    bash $deployScript $ProjectId $InstanceName $Zone
    if ($LASTEXITCODE -ne 0) {
        throw "Deployment script failed"
    }
    Write-Host "✅ Application deployed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to deploy application. Check the error above." -ForegroundColor Red
    Write-Host "You can try again by running:" -ForegroundColor Yellow
    Write-Host "   bash $deployScript $ProjectId $InstanceName $Zone" -ForegroundColor Gray
    exit 1
}

# Get final status
Write-Host ""
Write-Host "🎉 Migration Complete!" -ForegroundColor Green
Write-Host ""

try {
    $externalIp = gcloud compute instances describe $InstanceName --zone=$Zone --project=$ProjectId --format="value(networkInterfaces[0].accessConfigs[0].natIP)" 2>$null
    if ($externalIp) {
        Write-Host "🔗 Your application is now running at:" -ForegroundColor Cyan
        Write-Host "   http://$externalIp:8080" -ForegroundColor White
        Write-Host ""
        Write-Host "📊 Management Commands:" -ForegroundColor Yellow
        Write-Host "   SSH to VM: gcloud compute ssh $InstanceName --zone=$Zone --project=$ProjectId" -ForegroundColor Gray
        Write-Host "   View logs: gcloud compute ssh $InstanceName --zone=$Zone --project=$ProjectId --command='sudo journalctl -u tropical-cloud-detection -f'" -ForegroundColor Gray
        Write-Host "   Check status: gcloud compute ssh $InstanceName --zone=$Zone --project=$ProjectId --command='sudo systemctl status tropical-cloud-detection'" -ForegroundColor Gray
        Write-Host ""
        Write-Host "🔄 To update your application later:" -ForegroundColor Yellow
        Write-Host "   bash $deployScript $ProjectId $InstanceName $Zone" -ForegroundColor Gray
        Write-Host ""
        Write-Host "📖 For detailed documentation, see: deploy/README_COMPUTE_ENGINE.md" -ForegroundColor Cyan
    }
} catch {
    Write-Host "⚠️ Could not retrieve VM IP. Check the VM status manually." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Test your application at the URL above" -ForegroundColor White
Write-Host "2. Update your DNS records to point to the new IP (for production)" -ForegroundColor White
Write-Host "3. Consider setting up HTTPS with Let's Encrypt (see documentation)" -ForegroundColor White
Write-Host "4. Monitor resource usage and scale as needed" -ForegroundColor White