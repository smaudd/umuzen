from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse, HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from ..models import Video
from django.conf import settings
import os
import mimetypes
import glob

@login_required
def video_list(request):
    videos = Video.objects.filter(user=request.user, status='downloaded').order_by('-created_at')[:10]
    template = 'downloader/video_list_content.html' if request.htmx else 'downloader/video_list.html'
    return render(request, template, {'videos': videos})

@login_required
def search_videos(request):
    query = request.GET.get('q', '')
    videos = Video.objects.filter(user=request.user, title__icontains=query, status='downloaded') if query else Video.objects.none()
    template = 'downloader/search_content.html' if request.htmx else 'downloader/search.html'
    return render(request, template, {'videos': videos, 'query': query})

@login_required
def get_video_url(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    if video.status != 'downloaded':
        return HttpResponse('Video not ready', status=404)
    filepath = os.path.join(settings.MEDIA_ROOT, video.local_path)
    if os.path.exists(filepath):
        content_type, _ = mimetypes.guess_type(filepath)
        response = FileResponse(open(filepath, 'rb'), content_type=content_type or ('audio/mpeg' if video.media_type == 'audio' else 'video/mp4'))
        response['Accept-Ranges'] = 'bytes'
        return response
    else:
        return HttpResponse('File not found', status=404)

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
def get_player_html(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    if video.status != 'downloaded':
        return HttpResponse('<p>Media not ready</p>', status=404)
    return render(request, 'downloader/player.html', {'video': video})

@login_required
def play_media(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    if video.status != 'downloaded':
        return HttpResponse('Media not ready', status=404)
    return render(request, 'downloader/play.html', {'video': video})

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
