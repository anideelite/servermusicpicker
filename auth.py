import os
import time
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler

# Usar la carpeta /tmp de Render para guardar el token de forma persistente entre llamadas
cache_path = os.path.join("/tmp", ".cache-spotify")
cache_handler = CacheFileHandler(cache_path=cache_path)

sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-modify-playback-state user-read-playback-state",
    cache_handler=cache_handler
)

def set_token_info(token_info):
    cache_handler.save_token_to_cache(token_info)

def get_token_info():
    token_info = cache_handler.get_cached_token()
    if not token_info:
        return None
    
    # Spotipy y CacheFileHandler se encargan automáticamente de revisar la expiración, 
    # pero aseguramos la validación del token actual.
    return token_info
