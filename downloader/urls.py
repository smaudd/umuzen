from django.urls import path
from .views import (
    home,
    login_view, logout_view,
    download_video,
    video_list, search_videos, get_video_url, play_media, delete_video, get_thumbnail,
    create_playlist, playlist_list, add_to_playlist, edit_playlist, delete_playlist, update_video_playlists, get_playlist_select, get_playlist_modal,
)
from .views.video import get_player_html

urlpatterns = [
    path('', home, name='home'),
    path('download/', download_video, name='download'),
    path('videos/', video_list, name='video_list'),
    path('search/', search_videos, name='search_videos'),
    path('video/<int:video_id>/url/', get_video_url, name='get_video_url'),
    path('video/<int:video_id>/play/', play_media, name='play_media'),
    path('video/<int:video_id>/player/', get_player_html, name='get_player_html'),
    path('video/<int:video_id>/thumbnail/', get_thumbnail, name='get_thumbnail'),
    path('video/<int:video_id>/delete/', delete_video, name='delete_video'),
    path('playlists/create/', create_playlist, name='create_playlist'),
    path('playlists/', playlist_list, name='playlist_list'),
    path('playlists/<int:playlist_id>/edit/', edit_playlist, name='edit_playlist'),
    path('playlists/<int:playlist_id>/delete/', delete_playlist, name='delete_playlist'),
    path('video/<int:video_id>/playlist_select/', get_playlist_select, name='get_playlist_select'),
    path('video/<int:video_id>/playlist_modal/', get_playlist_modal, name='get_playlist_modal'),
    path('video/<int:video_id>/update_playlists/', update_video_playlists, name='update_video_playlists'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
