from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse, FileResponse, HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from .models import Video, Playlist
import yt_dlp
from django.conf import settings
import os
import uuid
import mimetypes
import requests
import threading
import glob

def home(request):
    if request.user.is_authenticated:
        return redirect('video_list')
    else:
        return redirect('login')

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
            display_title = f"{safe_channel} - {safe_title}"

            # Check if already exists
            if Video.objects.filter(youtube_url=url, user=request.user).exists():
                messages.error(request, 'Video already in queue or downloaded')
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

    return render(request, 'downloader/download.html')

@login_required
def video_list(request):
    videos = Video.objects.filter(user=request.user, status='downloaded').order_by('-created_at')[:10]
    return render(request, 'downloader/video_list.html', {'videos': videos})

@login_required
def search_videos(request):
    query = request.GET.get('q', '')
    videos = Video.objects.filter(user=request.user, title__icontains=query, status='downloaded') if query else Video.objects.none()
    return render(request, 'downloader/search.html', {'videos': videos, 'query': query})

@login_required
def get_video_url(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    if video.status != 'downloaded':
        return HttpResponse('Video not ready', status=404)
    filepath = os.path.join(settings.MEDIA_ROOT, video.local_path)
    if os.path.exists(filepath):
        content_type, _ = mimetypes.guess_type(filepath)
        return FileResponse(open(filepath, 'rb'), content_type=content_type or 'video/mp4')
    else:
        return JsonResponse({'error': 'File not found'}, status=404)

@login_required
def delete_video(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    if request.method == 'POST':
        # Delete all files with the base name (handles different extensions and temp files)
        base_name = video.title
        for file_path in glob.glob(os.path.join(settings.MEDIA_ROOT, f"{base_name}.*")):
            if os.path.exists(file_path):
                os.remove(file_path)
        # Delete from DB
        video.delete()
        messages.success(request, 'Video deleted successfully')
        return redirect('video_list')
    return redirect('video_list')

@login_required
def get_thumbnail(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    if video.status != 'downloaded' or not video.thumbnail_path:
        return HttpResponse(status=404)
    filepath = os.path.join(settings.MEDIA_ROOT, video.thumbnail_path)
    if os.path.exists(filepath):
        content_type, _ = mimetypes.guess_type(filepath)
        with open(filepath, 'rb') as f:
            return HttpResponse(f.read(), content_type=content_type or 'image/jpeg')
    else:
        return HttpResponse(status=404)

@login_required
def create_playlist(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Playlist.objects.create(name=name, user=request.user)
            messages.success(request, 'Playlist created')
        return redirect('playlist_list')
    return render(request, 'downloader/create_playlist.html')

@login_required
def playlist_list(request):
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'downloader/playlist_list.html', {'playlists': playlists})

@login_required
def add_to_playlist(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    if request.method == 'POST':
        playlist_id = request.POST.get('playlist')
        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
        playlist.videos.add(video)
        messages.success(request, 'Video added to playlist')
    return redirect('video_list')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('video_list')
    else:
        form = AuthenticationForm()
    return render(request, 'downloader/login.html', {'form': form})

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

        # Find the actual file
        actual_files = glob.glob(os.path.join(settings.MEDIA_ROOT, f"{base_name}.*"))
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

def logout_view(request):
    logout(request)
    return redirect('login')
