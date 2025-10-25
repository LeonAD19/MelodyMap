import sys
sys.dont_write_bytecode = True
from flask import render_template, Blueprint, request,jsonify

# Create a blueprint for routes
routes = Blueprint('routes', __name__)
spotify_api = Blueprint('spotify_api', __name__, url_prefix='/spotify')

@routes.route('/' )
def home():
    from .spotify.spotify_api import is_logged_in
    user_auth = is_logged_in()

    return render_template("home.html", user_auth=user_auth)

# Map page
@routes.route('/map')
def map_page():
    return render_template('map.html')

@spotify_api.route('/now_playing')
def now_playing():
    from .spotify.spotify_api import now_playing
    
    # Get coordinates from query parameters (sent from frontend)
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    
    return now_playing(lat, lng)

# Purpose: Render the currently playing song
@spotify_api.route('/render_now_playing')
def render_now_playing():
    return render_template('render_now_playing.html')

# Returns the logged-in user's profile (display name + avatar)
@spotify_api.route('/profile')
def profile_route():
    from .spotify.spotify_api import get_profile
    return get_profile()

# Define a route for the Spotify API that listens at '/spotify/songs'
@spotify_api.route('/songs')
def get_songs():
    from .spotify.spotify_dao import get_songs_from_db
    songs = get_songs_from_db()
    return jsonify(songs)

