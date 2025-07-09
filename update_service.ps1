# Add gcloud to PATH
$env:PATH += ";$env:USERPROFILE\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"

# Update Cloud Run service with environment variables from file
gcloud run services update tropical-cloud-detection `
    --region=us-central1 `
    --env-vars-file=env_vars.yaml

Write-Host "Service updated with environment variables from file!" 