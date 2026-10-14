from flask import Flask, redirect, request, render_template, session
from auth import sp_oauth, set_token_info, get_token_info
from bpm_handler import bpm_blueprint  # O como lo tengas importado
from spotipy import Spotify
import os

app = Flask(__name__)
# Necesario para guardar la sesión del usuario de forma segura
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "clave_secreta_super_segura")

app.register_blueprint(bpm_blueprint)

# ----- Rutas básicas -----
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code, as_dict=True)
    
    # Guardamos en la sesión de Flask para que no se pierda
    session['token_info'] = token_info
    set_token_info(token_info)

    sp = Spotify(auth=token_info['access_token'])
    user_profile = sp.current_user()
    user_id = user_profile.get("id", "desconocido")

    return render_template("dashboard.html", user_id=user_id)

@app.route("/estado_musica")
def estado_musica():
    # Endpoint útil para verificar si hay sesión activa
    token_info = session.get('token_info', get_token_info())
    if not token_info:
        return {"reproduciendo": False, "cancion": "No autorizado"}
    
    try:
        sp = Spotify(auth=token_info['access_token'])
        current = sp.current_playback()
        if current and current.get('is_playing'):
            track_name = current['item']['name']
            return {"reproduciendo": True, "cancion": track_name}
    except Exception as e:
        print("Error obteniendo estado:", e)
        
    return {"reproduciendo": False, "cancion": "Pausado o sin dispositivo"}

# ----- Ejecutar la app -----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
