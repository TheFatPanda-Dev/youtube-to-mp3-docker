# 🐋 Portainer Deployment Guide for YouTube Downloader

This guide shows you how to deploy the YouTube Downloader using Portainer on your Synology NAS.

## 📋 Prerequisites

1. **Portainer installed** on your Synology NAS
2. **SSH access** to your Synology (for file upload)
3. **Docker** enabled on your Synology

## 🚀 Quick Deploy with Portainer

### Method 1: Using Portainer Stacks (Recommended)

1. **Upload project files to Synology:**
   ```bash
   # SSH into your Synology and create the directories
   sudo mkdir -p /volume1/docker/youtube-downloader
   sudo mkdir -p "/volume1/Torrents/Youtube Downloads"

   # Upload all files from this project to that directory
   # You can use SCP, SFTP, or Synology File Station
   ```2. **Access Portainer:**
   - Open your browser to: `http://YOUR_SYNOLOGY_IP:9000`
   - Login to your Portainer instance

3. **Create a new Stack:**
   - Go to **Stacks** → **Add Stack**
   - **Name:** `youtube-downloader`
   - **Build method:** Upload
   - Copy and paste the docker-compose.yml content below

4. **Deploy the Stack:**
   - Click **Deploy the stack**
   - Wait for the build and deployment to complete

### Method 2: Using Portainer App Templates

1. **Create Custom Template:**
   - Go to **App Templates** → **Custom Templates**
   - Click **Add Custom Template**

2. **Template Configuration:**
   ```json
   {
     "type": 3,
     "title": "YouTube Downloader",
     "description": "Web-based YouTube to MP3/MP4 downloader",
     "categories": ["Media", "Download"],
     "platform": "linux",
     "logo": "https://raw.githubusercontent.com/yt-dlp/yt-dlp/master/devscripts/logo.png",
     "repository": {
       "url": "https://github.com/your-username/youtube-downloader",
       "stackfile": "docker-compose.yml"
     }
   }
   ```

## 📝 Docker Compose for Portainer Stack

Copy this content when creating a stack in Portainer:

```yaml
version: '3.8'

services:
  youtube-downloader:
    build: .
    container_name: youtube-downloader
    ports:
      - "7843:5000"
    volumes:
      - "/volume1/Torrents/Youtube Downloads:/app/downloads"
      - /etc/localtime:/etc/localtime:ro
    environment:
      - FLASK_ENV=production
      - TZ=Europe/Amsterdam  # Change to your timezone
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000"]
      interval: 30s
      timeout: 10s
      retries: 3
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.youtube-downloader.rule=Host(\`downloader.local\`)"
      - "traefik.http.services.youtube-downloader.loadbalancer.server.port=5000"
```

## 🔧 Portainer Configuration Steps

### Step 1: Environment Variables
In Portainer, you can set these environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `TZ` | `Europe/Amsterdam` | Your timezone |

### Step 2: Volume Mapping
Configure these volume mappings in Portainer:

| Container Path | Host Path | Description |
|---------------|-----------|-------------|
| `/app/downloads` | `/volume1/Torrents/Youtube Downloads` | Download storage |
| `/etc/localtime` | `/etc/localtime` | System timezone (read-only) |

### Step 3: Port Mapping
| Container Port | Host Port | Protocol |
|---------------|-----------|----------|
| `5000` | `7843` | TCP |

### Step 4: Network Settings
- **Network Mode:** `bridge` (default)
- **DNS:** Use automatic or set to `8.8.8.8, 1.1.1.1`

## 🌐 Advanced Portainer Setup with Reverse Proxy

If you're using Traefik or Nginx Proxy Manager with Portainer:

### Traefik Labels (add to docker-compose.yml)
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.youtube-downloader.rule=Host(`downloader.yourdomain.com`)"
  - "traefik.http.routers.youtube-downloader.entrypoints=websecure"
  - "traefik.http.routers.youtube-downloader.tls.certresolver=myresolver"
  - "traefik.http.services.youtube-downloader.loadbalancer.server.port=5000"
```

### Nginx Proxy Manager
1. **Add Proxy Host** in Nginx Proxy Manager
2. **Domain:** `downloader.yourdomain.com`
3. **Forward to:** `youtube-downloader:5000`
4. **Enable SSL** with Let's Encrypt

## 📊 Monitoring in Portainer

### Container Health Monitoring
The container includes a health check that you can monitor in Portainer:
- **Endpoint:** `http://localhost:5000`
- **Interval:** 30 seconds
- **Timeout:** 10 seconds
- **Retries:** 3

### Log Monitoring
To view logs in Portainer:
1. Go to **Containers**
2. Click on `youtube-downloader`
3. Go to **Logs** tab
4. Enable **Auto-refresh** for real-time logs

## 🔍 Troubleshooting in Portainer

### Common Issues and Solutions

1. **Container won't start:**
   - Check **Logs** in Portainer
   - Verify volume mappings
   - Ensure port 7843 is available

2. **Build fails:**
   - Ensure all project files are uploaded
   - Check **Console** output in Stack deployment
   - Verify Dockerfile syntax

3. **Downloads fail:**
   - Check container logs
   - Verify internet connectivity
   - Test with a simple YouTube URL

### Useful Portainer Commands

**Rebuild Stack:**
1. Go to **Stacks** → `youtube-downloader`
2. Click **Editor**
3. Click **Update the stack**
4. Enable **Re-pull image and redeploy**

**Container Shell Access:**
1. Go to **Containers** → `youtube-downloader`
2. Click **Console**
3. Select **Command:** `/bin/bash`
4. Click **Connect**

## 🚦 Deployment Checklist

- [ ] Portainer is running and accessible
- [ ] Project files uploaded to `/volume1/docker/youtube-downloader/`
- [ ] Stack created with correct docker-compose.yml
- [ ] Environment variables configured
- [ ] Volume mappings set correctly
- [ ] Port 7843 is available and mapped
- [ ] Container is running and healthy
- [ ] Web interface accessible at `http://SYNOLOGY_IP:7843`
- [ ] Test download works correctly

## 🔗 Quick Access Links

After deployment, you can access:
- **Web Interface:** `http://YOUR_SYNOLOGY_IP:7843`
- **Portainer Management:** `http://YOUR_SYNOLOGY_IP:9000`
- **Download Files:** Via the web interface or Synology File Station

## 📱 Mobile Access

The web interface is mobile-friendly and can be accessed from:
- **Local Network:** `http://SYNOLOGY_IP:7843`
- **VPN:** Same URL when connected to your network
- **Domain:** If you set up reverse proxy with domain

## 🔄 Updates and Maintenance

### Updating the Container
1. In Portainer, go to **Stacks** → `youtube-downloader`
2. Click **Editor**
3. Make any changes needed
4. Click **Update the stack**
5. Enable **Re-pull image and redeploy**

### Backup Configuration
- Export stack definition from Portainer
- Backup `/volume1/docker/youtube-downloader/` directory
- Include volume mappings and environment variables

This setup gives you a professional, manageable YouTube downloader running on your Synology with full Portainer integration! 🎉