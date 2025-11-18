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

# ------------------ MM-80 UNIT TESTS  ------------------
from urllib.parse import urlparse, parse_qs

def test_login_builds_correct_query_params(client):
    """
    /login should redirect to Spotify with the expected query parameters.
    """
    resp = client.get("/login")
    assert resp.status_code in (302, 307)
    loc = resp.location or ""
    parsed = urlparse(loc)
    assert parsed.netloc.endswith("accounts.spotify.com")
    assert parsed.path.strip("/") == "authorize"

    qs = parse_qs(parsed.query)
    # response_type=code
    assert qs.get("response_type", [""])[0] == "code"
    # client_id present (value is from env, we only assert it's non-empty)
    assert qs.get("client_id", [""])[0] != ""
    # redirect_uri present
    assert qs.get("redirect_uri", [""])[0] != ""
    # scope contains user-read-currently-playing
    assert "user-read-currently-playing" in qs.get("scope", [""])[0]

def test_callback_error_sets_flash_and_redirects(client):
    """
    If Spotify returns ?error=..., the route should flash and redirect.
    We can't see the flash text without a template, but we can assert session has flashes.
    """
    resp = client.get("/callback?error=access_denied")
    assert resp.status_code in (302, 307)

    # Confirm a flash was queued in session
    with client.session_transaction() as sess:
        # Flask stores flashes under '_flashes' list of (category, message)
        assert "_flashes" in sess
        assert len(sess["_flashes"]) >= 1

def test_callback_token_exchange_failure_redirects_and_flashes(client, monkeypatch):
    """
    If Spotify token exchange fails (non-200), route should flash and redirect home.
    """
    import flask_folder.spotify.spotify_routes as sr

    class BadResp:
        status_code = 400
        def json(self):
            return {"error": "bad_request"}

    monkeypatch.setattr(sr.requests, "post", lambda *a, **k: BadResp())

    resp = client.get("/callback?code=fakecode123")
    assert resp.status_code in (302, 307)

    with client.session_transaction() as sess:
        assert "_flashes" in sess
        assert len(sess["_flashes"]) >= 1

