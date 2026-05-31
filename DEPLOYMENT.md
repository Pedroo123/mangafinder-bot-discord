# Deployment Guide: Azure Container Apps

This guide outlines how to deploy the MangaFinder Discord Bot to Azure Container Apps.

## Prerequisites

- An Azure account with an active subscription.
- Azure CLI installed.
- Docker installed (for local builds).
- A Discord Bot Token and Reddit API Credentials.

## Configuration

The bot requires the following environment variables:

- `DISCORD_TOKEN`: Your Discord bot token.
- `REDDIT_CLIENT_ID`: Reddit API client ID.
- `REDDIT_CLIENT_SECRET`: Reddit API client secret.
- `REDDIT_USERNAME`: Your Reddit username.
- `REDDIT_PASSWORD`: Your Reddit password.
- `REDDIT_USER_AGENT`: (Optional) A custom user agent.

## Deployment Steps

### 1. Build and Push Docker Image

You can use Azure Container Registry (ACR) to host your image.

```bash
# Login to Azure
az login

# Create a resource group
az group create --name MangaFinderRG --location eastus

# Create an ACR
az acr create --resource-group MangaFinderRG --name mangafinderacr --sku Basic

# Login to ACR
az acr login --name mangafinderacr

# Build and tag the image
docker build -t mangafinderacr.azurecr.io/mangafinder-bot:latest .

# Push to ACR
docker push mangafinderacr.azurecr.io/mangafinder-bot:latest
```

### 2. Create Azure Container App

Since the bot is a background worker and does not need to handle HTTP requests, we disable ingress.

```bash
# Create Container App Environment
az containerapp env create --name MangaFinderEnv --resource-group MangaFinderRG --location eastus

# Create the Container App
az containerapp create \
  --name mangafinder-bot \
  --resource-group MangaFinderRG \
  --environment MangaFinderEnv \
  --image mangafinderacr.azurecr.io/mangafinder-bot:latest \
  --secrets "discord-token=<YOUR_TOKEN>" "reddit-id=<YOUR_ID>" "reddit-secret=<YOUR_SECRET>" "reddit-user=<YOUR_USER>" "reddit-pass=<YOUR_PASS>" \
  --env-vars "DISCORD_TOKEN=secretref:discord-token" "REDDIT_CLIENT_ID=secretref:reddit-id" "REDDIT_CLIENT_SECRET=secretref:reddit-secret" "REDDIT_USERNAME=secretref:reddit-user" "REDDIT_PASSWORD=secretref:reddit-pass" \
  --registry-server mangafinderacr.azurecr.io \
  --ingress internal \
  --target-port 80 \
  --cpu 0.25 --memory 0.5Gi \
  --min-replicas 1 --max-replicas 1
```

*Note: Although ingress is set to internal/80, the bot won't actually listen on it. Azure Container Apps currently requires a port for healthchecks if ingress is enabled, but for a pure background worker, you can also explore Azure Container Instances if preferred.*

### 3. Monitoring

You can view logs using:

```bash
az containerapp logs show --name mangafinder-bot --resource-group MangaFinderRG
```

## Security Best Practices

- Always use Azure Key Vault or Container App Secrets for credentials.
- Ensure the Docker image runs as a non-root user (already configured in our `Dockerfile`).
- Keep the base image updated.
