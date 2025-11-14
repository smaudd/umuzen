from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Video
import yt_dlp
import threading
import os
import glob
import requests
from django.conf import settings

@login_required
def download_video(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        media_type = request.POST.get('media_type', 'video')
        if not url:
            messages.error(request, 'URL is required')
            return redirect('download')

        try:
            # Get video info first
            with yt_dlp.YoutubeDL({'skip_download': True}) as ydl:
                info = ydl.extract_info(url, download=False)

            title = info['title']
            channel = info.get('uploader', 'Unknown')

            # Sanitize for filename and title
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_channel = "".join(c for c in channel if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if len(safe_title) > 80:
                safe_title = safe_title[:80]
            if len(safe_channel) > 30:
                safe_channel = safe_channel[:30]
            display_title = f"{safe_channel} - {safe_title} ({media_type})"

            # Check if already exists (same URL and media_type)
            if Video.objects.filter(youtube_url=url, media_type=media_type, user=request.user).exists():
                messages.error(request, f'{media_type.capitalize()} already downloaded for this video')
                return redirect('download')

            # Save to DB with info
            video = Video.objects.create(
                title=display_title,
                youtube_url=url,
                media_type=media_type,
                status='pending',
                user=request.user
            )

            # Start background download
            thread = threading.Thread(target=download_video_task, args=(video.id,))
            thread.daemon = True
            thread.start()

            messages.success(request, f'{media_type.capitalize()} "{title}" queued for download')
            return redirect('video_list')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('download')

    template = 'downloader/download_content.html' if request.htmx else 'downloader/download.html'
    return render(request, template)

def download_video_task(video_id):
    try:
        video = Video.objects.get(id=video_id)
        video.status = 'downloading'
        video.save()

        url = video.youtube_url
        media_type = video.media_type
        base_name = video.title

        # Ensure media directory exists
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        # Get video info for thumbnail
        with yt_dlp.YoutubeDL({'skip_download': True}) as ydl:
            info = ydl.extract_info(url, download=False)

        # Download thumbnail
        thumbnail_url = info.get('thumbnail')
        if thumbnail_url:
            response = requests.get(thumbnail_url)
            thumbnail_filename = f"{base_name}.jpg"
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, thumbnail_filename)
            with open(thumbnail_path, 'wb') as f:
                f.write(response.content)
        else:
            thumbnail_filename = None

        # Download video or audio
        if media_type == 'audio':
            ydl_opts = {
                'outtmpl': os.path.join(settings.MEDIA_ROOT, f"{base_name}.%(ext)s"),
                'format': 'bestaudio/best',
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    },
                    {
                        'key': 'EmbedThumbnail',
                    },
                    {
                        'key': 'FFmpegMetadata',
                        'add_metadata': True,
                    },
                ],
            }
        else:
            ydl_opts = {
                'outtmpl': os.path.join(settings.MEDIA_ROOT, f"{base_name}.%(ext)s"),
                'format': 'best',
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Find the actual file (exclude thumbnail .jpg)
        all_files = glob.glob(os.path.join(settings.MEDIA_ROOT, f"{base_name}.*"))
        actual_files = [f for f in all_files if not f.endswith('.jpg')]
        if actual_files:
            actual_filename = actual_files[0]
            video.local_path = os.path.basename(actual_filename)
        else:
            video.status = 'failed'
            video.save()
            return

        # Update DB
        video.thumbnail_path = thumbnail_filename
        video.status = 'downloaded'
        video.save()

    except Exception as e:
        video.status = 'failed'
        video.save()
