import sys
import os
sys.dont_write_bytecode = True

from dotenv import load_dotenv
from flask import Flask

### Application Factory ###
def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config['SECRET_KEY']= os.getenv("FLASK_SECRET_KEY")

    from .routes import routes
    app.register_blueprint(routes, url_prefix = '/')
    
    from .spotify_api import bp as spotify_api
    app.register_blueprint(spotify_api)
    
    from .spotify_auth import bp as spotify_auth
    app.register_blueprint(spotify_auth)
    
    return app