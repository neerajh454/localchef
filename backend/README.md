# LocalChef Backend

Django REST API backend for the LocalChef application.

## Prerequisites

- Python 3.13+

## Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**
   
   Windows (PowerShell):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   Windows (CMD):
   ```cmd
   venv\Scripts\activate.bat
   ```
   
   Linux/macOS:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

```bash
python manage.py runserver
```

The API will be available at: http://127.0.0.1:8000

## Project Structure

```
backend/
├── apps/
│   ├── core/       # Core functionality
│   └── users/      # User management
├── config/         # Django settings
├── manage.py
└── requirements.txt
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/otp/request/` | Request OTP for phone verification |
| POST | `/api/auth/otp/resend/` | Resend OTP (SMS or voice call) |
| POST | `/api/auth/otp/verify/` | Verify OTP and get JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh JWT access token |

### User Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/PUT | `/api/users/me/` | Get or update current user profile |
| POST | `/api/users/onboarding/` | Complete user profile (first-time users) |

### Addresses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/users/addresses/` | List or create addresses |
| GET/PUT/DELETE | `/api/users/addresses/<uuid>/` | Manage specific address |
| POST | `/api/users/addresses/<uuid>/set-default/` | Set address as default |

### Testing OTP (Before MSG91 Integration)

Currently using fixed OTP for testing. MSG91 integration will be added later.

**Test OTP Code:** `123456`

#### Example: Auth Flow

1. Request OTP:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "9833863944"}'
```

Response:
```json
{
  "message": "OTP sent successfully",
  "phone_number": "9833863944",
  "type": "success"
}
```

2. Verify OTP (use `123456`):
```bash
curl -X POST http://127.0.0.1:8000/api/auth/otp/verify/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "9833863944", "otp": "123456"}'
```

Response:
```json
{
  "access": "eyJ...",
  "refresh": "eyJ...",
  "is_new_user": true,
  "user": {
    "id": "uuid",
    "phone_number": "9833863944",
    "name": "",
    "role": ""
  }
}
```

3. Resend OTP (optional):
```bash
curl -X POST http://127.0.0.1:8000/api/auth/otp/resend/ \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "9833863944", "retry_type": "text"}'
```

## JWT Authentication

This app uses JWT (JSON Web Tokens) for authentication with access and refresh tokens.

### Token Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| `ACCESS_TOKEN_LIFETIME` | 60 minutes | How long access token is valid |
| `REFRESH_TOKEN_LIFETIME` | 7 days | How long refresh token is valid |
| `ROTATE_REFRESH_TOKENS` | True | New refresh token issued on each refresh |
| `BLACKLIST_AFTER_ROTATION` | True | Old refresh token invalidated after use |

### Token Usage

#### 1. Get Tokens (Login)

After OTP verification, you receive both tokens:

```json
{
  "access": "eyJhbGc...",
  "refresh": "eyJhbGc...",
  "is_new_user": true,
  "user": {...}
}
```

#### 2. Make Authenticated Requests

Include the access token in the `Authorization` header:

```bash
curl http://127.0.0.1:8000/api/users/me/ \
  -H "Authorization: Bearer eyJhbGc..."
```

#### 3. Refresh Token (When Access Token Expires)

When access token expires (after 60 min), use the refresh token to get a new one:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJhbGc..."}'
```

Response:
```json
{
  "access": "eyJnew_access_token...",
  "refresh": "eyJnew_refresh_token..."
}
```

**Note:** Both access and refresh tokens are rotated. Store the new refresh token!

#### 4. Handle Token Expiry

```
Access Token Expired (60 min)
    ↓
Call /api/auth/token/refresh/ with refresh token
    ↓
Get new access + refresh tokens
    ↓
Continue making API calls

Refresh Token Expired (7 days)
    ↓
User must login again (request new OTP)
```

### Frontend Implementation Example

```javascript
// Token storage
let tokens = { access: null, refresh: null };

// API call with auto-refresh
async function apiCall(url, options = {}) {
  options.headers = {
    ...options.headers,
    "Authorization": `Bearer ${tokens.access}`
  };
  
  let response = await fetch(url, options);
  
  // If 401, try refreshing token
  if (response.status === 401 && tokens.refresh) {
    const refreshResponse = await fetch("/api/auth/token/refresh/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: tokens.refresh })
    });
    
    if (refreshResponse.ok) {
      const newTokens = await refreshResponse.json();
      tokens.access = newTokens.access;
      tokens.refresh = newTokens.refresh;
      
      // Retry original request
      options.headers["Authorization"] = `Bearer ${tokens.access}`;
      response = await fetch(url, options);
    } else {
      // Refresh failed - redirect to login
      tokens = { access: null, refresh: null };
      window.location.href = "/login";
    }
  }
  
  return response;
}
```

## Deployment

### Local Development with Docker

```bash
# Start with PostgreSQL
docker-compose up

# Or build and run manually
docker build -t localchef-api .
docker run -p 8000:8000 localchef-api
```

### Azure Container Apps Deployment

#### Prerequisites

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed
- Azure subscription

#### Quick Deploy

```powershell
# 1. Login to Azure
az login

# 2. Run deployment script
.\deploy-azure.ps1
```

#### What Gets Created

| Resource | Name | Cost |
|----------|------|------|
| Resource Group | `localchef-rg` | Free |
| Container Registry | `localchefacr` | ~$5/mo |
| PostgreSQL Flexible Server | `localchef-db` | ~$12/mo |
| Container Apps Environment | `localchef-env` | Free |
| Container App | `localchef-api` | Pay-per-use |

**Estimated monthly cost:** $15-25 (scales to ~$0 when idle)

#### Manual Deployment Steps

1. **Create Resource Group**
   ```bash
   az group create --name localchef-rg --location centralindia
   ```

2. **Create Container Registry**
   ```bash
   az acr create --resource-group localchef-rg --name localchefacr --sku Basic --admin-enabled true
   ```

3. **Build and Push Image**
   ```bash
   az acr build --registry localchefacr --image localchef-api:latest .
   ```

4. **Create PostgreSQL Server**
   ```bash
   az postgres flexible-server create \
     --resource-group localchef-rg \
     --name localchef-db \
     --admin-user localchefadmin \
     --admin-password "YourSecurePassword!" \
     --sku-name Standard_B1ms \
     --tier Burstable
   ```

5. **Create Container Apps Environment**
   ```bash
   az containerapp env create \
     --name localchef-env \
     --resource-group localchef-rg \
     --location centralindia
   ```

6. **Deploy Container App**
   ```bash
   az containerapp create \
     --name localchef-api \
     --resource-group localchef-rg \
     --environment localchef-env \
     --image localchefacr.azurecr.io/localchef-api:latest \
     --target-port 8000 \
     --ingress external \
     --min-replicas 0 \
     --max-replicas 10
   ```

#### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `False` |
| `SECRET_KEY` | Django secret key | Auto-generated |
| `DATABASE_URL` | PostgreSQL connection | `postgres://user:pass@host:5432/db` |
| `ALLOWED_HOSTS` | Allowed domains | `localchef-api.azurecontainerapps.io` |
| `CSRF_TRUSTED_ORIGINS` | CSRF origins | `https://localchef-api.azurecontainerapps.io` |

#### Scaling Configuration

```bash
# Update scaling rules
az containerapp update \
  --name localchef-api \
  --resource-group localchef-rg \
  --min-replicas 1 \
  --max-replicas 10 \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 100
```

#### CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Azure Container Apps

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Build and Push to ACR
        run: |
          az acr build --registry localchefacr --image localchef-api:${{ github.sha }} ./backend
      
      - name: Deploy to Container Apps
        run: |
          az containerapp update \
            --name localchef-api \
            --resource-group localchef-rg \
            --image localchefacr.azurecr.io/localchef-api:${{ github.sha }}
```

#### Monitoring

```bash
# View logs
az containerapp logs show --name localchef-api --resource-group localchef-rg --follow

# View metrics
az monitor metrics list \
  --resource /subscriptions/{sub}/resourceGroups/localchef-rg/providers/Microsoft.App/containerApps/localchef-api \
  --metric Requests
```

#### Cleanup

```bash
# Delete all resources
az group delete --name localchef-rg --yes
```
