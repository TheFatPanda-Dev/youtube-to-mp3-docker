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
        if 'total_bytes' in d and d['total_bytes']:
            percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
            download_status[download_id]['progress'] = round(percent, 1)
        elif '_percent_str' in d:
            percent_str = d['_percent_str'].replace('%', '')
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
        download_status[download_id]['status'] = 'completed'
        download_status[download_id]['progress'] = 100
        download_status[download_id]['filename'] = os.path.basename(d['filename'])

def download_youtube_video(url, download_id):
    try:
        download_status[download_id] = {
            'status': 'downloading',
            'progress': 0,
            'log': [],
            'filename': None
        }

        # Force MP3-only download configuration
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'logger': DownloadLogger(download_id),
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:
        download_status[download_id]['status'] = 'error'
        download_status[download_id]['log'].append(f"Error: {str(e)}")

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
        download_status[download_id] = {
            'status': 'downloading',
            'progress': 0,
            'log': [],
            'filename': None,
            'is_playlist': False,
            'playlist_progress': {'current': 0, 'total': 0}
        }

        # Check if it's a playlist
        if is_playlist(url):
            download_status[download_id]['is_playlist'] = True
            if not download_playlist:
                download_status[download_id]['status'] = 'playlist_detected'
                download_status[download_id]['log'].append("Playlist detected. Please confirm if you want to download the entire playlist.")
                return

        # Configure download options
        ydl_opts = {
            'logger': DownloadLogger(download_id),
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        # Set output template based on playlist or single video
        if download_status[download_id]['is_playlist']:
            ydl_opts['outtmpl'] = os.path.join(DOWNLOAD_DIR, '%(playlist_title)s/%(title)s.%(ext)s')
            download_status[download_id]['log'].append("Downloading playlist...")
        else:
            ydl_opts['outtmpl'] = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:
        download_status[download_id]['status'] = 'error'
        download_status[download_id]['log'].append(f"Error: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    download_playlist = data.get('download_playlist', False)

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Check if it's a playlist first
    if is_playlist(url) and not download_playlist:
        playlist_info = get_playlist_info(url)
        if playlist_info['is_playlist']:
            return jsonify({
                'playlist_detected': True,
                'playlist_info': playlist_info
            })

    # Generate unique download ID
    download_id = f"{int(time.time())}_{hash(url) % 10000}"

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
    return jsonify(playlist_info)@app.route('/status/<download_id>')
def get_status(download_id):
    if download_id not in download_status:
        return jsonify({'error': 'Download not found'}), 404

    return jsonify(download_status[download_id])

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