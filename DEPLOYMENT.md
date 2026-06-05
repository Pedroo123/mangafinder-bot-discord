# Deployment Guide for Azure Container Apps

This guide explains how to deploy the MangaFinder Bot to Azure Container Apps.

## Prerequisites

- Azure CLI installed and configured.
- A Container Registry (ACR) to host the Docker image.
- A Resource Group in Azure.

## Steps

### 1. Build and Push the Docker Image

Build the image locally and push it to your Azure Container Registry:

```bash
# Log in to ACR
az acr login --name <your-registry-name>

# Build the image
docker build -t <your-registry-name>.azurecr.io/mangafinder-bot:latest .

# Push the image
docker push <your-registry-name>.azurecr.io/mangafinder-bot:latest
```

### 2. Create the Container App

The bot is a worker process and does not need to listen for HTTP traffic. Ensure ingress is disabled.

```bash
az containerapp create \
  --name mangafinder-bot \
  --resource-group <your-resource-group> \
  --environment <your-environment-name> \
  --image <your-registry-name>.azurecr.io/mangafinder-bot:latest \
  --cpu 0.25 --memory 0.5Gi \
  --min-replicas 1 --max-replicas 1 \
  --ingress disabled
```

### 3. Configure Secrets and Environment Variables

Add the required secrets and environment variables to the Container App:

```bash
# Add secrets
az containerapp secret set \
  --name mangafinder-bot \
  --resource-group <your-resource-group> \
  --secrets \
    discord-token="<your-discord-token>" \
    reddit-client-id="<your-reddit-client-id>" \
    reddit-client-secret="<your-reddit-client-secret>" \
    reddit-username="<your-reddit-username>" \
    reddit-password="<your-reddit-password>"

# Set environment variables using the secrets
az containerapp update \
  --name mangafinder-bot \
  --resource-group <your-resource-group> \
  --set-env-vars \
    DISCORD_TOKEN=secretref:discord-token \
    REDDIT_CLIENT_ID=secretref:reddit-client-id \
    REDDIT_CLIENT_SECRET=secretref:reddit-client-secret \
    REDDIT_USERNAME=secretref:reddit-username \
    REDDIT_PASSWORD=secretref:reddit-password
```

## Monitoring

You can view logs in the Azure Portal under "Log Stream" or use the following command:

```bash
az containerapp logs show --name mangafinder-bot --resource-group <your-resource-group> --follow
```
