# 🚀 MUET RAG Chatbot - Azure Deployment Guide

This guide provides a complete step-by-step process for deploying the MUET RAG Chatbot on Microsoft Azure.

---

## 📋 Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Prepare Your Application](#2-prepare-your-application)
3. [Create Azure Account](#3-create-azure-account)
4. [Install Azure CLI](#4-install-azure-cli)
5. [Create Azure Resources](#5-create-azure-resources)
6. [Deploy Using Azure App Service](#6-deploy-using-azure-app-service)
7. [Configure Environment Variables](#7-configure-environment-variables)
8. [Set Up Custom Domain (Optional)](#8-set-up-custom-domain-optional)
9. [Enable HTTPS/SSL](#9-enable-httpsssl)
10. [Monitor Your Application](#10-monitor-your-application)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Prerequisites

Before starting, ensure you have:

- ✅ Python 3.10+ installed locally
- ✅ Git installed
- ✅ Azure account (free tier available)
- ✅ Your application working locally
- ✅ All API keys (OpenRouter, Google AI, etc.)

---

## 2. Prepare Your Application

### Step 2.1: Create `requirements.txt`

Ensure your `requirements.txt` includes all dependencies:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
langchain==0.1.0
langchain-core==0.1.0
langchain-google-genai==1.0.0
langchain-openai==0.0.5
chromadb==0.4.22
apscheduler==3.10.4
pytz==2023.3
pydantic==2.5.0
crawl4ai==0.2.0
aiohttp==3.9.1
```

### Step 2.2: Create `startup.txt` (Azure startup command)

Create a new file `startup.txt`:

```
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### Step 2.3: Update `requirements.txt` to add Gunicorn

Add this line to your `requirements.txt`:

```
gunicorn==21.2.0
```

### Step 2.4: Create `.deployment` file

Create `.deployment` in your project root:

```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### Step 2.5: Create `azure-deploy.yml` (GitHub Actions - Optional)

For automated CI/CD, create `.github/workflows/azure-deploy.yml`:

```yaml
name: Deploy to Azure Web App

on:
  push:
    branches:
      - main
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: ${{ secrets.AZURE_WEBAPP_NAME }}
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

### Step 2.6: Create `.gitignore`

Ensure these are in your `.gitignore`:

```
.env
__pycache__/
*.pyc
.vscode/
*.db
vector_db/
.DS_Store
```

---

## 3. Create Azure Account

### Step 3.1: Sign Up

1. Go to [https://azure.microsoft.com/free](https://azure.microsoft.com/free)
2. Click **"Start free"**
3. Sign in with Microsoft account or create new
4. Complete verification (phone + credit card - won't be charged for free tier)
5. You get **$200 credit** for 30 days + 12 months of free services

### Step 3.2: Access Azure Portal

1. Go to [https://portal.azure.com](https://portal.azure.com)
2. Sign in with your credentials
3. You'll see the Azure Dashboard

---

## 4. Install Azure CLI

### Step 4.1: Download and Install

**Windows:**
```powershell
# Using winget (recommended)
winget install Microsoft.AzureCLI

# OR download MSI installer from:
# https://aka.ms/installazurecliwindows
```

**macOS:**
```bash
brew install azure-cli
```

**Linux (Ubuntu/Debian):**
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### Step 4.2: Verify Installation

```powershell
az --version
```

### Step 4.3: Login to Azure

```powershell
az login
```

This opens a browser for authentication. After login, you'll see your subscription details.

### Step 4.4: Set Default Subscription (if multiple)

```powershell
# List subscriptions
az account list --output table

# Set default
az account set --subscription "Your-Subscription-Name"
```

---

## 5. Create Azure Resources

### Step 5.1: Create Resource Group

A resource group is a container for your Azure resources.

```powershell
# Create resource group
az group create --name muet-chatbot-rg --location eastus
```

**Available locations:** eastus, westus, westeurope, southeastasia, etc.

### Step 5.2: Create App Service Plan

The App Service Plan defines the compute resources.

```powershell
# Create App Service Plan (Free tier)
az appservice plan create \
    --name muet-chatbot-plan \
    --resource-group muet-chatbot-rg \
    --sku F1 \
    --is-linux

# For production (Basic tier - recommended)
az appservice plan create \
    --name muet-chatbot-plan \
    --resource-group muet-chatbot-rg \
    --sku B1 \
    --is-linux
```

**Pricing Tiers:**
| Tier | Name | RAM | Storage | Price |
|------|------|-----|---------|-------|
| F1 | Free | 1 GB | 1 GB | $0 |
| B1 | Basic | 1.75 GB | 10 GB | ~$13/month |
| S1 | Standard | 1.75 GB | 50 GB | ~$70/month |
| P1V2 | Premium | 3.5 GB | 250 GB | ~$80/month |

### Step 5.3: Create Web App

```powershell
# Create the web app
az webapp create \
    --name muet-chatbot-app \
    --resource-group muet-chatbot-rg \
    --plan muet-chatbot-plan \
    --runtime "PYTHON:3.11"
```

**Note:** The app name must be globally unique. If `muet-chatbot-app` is taken, try `muet-chatbot-app-yourname`.

### Step 5.4: Verify Web App Creation

```powershell
# List web apps
az webapp list --resource-group muet-chatbot-rg --output table
```

Your app URL will be: `https://muet-chatbot-app.azurewebsites.net`

---

## 6. Deploy Using Azure App Service

### Method A: Deploy via Azure CLI (Recommended)

#### Step 6.1: Navigate to Project Directory

```powershell
cd "D:\ALL Projects\university-rag-chatbot"
```

#### Step 6.2: Create Zip of Your Application

```powershell
# Create deployment package
Compress-Archive -Path * -DestinationPath deploy.zip -Force
```

#### Step 6.3: Deploy the Zip

```powershell
az webapp deployment source config-zip \
    --resource-group muet-chatbot-rg \
    --name muet-chatbot-app \
    --src deploy.zip
```

#### Step 6.4: Configure Startup Command

```powershell
az webapp config set \
    --resource-group muet-chatbot-rg \
    --name muet-chatbot-app \
    --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000"
```

---

### Method B: Deploy via Git (Alternative)

#### Step 6.1: Initialize Git Repository

```powershell
git init
git add .
git commit -m "Initial commit for Azure deployment"
```

#### Step 6.2: Configure Deployment Credentials

```powershell
az webapp deployment user set \
    --user-name muetchatbotuser \
    --password YourSecurePassword123!
```

#### Step 6.3: Get Git Remote URL

```powershell
az webapp deployment source config-local-git \
    --name muet-chatbot-app \
    --resource-group muet-chatbot-rg
```

This returns a Git URL like:
```
https://muetchatbotuser@muet-chatbot-app.scm.azurewebsites.net/muet-chatbot-app.git
```

#### Step 6.4: Add Azure Remote and Push

```powershell
git remote add azure https://muetchatbotuser@muet-chatbot-app.scm.azurewebsites.net/muet-chatbot-app.git

git push azure main
```

Enter password when prompted.

---

### Method C: Deploy via VS Code Extension

#### Step 6.1: Install Azure Extension

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search "Azure App Service"
4. Install **Azure App Service** by Microsoft

#### Step 6.2: Sign In

1. Click Azure icon in sidebar
2. Click "Sign in to Azure"
3. Complete browser authentication

#### Step 6.3: Deploy

1. Right-click on your project folder
2. Select **"Deploy to Web App..."**
3. Select your subscription
4. Select `muet-chatbot-app`
5. Click **Deploy**

---

## 7. Configure Environment Variables

### Step 7.1: Set Environment Variables via CLI

```powershell
az webapp config appsettings set \
    --resource-group muet-chatbot-rg \
    --name muet-chatbot-app \
    --settings \
    OPENROUTER_API_KEY="your-openrouter-api-key" \
    GOOGLE_API_KEY="your-google-api-key" \
    LANGCHAIN_TRACING_V2="false" \
    PYTHONUNBUFFERED="1"
```

### Step 7.2: Set via Azure Portal (Alternative)

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **App Services** → **muet-chatbot-app**
3. Left menu → **Settings** → **Configuration**
4. Click **+ New application setting**
5. Add each key-value pair:
   - `OPENROUTER_API_KEY` = your-key
   - `GOOGLE_API_KEY` = your-key
6. Click **Save** at the top
7. Click **Continue** to restart the app

### Step 7.3: Verify Settings

```powershell
az webapp config appsettings list \
    --resource-group muet-chatbot-rg \
    --name muet-chatbot-app \
    --output table
```

---

## 8. Set Up Custom Domain (Optional)

### Step 8.1: Purchase/Configure Domain

If you have a domain (e.g., `muet-chatbot.com`):

1. Go to Azure Portal → App Services → muet-chatbot-app
2. Left menu → **Settings** → **Custom domains**
3. Click **+ Add custom domain**
4. Enter your domain name
5. Follow DNS configuration instructions:
   - Add CNAME record: `www` → `muet-chatbot-app.azurewebsites.net`
   - Add A record: `@` → Azure IP address
   - Add TXT record for verification

### Step 8.2: Validate Domain

```powershell
az webapp config hostname add \
    --webapp-name muet-chatbot-app \
    --resource-group muet-chatbot-rg \
    --hostname www.yourdomain.com
```

---

## 9. Enable HTTPS/SSL

### Step 9.1: Free SSL Certificate (Azure Managed)

1. Go to Azure Portal → App Services → muet-chatbot-app
2. Left menu → **Settings** → **TLS/SSL settings**
3. **Bindings** tab → **+ Add TLS/SSL Binding**
4. Select **App Service Managed Certificate** (Free)
5. Select your custom domain
6. Click **Add Binding**

### Step 9.2: Enforce HTTPS

```powershell
az webapp update \
    --resource-group muet-chatbot-rg \
    --name muet-chatbot-app \
    --https-only true
```

Or via Portal:
1. Go to **TLS/SSL settings**
2. Set **HTTPS Only** to **On**

---

## 10. Monitor Your Application

### Step 10.1: View Live Logs

```powershell
# Enable logging
az webapp log config \
    --resource-group muet-chatbot-rg \
    --name muet-chatbot-app \
    --docker-container-logging filesystem

# Stream logs
az webapp log tail \
    --resource-group muet-chatbot-rg \
    --name muet-chatbot-app
```

### Step 10.2: View Logs in Portal

1. Go to Azure Portal → App Services → muet-chatbot-app
2. Left menu → **Monitoring** → **Log stream**
3. Watch real-time logs

### Step 10.3: Application Insights (Advanced)

1. Left menu → **Settings** → **Application Insights**
2. Click **Turn on Application Insights**
3. Select or create new instance
4. Click **Apply**

Now you can:
- Track requests/failures
- Monitor performance
- Set up alerts
- View detailed traces

### Step 10.4: Set Up Alerts

1. Go to **Monitoring** → **Alerts**
2. Click **+ Create alert rule**
3. Configure conditions:
   - HTTP 5xx errors > 10
   - Response time > 5 seconds
   - CPU > 80%
4. Set notification (email, SMS)

---

## 11. Troubleshooting

### Common Issues & Solutions

#### Issue 1: Application Error / 500 Error

**Check Logs:**
```powershell
az webapp log tail --resource-group muet-chatbot-rg --name muet-chatbot-app
```

**Common causes:**
- Missing environment variables
- Incorrect startup command
- Module import errors

#### Issue 2: ModuleNotFoundError

**Solution:** Ensure all packages are in `requirements.txt`:
```powershell
pip freeze > requirements.txt
```

Then redeploy.

#### Issue 3: Slow Cold Start

**Solution:** Keep app warm with Always On (requires Basic tier+):
```powershell
az webapp config set \
    --resource-group muet-chatbot-rg \
    --name muet-chatbot-app \
    --always-on true
```

#### Issue 4: File Not Found Errors

**Solution:** Use correct paths. In Azure, your app runs from `/home/site/wwwroot/`:

```python
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "website_documents")
```

#### Issue 5: ChromaDB/Vector Store Issues

**Solution:** ChromaDB needs persistent storage. Configure Azure Storage:

```powershell
# Create storage account
az storage account create \
    --name muetchatbotstorage \
    --resource-group muet-chatbot-rg \
    --location eastus \
    --sku Standard_LRS

# Mount to web app
az webapp config storage-account add \
    --resource-group muet-chatbot-rg \
    --name muet-chatbot-app \
    --custom-id vectordb \
    --storage-type AzureFiles \
    --share-name vectordb \
    --account-name muetchatbotstorage \
    --mount-path /data/vectordb
```

#### Issue 6: Restart Application

```powershell
az webapp restart \
    --resource-group muet-chatbot-rg \
    --name muet-chatbot-app
```

---

## 📊 Deployment Checklist

Before going live, verify:

- [ ] Application loads at Azure URL
- [ ] Chat functionality works
- [ ] All environment variables set
- [ ] HTTPS enabled
- [ ] Logs are accessible
- [ ] Error handling works
- [ ] Static files load correctly
- [ ] Background scheduler runs (if needed)

---

## 💰 Cost Estimation

| Resource | Tier | Monthly Cost |
|----------|------|--------------|
| App Service | F1 (Free) | $0 |
| App Service | B1 (Basic) | ~$13 |
| App Service | S1 (Standard) | ~$70 |
| Storage Account | Standard | ~$5 |
| Custom Domain | - | ~$12/year |
| SSL Certificate | Azure Managed | Free |

**Recommended for Production:** B1 tier (~$13-20/month)

---

## 🔗 Useful Links

- [Azure Portal](https://portal.azure.com)
- [Azure CLI Documentation](https://docs.microsoft.com/en-us/cli/azure/)
- [Python on Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/quickstart-python)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

---

## 📞 Support

If you encounter issues:

1. Check Azure Status: [status.azure.com](https://status.azure.com)
2. Azure Documentation: [docs.microsoft.com/azure](https://docs.microsoft.com/azure)
3. Stack Overflow: Tag `azure-app-service`

---

**🎉 Congratulations! Your MUET Chatbot is now live on Azure!**

Your app URL: `https://muet-chatbot-app.azurewebsites.net`
