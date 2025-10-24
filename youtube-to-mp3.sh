#!/bin/bash

# YouTube to MP3 downloader script
# Usage: ./youtube-to-mp3.sh <youtube_url> [output_directory]

if [ $# -eq 0 ]; then
    echo "Usage: $0 <youtube_url> [output_directory]"
    echo "Example: $0 https://www.youtube.com/watch?v=VIDEO_ID /path/to/output"
    exit 1
fi

URL="$1"
OUTPUT_DIR="${2:-$HOME/Downloads}"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "Downloading YouTube video as MP3..."
echo "URL: $URL"
echo "Output directory: $OUTPUT_DIR"

# Download with yt-dlp
yt-dlp -x --audio-format mp3 \
    --audio-quality 0 \
    -o "$OUTPUT_DIR/%(title)s.%(ext)s" \
    --embed-metadata \
    --add-metadata \
    "$URL"

if [ $? -eq 0 ]; then
    echo "✅ Download completed successfully!"
    echo "Files saved to: $OUTPUT_DIR"
else
    echo "❌ Download failed. Please check the URL and try again."
    exit 1
fi