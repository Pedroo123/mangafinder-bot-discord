# Deployment Guide: MangaFinder Bot on Azure Container Apps

This document provides instructions for deploying the MangaFinder Bot to Azure Container Apps.

## Prerequisites

- Azure CLI installed and configured.
- A Reddit API application (Client ID and Secret).
- A Discord Bot Token.

## Containerization

The bot is containerized using a `Dockerfile` that follows security best practices:
- Uses a minimal `python:3.12-slim` base image.
- Runs as a non-root user (`appuser` with UID 5678).
- Optimized for Python performance (`PYTHONDONTWRITEBYTECODE`, `PYTHONUNBUFFERED`).
- Includes a healthcheck to ensure the bot process is running.

## Local Testing

You can test the container locally using Docker Compose:

1. Create a `.env` file based on `.env.example`.
2. Run `docker-compose up --build`.

## Azure Deployment Steps

### 1. Create a Container Registry (ACR)

```bash
az acr create --resource-group <resource-group> --name <registry-name> --sku Basic
```

### 2. Build and Push Image

```bash
az acr build --registry <registry-name> --image mangafinder-bot:latest .
```

### 3. Create a Container App Environment

```bash
az containerapp env create --name <env-name> --resource-group <resource-group> --location <location>
```

### 4. Deploy the Container App

The bot does not require an ingress as it is a worker process.

```bash
az containerapp create \
  --name mangafinder-bot \
  --resource-group <resource-group> \
  --environment <env-name> \
  --image <registry-name>.azurecr.io/mangafinder-bot:latest \
  --registry-server <registry-name>.azurecr.io \
  --cpu 0.25 --memory 0.5Gi \
  --env-vars \
    DISCORD_TOKEN=<token> \
    REDDIT_CLIENT_ID=<id> \
    REDDIT_CLIENT_SECRET=<secret> \
    REDDIT_USERNAME=<username> \
    REDDIT_PASSWORD=<password> \
    REDDIT_USER_AGENT="mangafinder-bot/0.1"
```

## Monitoring

- **Logs:** Use `az containerapp logs show` to view the bot's output.
- **Health:** The healthcheck is monitored by Azure to ensure reliability.
