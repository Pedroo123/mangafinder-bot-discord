# Deployment Guide for Azure Container Apps

This guide explains how to deploy the MangaFinder Bot to Azure Container Apps.

## Prerequisites
- Azure CLI installed
- An active Azure subscription
- Docker installed locally (optional, for local testing)

## Steps

### 1. Build and Push the Docker Image
You can use Azure Container Registry (ACR) to host your image.

```bash
# Login to Azure
az login

# Create a resource group
az group create --name manga-finder-rg --location eastus

# Create an ACR
az acr create --resource-group manga-finder-rg --name mangafinderacr --sku Basic

# Login to ACR
az acr login --name mangafinderacr

# Build and push the image
az acr build --registry mangafinderacr --image mangafinder-bot:v1 .
```

### 2. Create the Container App Environment
```bash
az containerapp env create \
  --name manga-finder-env \
  --resource-group manga-finder-rg \
  --location eastus
```

### 3. Deploy the Container App
The bot does not need an ingress as it connects to Discord and Reddit via outbound connections.

```bash
az containerapp create \
  --name mangafinder-bot \
  --resource-group manga-finder-rg \
  --environment manga-finder-env \
  --image mangafinderacr.azurecr.io/mangafinder-bot:v1 \
  --secrets "discord-token=<YOUR_DISCORD_TOKEN>" \
            "reddit-client-id=<YOUR_REDDIT_CLIENT_ID>" \
            "reddit-client-secret=<YOUR_REDDIT_CLIENT_SECRET>" \
            "reddit-username=<YOUR_REDDIT_USERNAME>" \
            "reddit-password=<YOUR_REDDIT_PASSWORD>" \
  --env-vars "DISCORD_TOKEN=secretref:discord-token" \
             "REDDIT_CLIENT_ID=secretref:reddit-client-id" \
             "REDDIT_CLIENT_SECRET=secretref:reddit-client-secret" \
             "REDDIT_USERNAME=secretref:reddit-username" \
             "REDDIT_PASSWORD=secretref:reddit-password" \
  --cpu 0.25 --memory 0.5Gi
```

## Security Best Practices
- Use Managed Identities if possible to access other Azure resources.
- Regularly update the base image in the `Dockerfile`.
- Ensure no sensitive information is committed to the repository (check `.gitignore`).
