from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import json
import threading
import time
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
DOWNLOAD_DIR = '/app/downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Store download progress
download_status = {}

class DownloadLogger:
    def __init__(self, download_id):
        self.download_id = download_id

    def debug(self, msg):
        pass

    def info(self, msg):
        if self.download_id in download_status:
            download_status[self.download_id]['log'].append(msg)

    def warning(self, msg):
        if self.download_id in download_status:
            download_status[self.download_id]['log'].append(f"WARNING: {msg}")

    def error(self, msg):
        if self.download_id in download_status:
            download_status[self.download_id]['log'].append(f"ERROR: {msg}")
            download_status[self.download_id]['status'] = 'error'

def progress_hook(d, download_id):
    if download_id not in download_status:
        return

    if d['status'] == 'downloading':
        # Update download progress
        if 'total_bytes' in d and d['total_bytes']:
            percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
            download_status[download_id]['progress'] = round(percent, 1)
        elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
            percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
            download_status[download_id]['progress'] = round(percent, 1)
        elif '_percent_str' in d:
            percent_str = d['_percent_str'].replace('%', '').strip()
            try:
                download_status[download_id]['progress'] = float(percent_str)
            except:
                pass

        # Update playlist progress if available
        if 'playlist_index' in d and 'playlist_count' in d:
            download_status[download_id]['playlist_progress'] = {
                'current': d['playlist_index'],
                'total': d['playlist_count']
            }

    elif d['status'] == 'finished':
        # Video download finished, now converting to MP3
        download_status[download_id]['progress'] = 95
        download_status[download_id]['log'].append("Download finished, now converting to MP3...")

    elif d['status'] == 'error':
        download_status[download_id]['status'] = 'error'
        download_status[download_id]['log'].append("Error during download")

def is_playlist(url):
    """Check if the URL is a YouTube playlist"""
    playlist_patterns = [
        r'[&?]list=',  # Contains list parameter
        r'playlist\?',  # Direct playlist URL
        r'/playlist',   # Playlist path
    ]

    for pattern in playlist_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    return False

def get_playlist_info(url):
    """Get basic playlist information"""
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # Don't download, just get info
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if info.get('_type') == 'playlist':
                return {
                    'is_playlist': True,
                    'title': info.get('title', 'Unknown Playlist'),
                    'video_count': len(info.get('entries', [])),
                    'uploader': info.get('uploader', 'Unknown'),
                }
    except Exception as e:
        return {'is_playlist': False, 'error': str(e)}

    return {'is_playlist': False}

def download_youtube_video(url, download_id, download_playlist=False):
    try:
        # Status dict already initialized in /download route, just add to log
        download_status[download_id]['log'].append("Starting yt-dlp download process...")

        # Check if it's a playlist and user wants single video
        if is_playlist(url) and not download_playlist:
            download_status[download_id]['log'].append("Extracting single video from playlist URL...")
        elif is_playlist(url) and download_playlist:
            download_status[download_id]['is_playlist'] = True
            download_status[download_id]['log'].append("Downloading entire playlist...")

        # Post-processor hook for conversion progress
        def postprocessor_hook(d):
            if d['status'] == 'started':
                download_status[download_id]['log'].append(f"Post-processing: {d.get('postprocessor', 'processing')}...")
            elif d['status'] == 'finished':
                download_status[download_id]['log'].append("Post-processing complete!")

        # Configure download options
        ydl_opts = {
            'logger': DownloadLogger(download_id),
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            'postprocessor_hooks': [postprocessor_hook],
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': False,
        }

        # If user wants single video from a playlist, don't download the whole playlist
        if is_playlist(url) and not download_playlist:
            ydl_opts['noplaylist'] = True
            download_status[download_id]['log'].append("Option: noplaylist=True (single video only)")

        # Set output template based on playlist or single video
        if download_status[download_id]['is_playlist']:
            ydl_opts['outtmpl'] = os.path.join(DOWNLOAD_DIR, '%(playlist_title)s/%(title)s.%(ext)s')
        else:
            ydl_opts['outtmpl'] = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')

        download_status[download_id]['log'].append("Connecting to YouTube...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Ensure status is marked as completed after download finishes
        if download_status[download_id]['status'] != 'error':
            download_status[download_id]['status'] = 'completed'
            download_status[download_id]['progress'] = 100
            download_status[download_id]['log'].append("✓ Download completed successfully!")

    except Exception as e:
        download_status[download_id]['status'] = 'error'
        download_status[download_id]['progress'] = 0
        download_status[download_id]['log'].append(f"✗ Error: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    download_playlist = data.get('download_playlist', False)
    confirmed = data.get('confirmed', False)

    print(f"[DEBUG] Download request - URL: {url[:50]}..., playlist: {download_playlist}, confirmed: {confirmed}")

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Check if it's a playlist first (unless already confirmed by user)
    if is_playlist(url) and not download_playlist and not confirmed:
        print(f"[DEBUG] Playlist detected, asking for confirmation")
        playlist_info = get_playlist_info(url)
        if playlist_info['is_playlist']:
            return jsonify({
                'playlist_detected': True,
                'playlist_info': playlist_info
            })

    # Generate unique download ID
    download_id = f"{int(time.time())}_{hash(url) % 10000}"

    # Initialize status BEFORE starting thread (prevent race condition)
    download_status[download_id] = {
        'status': 'downloading',
        'progress': 0,
        'log': ['Initializing download...'],
        'filename': None,
        'is_playlist': False,
        'playlist_progress': {'current': 0, 'total': 0}
    }

    print(f"[DEBUG] Starting download with ID: {download_id}")

    # Start download in background thread
    thread = threading.Thread(target=download_youtube_video, args=(url, download_id, download_playlist))
    thread.daemon = True
    thread.start()

    return jsonify({'download_id': download_id})

@app.route('/check-playlist', methods=['POST'])
def check_playlist():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    playlist_info = get_playlist_info(url)
    return jsonify(playlist_info)

@app.route('/status/<download_id>')
def get_status(download_id):
    print(f"[DEBUG] Status check for ID: {download_id}")
    print(f"[DEBUG] Available IDs: {list(download_status.keys())}")

    if download_id not in download_status:
        print(f"[DEBUG] Download ID not found!")
        return jsonify({'error': 'Download not found'}), 404

    status_data = download_status[download_id]
    print(f"[DEBUG] Returning status: {status_data['status']}, progress: {status_data['progress']}")
    return jsonify(status_data)

@app.route('/downloads')
def list_downloads():
    files = []
    for filename in os.listdir(DOWNLOAD_DIR):
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            files.append({
                'name': filename,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

    files.sort(key=lambda x: x['modified'], reverse=True)
    return jsonify(files)

@app.route('/download_file/<filename>')
def download_file(filename):
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)