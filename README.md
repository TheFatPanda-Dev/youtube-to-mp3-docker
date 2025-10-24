# YouTube to MP3 Downloader Docker Container

A web-based YouTube to MP3 downloader that runs in a Docker container, perfect for hosting on your Synology NAS.

## Features

- 🎵 Download YouTube videos as high-quality MP3 files
- 📋 **Playlist support** - Download individual videos or entire playlists
- 🔍 **Smart detection** - Automatically detects playlists and asks for confirmation
- 🌐 Clean web interface accessible from any device
- 📱 Mobile-friendly responsive design
- 📊 Real-time download progress with playlist tracking
- 📂 Browse and download previous files
- 🔄 Background downloading with status updates

## Quick Start for Synology

**For Synology Deployment:**
```bash
# Create the download directory first
sudo mkdir -p "/volume1/Torrents/Youtube Downloads"

# Upload the entire youtube-downloader folder to your Synology
# Then SSH into your Synology and run:
cd /volume1/docker/youtube-downloader/
sudo docker-compose up -d --build
```

### Method 2: Using Synology Docker GUI

1. **Build the image first via SSH:**
   ```bash
   cd /volume1/docker/youtube-downloader/
   sudo docker build -t youtube-downloader .
   ```

2. **In Synology Docker GUI:**
   - Go to **Image** → **Add** → **From Image** → `youtube-downloader`
   - Configure container:
     - **Container Name:** `youtube-downloader`
     - **Port:** Local `7843` → Container `5000`
     - **Volume:** Map `/volume1/Torrents/Youtube Downloads` → `/app/downloads`
     - **Environment:** `FLASK_ENV=production`

## Usage

1. Open the web interface in your browser
2. Paste a YouTube URL (video or playlist)
3. If it's a playlist, choose to download single video or entire playlist
4. Click "Download as MP3"
5. Monitor progress in real-time
6. Download completed files from the "Recent Downloads" section

## File Structure

```
youtube-downloader/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Compose configuration
├── app.py                  # Flask web application
├── templates/
│   └── index.html         # Web interface
├── static/                # Static files (empty for now)
├── downloads/             # Downloaded files (created automatically)
└── README.md             # This file
```

## Configuration

### Environment Variables

- `FLASK_ENV`: Set to `production` for production use
- `FLASK_APP`: Application entry point (defaults to `app.py`)

### Volumes

- `/app/downloads`: Where downloaded files are stored
- Map this to `/volume1/Torrents/Youtube Downloads` on your Synology

### Ports

- `7843`: Web interface port
- You can change the external port in `docker-compose.yml`

## Security Notes

- This container runs on your local network
- Consider using a reverse proxy with authentication for external access
- The container runs as root for ffmpeg compatibility
- Downloaded files are stored in the mapped volume

## Troubleshooting

### Common Issues

1. **Container won't start:**
   - Check logs: `sudo docker logs youtube-downloader`
   - Ensure port 7843 is not in use

2. **Downloads fail:**
   - YouTube may have changed their API
   - Check container logs for yt-dlp errors
   - Try updating the container

3. **Permission issues:**
   - Ensure the downloads directory is writable
   - Check Synology folder permissions

### Updating

To update to the latest version:

```bash
cd /volume1/docker/youtube-downloader/
sudo docker-compose down
sudo docker-compose up -d --build
```

## Technical Details

- **Base Image:** Python 3.11 slim
- **Dependencies:** yt-dlp, Flask, ffmpeg
- **Download Engine:** yt-dlp (more reliable than ytdl-core)
- **Audio Processing:** ffmpeg
- **Web Framework:** Flask with real-time progress updates

## Support

This container is designed to be simple and reliable. The web interface provides real-time feedback and error messages to help diagnose any issues.