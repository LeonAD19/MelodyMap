#Below is the code for the unit tests
#Test will be more efficient and ready to use once we make sure our DB is up
#For now, this test is a draft, final draft in Sprint 3, this is focusing on the login flow for now
#Test code will not interfere with actual code to use application

# flask_folder/tests/test_spotify_unit.py  (replace the app() fixture only)

import pytest
from flask import Flask, Blueprint
from flask.testing import FlaskClient

@pytest.fixture
def app(monkeypatch):
    """
    Minimal Flask app that registers:
      - a 'routes' blueprint with endpoint 'routes.home' (needed for redirects)
      - the real Spotify OAuth blueprint (unit target)
    """
    # Set env BEFORE importing the spotify blueprint
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("SPOTIFY_REDIRECT_URI", "http://localhost/callback")

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test"

    # ✅ Minimal 'routes' blueprint to satisfy url_for('routes.home')
    routes = Blueprint("routes", __name__)
    @routes.route("/")
    def home():
        return "home ok"
    app.register_blueprint(routes)

    # Now import/register the Spotify OAuth blueprint
    from flask_folder.spotify_routes import spotify_bp
    app.register_blueprint(spotify_bp)

    return app

@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()
