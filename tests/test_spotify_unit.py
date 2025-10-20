# tests/test_spotify_unit.py
import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_folder.spotify_routes import spotify_bp

@pytest.fixture
def app():
    """Create a minimal Flask app for isolated unit tests."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test"
    app.register_blueprint(spotify_bp)
    yield app

@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()

def test_login_redirect_url(client):
    """Ensure /login redirects to Spotify's auth page."""
    response = client.get("/login")
    assert response.status_code in (302, 307)
    assert "spotify.com" in response.location.lower()

def test_callback_handles_missing_code(client):
    """If callback called without a code, should flash or show error."""
    response = client.get("/callback")
    # Expect redirect or error message
    assert response.status_code in (302, 400)
    # Defensive: handle whichever behavior your app uses
    assert b"error" in response.data.lower() or response.status_code == 302
