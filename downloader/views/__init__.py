from .home import home
from .auth import login_view, logout_view
from .download import download_video, download_video_task
from .video import video_list, search_videos, get_video_url, play_media, get_player_html, delete_video, get_thumbnail
from .playlist import create_playlist, playlist_list, add_to_playlist, edit_playlist, delete_playlist, update_video_playlists, get_playlist_select, get_playlist_modal

__all__ = [
    'home',
    'login_view', 'logout_view',
    'download_video', 'download_video_task',
    'video_list', 'search_videos', 'get_video_url', 'delete_video', 'get_thumbnail',
    'create_playlist', 'playlist_list', 'add_to_playlist', 'edit_playlist', 'delete_playlist', 'update_video_playlists', 'get_playlist_select', 'get_playlist_modal',
]
