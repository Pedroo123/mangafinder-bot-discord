# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Labels for better image management
LABEL maintainer="Brankksss"
LABEL version="1.0"
LABEL description="Discord bot for searching manga on Reddit"

# Install procps for pgrep (used in healthcheck)
RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

# Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Create a non-root user for security
# Azure Container Apps can run as any user, but non-root is best practice
RUN adduser -u 5678 --disabled-password --gecos "" appuser

# Set work directory
WORKDIR /app

# Install dependencies
# Layer caching: only re-install if requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src/ /app/src/
COPY AGENTS.md /app/

# Set ownership to non-root user
RUN chown -R appuser /app

# Switch to non-root user
USER appuser

# Set the path so python can find the modules in src
ENV PYTHONPATH=/app/src

# Healthcheck to ensure the bot process is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD pgrep -f "python src/main.py" || exit 1

# Run the bot
CMD ["python", "src/main.py"]
