from flask import Blueprint, request, jsonify
from spotipy import Spotify
from auth import get_token_info
import random

bpm_blueprint = Blueprint("bpm", __name__)

playlist_uris = {
    "relajado": "spotify:playlist:2ObbFHzjAw5yucJ57MbqOn",
    "normal":   "spotify:playlist:3Lqw8YaDSWQRTkiIejggVT",
    "agitado":  "spotify:playlist:3Lqw8YaDSWQRTkiIejggVT"
}

@bpm_blueprint.route("/bpm", methods=["POST"])
def recibir_bpm():
    data = request.get_json()
    if not data or "bpm" not in data:
        return jsonify({"error": "Se requiere el valor 'bpm'"}), 400

    try:
        bpm = int(data["bpm"])
        if bpm < 75:
            categoria = "relajado"
        elif bpm <= 110:
            categoria = "normal"
        else:
            categoria = "agitado"

        token_info = get_token_info()
        if not token_info:
            return jsonify({"error": "Token inválido"}), 403

        sp = Spotify(auth=token_info["access_token"])

        # 1. Verificar si hay un dispositivo activo antes de ordenar reproducir
        devices = sp.devices()
        if not devices or not devices.get("devices"):
            return jsonify({"error": "No hay ningún dispositivo de Spotify activo. Abre Spotify en tu app."}), 400
        
        # Buscar un dispositivo activo o usar el primero disponible
        active_device_id = None
        for d in devices["devices"]:
            if d.get("is_active"):
                active_device_id = d["id"]
                break
        if not active_device_id:
            active_device_id = devices["devices"][0]["id"]

        # 2. Obtener canciones de la playlist
        playlist_uri = playlist_uris[categoria]
        results = sp.playlist_items(playlist_uri, additional_types=['track'])
        tracks = results["items"]
        
        # Manejar paginación por si la playlist tiene más de 100 canciones
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        # Filtrar solo elementos válidos que tengan pista
        valid_tracks = [t["track"] for t in tracks if t and t.get("track")]
        if not valid_tracks:
            return jsonify({"error": "Playlist vacía o sin canciones válidas"}), 500

        track = random.choice(valid_tracks)
        track_uri = track["uri"]
        track_name = track["name"]
        
        # 3. Forzar reproducción en el dispositivo detectado
        sp.start_playback(device_id=active_device_id, uris=[track_uri])

        return jsonify({
            "message": "BPM recibido y música actualizada", 
            "cancion": track_name, 
            "ya_reproduciendo": True
        }), 200

    except Exception as e:
        print(f"Error en /bpm: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bpm_blueprint.route("/estado_musica", methods=["GET"])
def estado_musica():
    try:
        token_info = get_token_info()
        if not token_info:
            return jsonify({"error": "Token inválido"}), 403

        sp = Spotify(auth=token_info["access_token"])
        current = sp.current_playback()
        if current and current.get("is_playing"):
            cancion = current["item"]["name"]
            return jsonify({"reproduciendo": True, "cancion": cancion}), 200
        else:
            return jsonify({"reproduciendo": False, "cancion": None}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
