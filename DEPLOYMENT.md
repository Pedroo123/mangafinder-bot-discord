# Deployment Guide - Azure Container Apps

This guide describes how to deploy the MangaFinder Discord Bot to Azure Container Apps.

## Prerequisites

1.  **Azure CLI** installed and logged in (`az login`).
2.  **Docker** installed for local image building (optional if using ACR tasks).
3.  **Discord Bot Token** and **Reddit API Credentials**.

## Step 1: Create an Azure Container Registry (ACR)

```bash
az acr create --resource-group <your-resource-group> --name <your-registry-name> --sku Basic
az acr login --name <your-registry-name>
```

## Step 2: Build and Push the Docker Image

```bash
docker build -t <your-registry-name>.azurecr.io/mangafinder-bot:latest .
docker push <your-registry-name>.azurecr.io/mangafinder-bot:latest
```

## Step 3: Create the Container App Environment

```bash
az containerapp env create --name mangafinder-env --resource-group <your-resource-group> --location <location>
```

## Step 4: Deploy the Container App

Since the bot is a background worker (it doesn't listen for HTTP traffic), we disable ingress.

```bash
az containerapp create \
  --name mangafinder-bot \
  --resource-group <your-resource-group> \
  --environment mangafinder-env \
  --image <your-registry-name>.azurecr.io/mangafinder-bot:latest \
  --registry-server <your-registry-name>.azurecr.io \
  --ingress disabled \
  --secrets \
    discord-token="<your-discord-token>" \
    reddit-client-id="<your-reddit-id>" \
    reddit-client-secret="<your-reddit-secret>" \
    reddit-username="<your-reddit-username>" \
    reddit-password="<your-reddit-password>" \
  --env-vars \
    DISCORD_TOKEN=secretref:discord-token \
    REDDIT_CLIENT_ID=secretref:reddit-client-id \
    REDDIT_CLIENT_SECRET=secretref:reddit-client-secret \
    REDDIT_USERNAME=secretref:reddit-username \
    REDDIT_PASSWORD=secretref:reddit-password \
    REDDIT_USER_AGENT="mangafinder-bot/1.0 by <your-username>"
```

## Important Notes

- **Scale to Zero**: Azure Container Apps can scale to zero, but for a Discord bot, you likely want at least one replica running (`--min-replicas 1 --max-replicas 1`).
- **Security**: The `Dockerfile` is configured to run as a non-root user (`appuser`).
- **Monitoring**: You can view logs using `az containerapp logs show`.
