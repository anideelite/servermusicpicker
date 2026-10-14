import os
from spotipy.oauth2 import SpotifyOAuth

sp_oauth = SpotifyOAuth(
    client_id=os.environ.get("SPOTIPY_CLIENT_ID"),
    client_secret=os.environ.get("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.environ.get("SPOTIPY_REDIRECT_URI"),
    scope="user-read-playback-state user-modify-playback-state playlist-read-private playlist-read-collaborative",
    cache_path="/tmp/.cache",  # <--- Usamos /tmp para que Railway sí lo deje escribir
    show_dialog=True
)

def get_token_info():
    return sp_oauth.get_cached_token()

def set_token_info(token_info):
    pass
