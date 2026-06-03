# Deployment Guide for MangaFinder Bot

This bot is designed to be hosted on **Azure Container Apps** with minimal infrastructure requirements.

## Azure Container Apps Setup

Since the bot is a Discord bot that initiates connections and does not need to listen for incoming traffic, the setup is straightforward.

### 1. Requirements

- Azure Subscription
- Azure Container Registry (ACR) to store the image
- Azure Container App environment

### 2. Deployment Configuration

- **Ingress**: Disabled (the bot does not need an HTTP endpoint).
- **Target Port**: None.
- **CPU/Memory**: 0.25 CPU and 0.5Gi memory is sufficient for small user bases.

### 3. Environment Variables

The following environment variables must be configured in the Container App's "Secrets" and "Configuration" sections:

| Variable | Description |
|----------|-------------|
| `DISCORD_TOKEN` | Your Discord bot token from the developer portal. |
| `REDDIT_CLIENT_ID` | Your Reddit API Client ID. |
| `REDDIT_CLIENT_SECRET` | Your Reddit API Client Secret. |
| `REDDIT_USERNAME` | Your Reddit account username. |
| `REDDIT_PASSWORD` | Your Reddit account password. |
| `REDDIT_USER_AGENT` | A descriptive user agent (e.g., `mangafinder-bot/0.1 by [YourName]`). |

### 4. Healthcheck

The `Dockerfile` includes a healthcheck using `pgrep`:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD pgrep -f "python src/main.py" || exit 1
```
Azure Container Apps will use this to ensure the bot process is alive.

## Local Deployment with Docker

You can test the container locally using:

```bash
docker build -t mangafinder-bot .
docker run --env-file .env mangafinder-bot
```

Or using Docker Compose:

```bash
docker-compose up --build
```
