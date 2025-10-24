# 🎯 Quick Deploy Template for Portainer

Use this template for quick deployment in Portainer App Templates.

## App Template JSON

Copy this JSON configuration when creating a custom template in Portainer:

```json
{
  "type": 3,
  "title": "YouTube Downloader",
  "description": "Web-based YouTube to MP3/MP4 downloader with real-time progress tracking",
  "note": "Deploy a containerized YouTube downloader with a beautiful web interface. Perfect for downloading YouTube content as MP3 or MP4 files.",
  "categories": ["Media", "Download", "Utility"],
  "platform": "linux",
  "logo": "https://cdn-icons-png.flaticon.com/512/1384/1384060.png",
  "name": "youtube-downloader",
  "image": "youtube-downloader:latest",
  "network": "bridge",
  "volumes": [
    {
      "container": "/app/downloads",
      "bind": "/volume1/Torrents/Youtube Downloads"
    },
    {
      "container": "/etc/localtime",
      "bind": "/etc/localtime",
      "readonly": true
    }
  ],
  "ports": [
    {
      "label": "Web Interface",
      "description": "Web interface for YouTube downloading",
      "host": "7843",
      "container": "5000",
      "protocol": "tcp"
    }
  ],
  "env": [
    {
      "name": "FLASK_ENV",
      "label": "Flask Environment",
      "default": "production",
      "description": "Flask application environment"
    },
    {
      "name": "TZ",
      "label": "Timezone",
      "default": "Europe/Amsterdam",
      "description": "Container timezone (e.g., America/New_York, Europe/London)"
    }
  ],
  "restart_policy": "unless-stopped",
  "command": "python app.py"
}
```

## Stack Template

For Portainer Stacks, use this docker-compose.yml:

```yaml
version: '3.8'

services:
  youtube-downloader:
    build: .
    container_name: youtube-downloader
    ports:
      - "${WEB_PORT:-7843}:5000"
    volumes:
      - ${DATA_DIR:-"/volume1/Torrents/Youtube Downloads"}:/app/downloads
      - /etc/localtime:/etc/localtime:ro
    environment:
      - FLASK_ENV=${FLASK_ENV:-production}
      - TZ=${TIMEZONE:-UTC}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    labels:
      - "com.centurylinklabs.watchtower.enable=true"
      - "app.name=youtube-downloader"
      - "app.description=YouTube to MP3/MP4 downloader"
```

## Environment Variables Template

```bash
# Port Configuration
WEB_PORT=7843

# Storage Configuration
DATA_DIR="/volume1/Torrents/Youtube Downloads"# Application Configuration
FLASK_ENV=production
TIMEZONE=Europe/Amsterdam

# Optional: Custom download settings
MAX_DOWNLOAD_SIZE=500M
CONCURRENT_DOWNLOADS=3
```