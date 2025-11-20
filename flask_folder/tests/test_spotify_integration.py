#Below is the code for the integration tests
#Test will be more efficient and ready to use once we make sure our DB is up
#For now, this test is a draft, final draft in Sprint 3, this is focusing on the login flow for now
#Test code will not interfere with actual code to use application

import pytest

@pytest.fixture
def app(monkeypatch):
    """
    Use the real app factory so all blueprints are registered.
    Set env BEFORE importing create_app so spotify modules read proper values.
    """
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_client_secret")
    monkeypatch.setenv("SPOTIFY_REDIRECT_URI", "http://localhost/callback")
    monkeypatch.setenv("FLASK_SECRET_KEY", "test-secret")

    from flask_folder import create_app
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_spotify_login_redirect(client):
    """Full app: /login should redirect to Spotify authorize URL."""
    resp = client.get("/login")
    assert resp.status_code in (302, 307)
    assert "accounts.spotify.com" in (resp.location or "").lower()

def test_spotify_callback_flow_mocked(client, monkeypatch):
    """Mock Spotify token exchange end-to-end in the full app context."""
    class FakeResp:
        status_code = 200
        def json(self):
            return {
                "access_token": "fake_access",
                "refresh_token": "fake_refresh",
                "expires_in": 3600
            }

    import flask_folder.spotify.spotify_routes as sr
    monkeypatch.setattr(sr.requests, "post", lambda url, data=None, headers=None: FakeResp())

    resp = client.get("/callback?code=abc123")
    assert resp.status_code in (200, 302, 307)

# ---------------- MM-85 INTEGRATION TESTS  ----------------

def test_home_route_exists(client):
    """
    Sanity: GET / should be handled by your app (routes.home).
    We don't assert content, only that it's reachable.
    """
    resp = client.get("/")
    assert resp.status_code == 200

def test_render_now_playing_template_route(client):
    """
    /spotify/render_now_playing should return 200 (template render).
    """
    resp = client.get("/spotify/render_now_playing")
    assert resp.status_code == 200

def test_now_playing_calls_api_with_coords(client, monkeypatch):
    """
    /spotify/now_playing should pass lat/lng query params through to spotify_api.now_playing
    without actually calling Spotify.
    """
    import flask_folder.spotify.spotify_api as api

    seen = {}

    def fake_now_playing(lat, lng):
        # Assert types and capture values
        assert isinstance(lat, float)
        assert isinstance(lng, float)
        seen["lat"] = lat
        seen["lng"] = lng
        # Flask view functions can return (dict, status)
        return {"ok": True, "lat": lat, "lng": lng}, 200

    monkeypatch.setattr(api, "now_playing", fake_now_playing)

    resp = client.get("/spotify/now_playing?lat=29.88&lng=-97.94")
    assert resp.status_code == 200
    assert seen == {"lat": 29.88, "lng": -97.94}

def test_profile_route_calls_get_profile(client, monkeypatch):
    """
    /spotify/profile should delegate to spotify_api.get_profile
    """
    import flask_folder.spotify.spotify_api as api

    def fake_get_profile():
        return {"display_name": "Test User", "images": []}, 200

    monkeypatch.setattr(api, "get_profile", fake_get_profile)

    resp = client.get("/spotify/profile")
    assert resp.status_code == 200
