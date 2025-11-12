#Below is the code for the unit tests
#Test will be more efficient and ready to use once we make sure our DB is up
#For now, this test is a draft, final draft in Sprint 3, this is focusing on the login flow for now
#Test code will not interfere with actual code to use application

# flask_folder/tests/test_spotify_unit.py

import pytest
from flask import Flask, Blueprint
from flask.testing import FlaskClient

@pytest.fixture
def app(monkeypatch):
    """
    Minimal Flask app that registers:
      - a 'routes' blueprint with endpoint 'routes.home' (needed by spotify callback redirects)
      - the real Spotify OAuth blueprint (unit target)

    Env vars are set BEFORE importing the spotify module so it reads proper values.
    """
    # Set env for spotify_routes BEFORE import
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("SPOTIFY_REDIRECT_URI", "http://localhost/callback")

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test"

    # Minimal 'routes' blueprint so url_for('routes.home') resolves during tests
    routes = Blueprint("routes", __name__)
    @routes.route("/")
    def home():
        return "home ok"
    app.register_blueprint(routes)

    # Import and register the real Spotify OAuth blueprint from the subpackage
    from flask_folder.spotify.spotify_routes import spotify_bp
    app.register_blueprint(spotify_bp)

    return app

@pytest.fixture
def client(app) -> FlaskClient:
    return app.test_client()

def test_login_redirects_to_spotify(client):
    """GET /login should redirect to Spotify's authorize URL."""
    resp = client.get("/login")
    assert resp.status_code in (302, 307)
    assert "accounts.spotify.com" in (resp.location or "").lower()

def test_callback_with_error_redirects(client):
    """Callback with ?error=... should redirect safely (no token exchange)."""
    resp = client.get("/callback?error=access_denied")
    assert resp.status_code in (302, 307)

def test_callback_with_code_mocks_token_exchange(client, monkeypatch):
    """Mock requests.post so no real network call is made; ensure flow completes."""
    class FakeResp:
        status_code = 200
        def json(self):
            return {
                "access_token": "fake_access",
                "refresh_token": "fake_refresh",
                "expires_in": 3600
            }

    # Patch requests.post inside the spotify_routes module
    import flask_folder.spotify.spotify_routes as sr
    monkeypatch.setattr(sr.requests, "post", lambda url, data=None, headers=None: FakeResp())

    resp = client.get("/callback?code=fakecode123")
    # Depending on implementation, callback may return a success page or a redirect
    assert resp.status_code in (200, 302, 307)
