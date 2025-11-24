# flask_folder/tests/test_spotify_tokens.py

import pytest
import time
from flask import Flask, session
from unittest.mock import Mock, patch


@pytest.fixture
def app(monkeypatch):
    """
    Minimal Flask app for testing token management.
    Env vars are set BEFORE importing the spotify module so it reads proper values.
    """
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_client_id")

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test_secret"
    app.config["TESTING"] = True

    return app


# ============================================================
# TESTS FOR set_tokens()
# ============================================================

def test_set_tokens_stores_tokens_in_session(app):
    """set_tokens() should store access/refresh tokens and calculate expiry."""
    with app.test_request_context():
        from flask_folder.spotify.spotify_tokens import set_tokens

        current_time = time.time()
        tokens = {
            'access_token': 'test_access',
            'refresh_token': 'test_refresh',
            'expires_in': 3600
        }

        with patch('flask_folder.spotify.spotify_tokens.time.time', return_value=current_time):
            set_tokens(tokens)

        assert session['spotify_access_token'] == 'test_access'
        assert session['spotify_refresh_token'] == 'test_refresh'
        assert session['spotify_expires_at'] == int(current_time) + 3600 - 30
        assert 'uuid' in session


def test_set_tokens_preserves_refresh_token_when_missing(app):
    """set_tokens() should NOT overwrite refresh_token if new response doesn't include it."""
    with app.test_request_context():
        from flask_folder.spotify.spotify_tokens import set_tokens

        # Initial tokens with refresh
        set_tokens({
            'access_token': 'access_1',
            'refresh_token': 'refresh_original',
            'expires_in': 3600
        })

        # Refresh response without refresh token
        set_tokens({
            'access_token': 'access_2',
            'expires_in': 3600
        })

        assert session['spotify_refresh_token'] == 'refresh_original'
        assert session['spotify_access_token'] == 'access_2'


# ============================================================
# TESTS FOR clear_tokens()
# ============================================================

def test_clear_tokens_removes_all_spotify_keys(app):
    """clear_tokens() should remove all spotify_* keys and uuid from session."""
    with app.test_request_context():
        from flask_folder.spotify.spotify_tokens import set_tokens, clear_tokens

        set_tokens({
            'access_token': 'test_access',
            'refresh_token': 'test_refresh',
            'expires_in': 3600
        })

        # Add non-Spotify session data
        session['user_preference'] = 'dark_mode'

        clear_tokens()

        assert 'spotify_access_token' not in session
        assert 'spotify_refresh_token' not in session
        assert 'spotify_expires_at' not in session
        assert 'uuid' not in session
        assert session['user_preference'] == 'dark_mode'


# ============================================================
# TESTS FOR get_access_token()
# ============================================================

def test_get_access_token_returns_valid_token(app):
    """get_access_token() should return the access token if not expired."""
    with app.test_request_context():
        from flask_folder.spotify.spotify_tokens import set_tokens, get_access_token

        current_time = time.time()

        with patch('flask_folder.spotify.spotify_tokens.time.time', return_value=current_time):
            set_tokens({
                'access_token': 'valid_token',
                'refresh_token': 'refresh_token',
                'expires_in': 3600
            })

        # Token still valid
        with patch('flask_folder.spotify.spotify_tokens.time.time', return_value=current_time + 100):
            result = get_access_token()

        assert result == 'valid_token'


def test_get_access_token_returns_none_when_no_tokens(app):
    """get_access_token() should return None if no tokens in session."""
    with app.test_request_context():
        from flask_folder.spotify.spotify_tokens import get_access_token

        result = get_access_token()
        assert result is None


def test_get_access_token_refreshes_expired_token(app):
    """get_access_token() should refresh the token if expired."""
    with app.test_request_context():
        from flask_folder.spotify.spotify_tokens import set_tokens, get_access_token

        current_time = time.time()

        with patch('flask_folder.spotify.spotify_tokens.time.time', return_value=current_time):
            set_tokens({
                'access_token': 'old_token',
                'refresh_token': 'refresh_123',
                'expires_in': 3600
            })

        # Mock successful refresh
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'new_token',
            'expires_in': 3600
        }

        # Token expired
        future_time = current_time + 4000

        with patch('flask_folder.spotify.spotify_tokens.time.time', return_value=future_time):
            with patch('flask_folder.spotify.spotify_tokens.refresh_client_token', return_value=mock_response):
                result = get_access_token()

        assert result == 'new_token'
        assert session['spotify_access_token'] == 'new_token'
        assert session['spotify_refresh_token'] == 'refresh_123'


def test_get_access_token_clears_tokens_on_refresh_failure(app):
    """get_access_token() should clear all tokens if refresh fails."""
    with app.test_request_context():
        from flask_folder.spotify.spotify_tokens import set_tokens, get_access_token

        current_time = time.time()

        with patch('flask_folder.spotify.spotify_tokens.time.time', return_value=current_time):
            set_tokens({
                'access_token': 'old_token',
                'refresh_token': 'refresh_123',
                'expires_in': 3600
            })

        # Mock failed refresh
        mock_response = Mock()
        mock_response.status_code = 401

        future_time = current_time + 4000

        with patch('flask_folder.spotify.spotify_tokens.time.time', return_value=future_time):
            with patch('flask_folder.spotify.spotify_tokens.refresh_client_token', return_value=mock_response):
                result = get_access_token()

        assert result is None
        assert 'spotify_access_token' not in session
        assert 'spotify_refresh_token' not in session


# ============================================================
# TESTS FOR refresh_client_token()
# ============================================================

def test_refresh_client_token_sends_correct_request(app, monkeypatch):
    """refresh_client_token() should send POST request with correct parameters."""
    with app.test_request_context():
        from flask_folder.spotify.spotify_tokens import refresh_client_token

        captured_args = {}

        def mock_post(url, data=None, headers=None):
            captured_args['url'] = url
            captured_args['data'] = data
            captured_args['headers'] = headers

            mock_resp = Mock()
            mock_resp.status_code = 200
            return mock_resp

        monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_client_123")

        with patch('flask_folder.spotify.spotify_tokens.requests.post', side_effect=mock_post):
            refresh_client_token('test_refresh_token')

        assert captured_args['url'] == "https://accounts.spotify.com/api/token"
        assert captured_args['data']['grant_type'] == 'refresh_token'
        assert captured_args['data']['refresh_token'] == 'test_refresh_token'
        assert captured_args['data']['client_id'] == 'test_client_123'
        assert captured_args['headers']['Content-Type'] == 'application/x-www-form-urlencoded'
