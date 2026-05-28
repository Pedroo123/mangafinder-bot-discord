# Deployment Guide for Azure Container Apps

This guide explains how to deploy the MangaFinder Bot to Azure using Azure Container Apps.

## Prerequisites

1.  **Azure Account:** An active Azure subscription.
2.  **Azure CLI:** Installed and logged in (`az login`).
3.  **Docker:** (Optional) for local testing.
4.  **Reddit API Credentials:** CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD.
5.  **Discord Bot Token.**

## Steps

### 1. Create a Resource Group
```bash
az group create --name mangafinder-rg --location eastus
```

### 2. Create an Azure Container Registry (ACR)
```bash
az acr create --resource-group mangafinder-rg --name mangafinderregistry --sku Basic
az acr login --name mangafinderregistry
```

### 3. Build and Push the Image
```bash
# Get the login server name
ACR_SERVER=$(az acr show --name mangafinderregistry --query loginServer --output tsv)

# Build the image locally
docker build -t $ACR_SERVER/mangafinder-bot:v1 .

# Push the image
docker push $ACR_SERVER/mangafinder-bot:v1
```

### 4. Create the Container App Environment
```bash
az containerapp env create --name mangafinder-env --resource-group mangafinder-rg --location eastus
```

### 5. Deploy the Container App
Ensure you have your secrets ready to be passed as environment variables.

```bash
az containerapp create \
  --name mangafinder-bot \
  --resource-group mangafinder-rg \
  --environment mangafinder-env \
  --image $ACR_SERVER/mangafinder-bot:v1 \
  --registry-server $ACR_SERVER \
  --env-vars \
    DISCORD_TOKEN=<your-discord-token> \
    REDDIT_CLIENT_ID=<your-reddit-id> \
    REDDIT_CLIENT_SECRET=<your-reddit-secret> \
    REDDIT_USERNAME=<your-reddit-username> \
    REDDIT_PASSWORD=<your-reddit-password> \
  --cpu 0.25 --memory 0.5Gi \
  --min-replicas 1 --max-replicas 1
```

## Maintenance

To update the bot, build and push a new image tag and update the Container App:
```bash
az containerapp update --name mangafinder-bot --resource-group mangafinder-rg --image $ACR_SERVER/mangafinder-bot:v2
```
