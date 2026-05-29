# Deployment Guide for MangaFinder Bot

This guide provides instructions on how to deploy the MangaFinder Discord bot to Azure Container Apps.

## Prerequisites

1.  **Azure CLI:** Installed and logged in (`az login`).
2.  **Docker:** Installed for local testing and building (optional if using ACR build).
3.  **Discord Bot Token:** Obtain one from the [Discord Developer Portal](https://discord.com/developers/applications).
4.  **Reddit API Credentials:** Obtain from [Reddit App Preferences](https://www.reddit.com/prefs/apps).

## Step-by-Step Deployment

### 1. Set Variables

```bash
RESOURCE_GROUP="MangaFinderRG"
LOCATION="eastus"
CONTAINER_APP_NAME="mangafinder-bot"
ACR_NAME="mangafinderregistry"
```

### 2. Create Resource Group

```bash
az group create --name $RESOURCE_GROUP --location $LOCATION
```

### 3. Create Azure Container Registry (ACR)

```bash
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true
```

### 4. Build and Push Image to ACR

```bash
az acr build --registry $ACR_NAME --image mangafinder-bot:v1 .
```

### 5. Create Container App Environment

```bash
az containerapp env create --name "mangafinder-env" --resource-group $RESOURCE_GROUP --location $LOCATION
```

### 6. Deploy Container App

Deploy the app with required environment variables. Ensure you replace the placeholders with your actual credentials.

```bash
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment "mangafinder-env" \
  --image "$ACR_NAME.azurecr.io/mangafinder-bot:v1" \
  --min-replicas 1 \
  --max-replicas 1 \
  --env-vars \
    DISCORD_TOKEN=your_discord_token \
    REDDIT_CLIENT_ID=your_reddit_client_id \
    REDDIT_CLIENT_SECRET=your_reddit_client_secret \
    REDDIT_USERNAME=your_reddit_username \
    REDDIT_PASSWORD=your_reddit_password \
    REDDIT_USER_AGENT="mangafinder-bot/0.1 by Brankksss"
```

*Note: We set replicas to 1 to ensure only one instance of the bot runs. Ingress is disabled as the bot does not need to listen for incoming HTTP traffic.*

## Verification

Check the logs to ensure the bot has started correctly:

```bash
az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --follow
```
