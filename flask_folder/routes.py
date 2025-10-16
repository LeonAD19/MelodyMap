import sys 
sys.dont_write_bytecode = True
from flask import render_template, Blueprint

# Create a blueprint for routes
routes = Blueprint('routes', __name__)
spotify_api = Blueprint('spotify_api', __name__, url_prefix='/spotify')

@routes.route('/' )
def home():
    from .spotify_api import is_logged_in
    user_auth = is_logged_in()

    return render_template("home.html", user_auth=user_auth)

# Map page
@routes.route('/map')
def map_page():
    return render_template('map.html')

@spotify_api.route('/now_playing')
def now_playing():
    from .spotify_api import now_playing
    return now_playing()

# Purpose: Render the currently playing song
@spotify_api.route('/render_now_playing')
def render_now_playing():
    return render_template('render_now_playing.html')