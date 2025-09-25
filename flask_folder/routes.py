import os
import requests
from flask import render_template, request, Flask, Blueprint, redirect, session, url_for, flash
from dotenv import load_dotenv

import re #regular expressions module
from markupsafe import escape #protects projects against injection attacks
#from flask_folder import app
import sys 
sys.dont_write_bytecode = True

# Load .env file
load_dotenv()

# Create a blueprint for routes
routes = Blueprint('routes', __name__)

# Spotify OAuth Configurations
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize" # Spotify login URL
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token" # Spotify token URL

# Load environment variables
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')        # Spotify App Client ID
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')# Spotify App Client Secret
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')  # URL Spotify redirects to after login
SCOPE = "user-read-currently-playing"             # Permission to read user's currently playing track

# Routes to Home
routes.route('/' )
def home():
    return render_template("home.html")

@routes.route('/login')
# Spotify login route
def login():
    # Starts the Spotify OAuth flow. Redirects user to Spotify's authorization URL.
    auth_query = {
        "response_type": "code", # Request authorization code
        "client_id": CLIENT_ID,
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI,
        
    }

    # Building query starting with URL encoding
    url_args = "&".join([f"{key}={requests.utils.quote(val)}" for key, val in auth_query.items()])
    auth_url = f"{SPOTIFY_AUTH_URL}?{url_args}"

    # Redirect user to Spotify's authorization URL
    return redirect(auth_url)

# Spotify OAuth callback route
@routes.route('/callback')
def callback():

    # Handles the redirect from Spotify after user login
    code = request.args.get("code")
    error = request.args.get("error")

    # Handle error if user denied access or any other error occurred
    if error:
        flash("Login Failed. Please try again.")
        return redirect(url_for('routes.home'))
    
    # Prepare data to request access token
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    # Request access token from Spotify
    response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
    if response.status_code != 200:
        flash("Failed to get token. Please try again.")
        return redirect(url_for('routes.home'))
    
    # Store access token in session
    token_info = response.json()
    session['access_token'] = token_info['access_token']

    # Successful login
    flash("Login successful!")
    return redirect(url_for('routes.home'))