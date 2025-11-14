from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Playlist, Video

@login_required
def create_playlist(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Playlist.objects.create(name=name, user=request.user)
            messages.success(request, 'Playlist created')
        return redirect('playlist_list')
    template = 'downloader/create_playlist_content.html' if request.htmx else 'downloader/create_playlist.html'
    return render(request, template)

@login_required
def playlist_list(request):
    playlists = Playlist.objects.filter(user=request.user)
    template = 'downloader/playlist_list_content.html' if request.htmx else 'downloader/playlist_list.html'
    return render(request, template, {'playlists': playlists})

@login_required
def add_to_playlist(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    if request.method == 'POST':
        playlist_id = request.POST.get('playlist')
        playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
        playlist.videos.add(video)
        messages.success(request, 'Video added to playlist')
    return redirect('video_list')

@login_required
def edit_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            playlist.name = name
            playlist.save()
            messages.success(request, 'Playlist updated')
        return redirect('playlist_list')

@login_required
def delete_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    if request.method == 'POST':
        playlist.delete()
        messages.success(request, 'Playlist deleted')
    return redirect('playlist_list')

@login_required
def update_video_playlists(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    if request.method == 'POST':
        playlist_ids = request.POST.getlist('playlists')
        playlists = Playlist.objects.filter(id__in=playlist_ids, user=request.user)
        video.playlist_set.set(playlists)
        messages.success(request, 'Playlists updated')
    return redirect(request.META.get('HTTP_HX_CURRENT_URL', 'video_list'))

@login_required
def get_playlist_select(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'downloader/_playlist_select.html', {'video': video, 'playlists': playlists})

@login_required
def get_playlist_modal(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    playlists = Playlist.objects.filter(user=request.user)
    return render(request, 'downloader/_playlist_modal.html', {'video': video, 'playlists': playlists})
