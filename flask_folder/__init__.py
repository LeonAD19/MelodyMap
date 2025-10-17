import sys
import os
sys.dont_write_bytecode = True # Prevents creation of .pyc cache files

from dotenv import load_dotenv
from flask import Flask

### Application Factory ###
def create_app():
    load_dotenv()   # Load .env variables into environment

    app = Flask(__name__)
    app.config['SECRET_KEY']= os.getenv("FLASK_SECRET_KEY") # Set Flask secret key

    # Import and register route blueprints
    from .routes import routes, spotify_api
    app.register_blueprint(routes)
    app.register_blueprint(spotify_api)

    # Register the Spotify OAuth blueprint
    from .spotify_routes import spotify_bp
    app.register_blueprint(spotify_bp)

    return app