# Umuzen - Django YouTube Downloader

Django web application for downloading YouTube videos and audio with a nostalgic Windows XP-inspired interface.

## Features

- **User Authentication**: Secure login system for personalized access
- **Video/Audio Downloads**: Download videos in MP4/MP3
- **Playlist Management**: WIP
- **Thumbnail Support**: Automatic thumbnail fetching and display
- **Async Processing**: Background downloads using threading for smooth UX
- **Global Player**: WIP

## Tech Stack

- **Backend**: Django 5.2.8
- **Frontend**: XP.css, HTMX, Vanilla JavaScript
- **Video Processing**: yt-dlp, FFmpeg
- **Database**: SQLite (development) / PostgreSQL (production)
- **Async**: Python threading
- **HTTP Client**: requests

## Requirements

- Python 3.8+
- FFmpeg (for audio conversion)
- yt-dlp (YouTube downloader)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/smaudd/umuzen.git
   cd umuzen
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install system dependencies:**

   - FFmpeg: `brew install ffmpeg` (macOS) or download from https://ffmpeg.org/
   - yt-dlp: `pip install yt-dlp` (or `brew install yt-dlp`)

5. **Run migrations:**

   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional):**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server:**

   ```bash
   python manage.py runserver
   ```

8. **Access the app:**
   Open http://localhost:8000 in your browser

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube downloading
- [XP.css](https://github.com/botoxparty/XP.css) for the Windows XP theme
- [HTMX](https://htmx.org/) for seamless frontend interactions
- [Django](https://www.djangoproject.com/) for the robust backend framework
