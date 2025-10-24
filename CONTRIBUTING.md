# Contributing to YouTube to MP3 Downloader

Thank you for your interest in contributing! This project welcomes contributions from the community.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/youtube-downloader.git
   cd youtube-downloader
   ```

2. Build and run locally:
   ```bash
   docker-compose up --build
   ```

3. Access the application at `http://localhost:7843`

## Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and test them locally

3. Commit your changes:
   ```bash
   git commit -m "Add your descriptive commit message"
   ```

4. Push to your fork and create a pull request

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Update documentation for new features

## Testing

- Test the Docker build: `docker build -t youtube-downloader .`
- Test the web interface manually
- Verify downloads work with both single videos and playlists

## Reporting Issues

When reporting issues, please include:
- Operating system and version
- Docker version
- Steps to reproduce the issue
- Expected vs actual behavior
- Any error messages or logs

## Feature Requests

Feature requests are welcome! Please open an issue to discuss new features before implementing them.