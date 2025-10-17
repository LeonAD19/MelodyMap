import os
import requests
from flask import request, Blueprint, redirect, url_for, flash
from dotenv import load_dotenv
import sys
sys.dont_write_bytecode = True

# Loads environment variables from .env file
load_dotenv()

# Blueprint for your OAuth login
spotify_bp = Blueprint('spotify_bp', __name__)

# Spotify OAuth Config
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

# Load sensitive credentials from .env
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SCOPE = "user-read-currently-playing"

# === LOGIN ROUTE ===
@spotify_bp.route('/login')
def login():
    # Redirect user to Spotify's authorization page
    auth_query = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI,
        "show_dialog": "true" # Always show Spotify login prompt
    }

    # Join parameters into a single URL string (properly encoded)
    url_args = "&".join([f"{key}={requests.utils.quote(val)}" for key, val in auth_query.items()])
    auth_url = f"{SPOTIFY_AUTH_URL}?{url_args}"

    # Redirect the user to Spotify’s authorization page
    return redirect(auth_url)

# Callback route that Spotify redirects to after login
@spotify_bp.route('/callback')
def callback():
    # Get authorization code or error returned from Spotify
    code = request.args.get("code")
    error = request.args.get("error")

    # If Spotify returned an error, notify user and redirect home
    if error:
        flash("Login Failed. Please try again.")
        return redirect(url_for('routes.home'))

    # Exchange code for access token from spotify
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    # Send POST request to Spotify API to exchange code for access token
    response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
    
    # If Spotify didn't return a successful response
    if response.status_code != 200:
        flash("Login Failed. Please try again.")
        return redirect(url_for('routes.home'))

    # Save tokens in session
    from .spotify_tokens import set_tokens

    # Parse token info from Spotify
    token_info = response.json()
    set_tokens(token_info)

    # Notify user that login succeeded
    flash("Login successful!", "success")
    return redirect(url_for('routes.home'))
    