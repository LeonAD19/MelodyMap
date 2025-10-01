import os
import requests
from flask import request, Blueprint, redirect, url_for, flash
from dotenv import load_dotenv
import sys
sys.dont_write_bytecode = True

load_dotenv()

# Blueprint for your OAuth login
spotify_bp = Blueprint('spotify_bp', __name__)

# Spotify OAuth Config
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SCOPE = "user-read-currently-playing"

@spotify_bp.route('/login')
def login():
    auth_query = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI,
        "show_dialog": "true"
    }

    url_args = "&".join([f"{key}={requests.utils.quote(val)}" for key, val in auth_query.items()])
    auth_url = f"{SPOTIFY_AUTH_URL}?{url_args}"
    return redirect(auth_url)

@spotify_bp.route('/callback')
def callback():
    code = request.args.get("code")
    error = request.args.get("error")

    if error:
        flash("Login Failed. Please try again.")
        return redirect(url_for('routes.home'))

    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
    if response.status_code != 200:
        flash("spotifylogo.png", "success")
        return redirect(url_for('routes.home'))

    from .spotify_tokens import set_tokens

    token_info = response.json()
    set_tokens(token_info)

    flash("Login successful!", "success")
    return redirect(url_for('routes.home'))
    
def refresh_client_token(token):
    return requests.post(
        SPOTIFY_TOKEN_URL, 
        data = {
                'grant_type': 'refresh_token',
                'refresh_token': token,
                'client_id': CLIENT_ID,
            }, 
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    )