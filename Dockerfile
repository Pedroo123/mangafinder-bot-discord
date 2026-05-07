# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user for security
RUN adduser -u 5678 --disabled-password --gecos "" appuser

# Set work directory
WORKDIR /app

# Install dependencies
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

# Healthcheck for Azure Container Apps (optional but good practice)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD pgrep -f "python src/main.py" || exit 1

# Run the bot
CMD ["python", "src/main.py"]
