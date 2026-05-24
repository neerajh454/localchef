# LocalChef - Azure Container Apps Deployment Script
# Prerequisites: Azure CLI installed and logged in (az login)

# ==================== CONFIGURATION ====================
$RESOURCE_GROUP = "localchef-rg"
$LOCATION = "centralindia"  # Change to your preferred region
$CONTAINER_APP_ENV = "localchef-env"
$CONTAINER_APP_NAME = "localchef-api"
$ACR_NAME = "localchefacr"  # Must be globally unique, lowercase
$POSTGRES_SERVER = "localchef-db"
$POSTGRES_DB = "localchef"
$POSTGRES_USER = "localchefadmin"
# Generate a random password or set your own
$POSTGRES_PASSWORD = "LocalChef@2026!"  # Change this!
$SECRET_KEY = [System.Guid]::NewGuid().ToString() + [System.Guid]::NewGuid().ToString()

# ==================== CREATE RESOURCES ====================

Write-Host "Creating Resource Group..." -ForegroundColor Cyan
az group create --name $RESOURCE_GROUP --location $LOCATION

Write-Host "Creating Azure Container Registry..." -ForegroundColor Cyan
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

Write-Host "Creating PostgreSQL Flexible Server..." -ForegroundColor Cyan
az postgres flexible-server create `
    --resource-group $RESOURCE_GROUP `
    --name $POSTGRES_SERVER `
    --location $LOCATION `
    --admin-user $POSTGRES_USER `
    --admin-password $POSTGRES_PASSWORD `
    --sku-name Standard_B1ms `
    --tier Burstable `
    --storage-size 32 `
    --version 15 `
    --public-access 0.0.0.0

Write-Host "Creating PostgreSQL Database..." -ForegroundColor Cyan
az postgres flexible-server db create `
    --resource-group $RESOURCE_GROUP `
    --server-name $POSTGRES_SERVER `
    --database-name $POSTGRES_DB

Write-Host "Creating Container Apps Environment..." -ForegroundColor Cyan
az containerapp env create `
    --name $CONTAINER_APP_ENV `
    --resource-group $RESOURCE_GROUP `
    --location $LOCATION

# ==================== BUILD AND PUSH IMAGE ====================

Write-Host "Building and pushing Docker image..." -ForegroundColor Cyan
az acr build --registry $ACR_NAME --image localchef-api:latest .

# ==================== GET CONNECTION STRINGS ====================

$ACR_LOGIN_SERVER = az acr show --name $ACR_NAME --query loginServer -o tsv
$ACR_PASSWORD = az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv
$POSTGRES_HOST = "$POSTGRES_SERVER.postgres.database.azure.com"
$DATABASE_URL = "postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DB}?sslmode=require"

# ==================== DEPLOY CONTAINER APP ====================

Write-Host "Deploying Container App..." -ForegroundColor Cyan
az containerapp create `
    --name $CONTAINER_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --environment $CONTAINER_APP_ENV `
    --image "${ACR_LOGIN_SERVER}/localchef-api:latest" `
    --registry-server $ACR_LOGIN_SERVER `
    --registry-username $ACR_NAME `
    --registry-password $ACR_PASSWORD `
    --target-port 8000 `
    --ingress external `
    --min-replicas 0 `
    --max-replicas 10 `
    --cpu 0.5 `
    --memory 1.0Gi `
    --env-vars `
        "DEBUG=False" `
        "SECRET_KEY=$SECRET_KEY" `
        "DATABASE_URL=$DATABASE_URL" `
        "ALLOWED_HOSTS=*"

# ==================== RUN MIGRATIONS ====================

Write-Host "Running database migrations..." -ForegroundColor Cyan
az containerapp exec `
    --name $CONTAINER_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --command "python manage.py migrate"

# ==================== GET APP URL ====================

$APP_URL = az containerapp show `
    --name $CONTAINER_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --query properties.configuration.ingress.fqdn -o tsv

Write-Host ""
Write-Host "==================== DEPLOYMENT COMPLETE ====================" -ForegroundColor Green
Write-Host "API URL: https://$APP_URL" -ForegroundColor Yellow
Write-Host ""
Write-Host "Test your API:" -ForegroundColor Cyan
Write-Host "  curl https://$APP_URL/api/auth/otp/request/ -X POST -H 'Content-Type: application/json' -d '{\"phone_number\": \"9833863944\"}'"
Write-Host ""
Write-Host "Important: Update ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS with your actual domain" -ForegroundColor Red
