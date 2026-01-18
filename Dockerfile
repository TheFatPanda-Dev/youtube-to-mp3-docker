FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir \
    yt-dlp \
    flask \
    flask-cors

# Create downloads directory
RUN mkdir -p /app/downloads

# Copy application files
COPY app.py /app/
COPY templates/ /app/templates/
COPY static/ /app/static/

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the application
CMD ["python", "app.py"]