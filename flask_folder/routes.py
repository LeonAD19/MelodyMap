import os

import re #regular expressions module
from markupsafe import escape #protects projects against injection attacks
#from flask_folder import app
import sys 
sys.dont_write_bytecode = True
from flask import render_template, request, Flask,Blueprint


# Create a blueprint for routes
routes = Blueprint('routes', __name__)

@routes.route('/' )
def home():
    from .spotify_api import is_logged_in
    user_auth = is_logged_in()

    return render_template("home.html", user_auth=user_auth)

# Map page
@routes.route('/map')
def map_page():
    return render_template('map.html')
