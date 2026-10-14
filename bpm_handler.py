from flask import Blueprint, request, jsonify
from spotipy import Spotify
from auth import sp_oauth
import random

bpm_blueprint = Blueprint("bpm", __name__)

playlist_uris = {
    "relajado": "spotify:playlist:2PorBhwNt28E7OzrIYCauY",
    "normal":   "spotify:playlist:0EwgVn5TPobpQd5pucCppp",
    "agitado":  "spotify:playlist:12TzlhPrV36sAB4TN0dJF8"
}

@bpm_blueprint.route("/bpm", methods=["POST"])
def recibir_bpm():
    data = request.get_json()
    if not data or "bpm" not in data:
        return jsonify({"error": "Se requiere el valor 'bpm'"}), 400

    try:
        bpm = int(data["bpm"])
        categoria = "relajado" if bpm < 75 else ("normal" if bpm <= 110 else "agitado")

        token_info = sp_oauth.get_cached_token()
        if not token_info:
            return jsonify({"error": "No autorizado. Inicia sesión en la web."}), 403

        sp = Spotify(auth=token_info["access_token"])

        # Detectar dispositivo activo en Spotify
        devices = sp.devices()
        if not devices or not devices.get("devices"):
            return jsonify({"error": "Abre Spotify en tu app o PC"}), 400
        
        active_device_id = next((d["id"] for d in devices["devices"] if d.get("is_active")), devices["devices"][0]["id"])

        # Seleccionar canción aleatoria
        playlist_uri = playlist_uris[categoria]
        results = sp.playlist_items(playlist_uri, additional_types=['track'])
        valid_tracks = [t["track"] for t in results["items"] if t and t.get("track")]
        
        if not valid_tracks:
            return jsonify({"error": "Playlist vacía"}), 500

        track = random.choice(valid_tracks)
        sp.start_playback(device_id=active_device_id, uris=[track["uri"]])

        return jsonify({
            "message": "BPM recibido y música actualizada", 
            "cancion": track["name"], 
            "ya_reproduciendo": True
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bpm_blueprint.route("/estado_musica", methods=["GET"])
def estado_musica():
    try:
        token_info = sp_oauth.get_cached_token()
        if not token_info:
            return jsonify({"ya_reproduciendo": False, "cancion": "No autorizado"}), 200

        sp = Spotify(auth=token_info["access_token"])
        current = sp.current_playback()
        if current and current.get("is_playing"):
            cancion = current["item"]["name"]
            return jsonify({"ya_reproduciendo": True, "cancion": cancion}), 200
        else:
            return jsonify({"ya_reproduciendo": False, "cancion": "Pausado"}), 200

    except Exception as e:
        return jsonify({"ya_reproduciendo": False, "cancion": str(e)}), 200
