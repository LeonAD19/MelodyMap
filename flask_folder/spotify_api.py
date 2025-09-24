import os
import requests
import time
from flask import Blueprint, session, jsonify
from .spotify_tokens import set_tokens, clear_tokens

# ==== SPOTIFY DASHBOARD LINK ====
# The redirect will almost definetly need to be changed
# https://developer.spotify.com/dashboard/8fe0b36abc4744aca36f7c9bca17ef74

bp = Blueprint('spotify_api', __name__, url_prefix='/spotify')

# =========================
# CONFIG (used by all parts)
# =========================

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')  # must match Spotify Dashboard
SCOPES = os.getenv('SPOTIFY_SCOPES', '').split()

TOKEN_URL = 'https://accounts.spotify.com/api/token'
    
# =========================
# API CALL (business logic)
# =========================
# Purpose: Use the access token to call /v1/me/player/currently-playing,
@bp.route('/now_playing')
def now_playing():
    token = ensure_access_token()
    if not token:
        return jsonify({'authorized': False, 'playing': None})
    
    r = requests.get(
        'https://api.spotify.com/v1/me/player/currently-playing', 
        headers = {'Authorization': f'Bearer {token}'}
    )

    # print('\nCurrently Playing status:', r.status_code)
    if r.status_code == 204:
        return jsonify({'authorized': True, 'playing': None})
    if r.status_code in (401, 403):
        clear_tokens()
        return jsonify({"authorized": False, "playing": None}), r.status_code
    if r.status_code != 200:
        return jsonify({'authorized': True, 'error': r.text}), r.status_code

    payload = r.json()
    # print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))

    # Safe field access to avoid KeyErrors if fields are missing
    item = (payload.get('item') or {})
    name = item.get('name') or 'Unknown'
    album = item.get('album') or {}
    album_name = album.get('name') or 'Unknown'
    album_images = album.get('images') or []
    album_art = album_images[0].get('url') if album_images else None    # get url from images
    artists_list = item.get('artists') or []
    artists = ', '.join(a.get('name', '') for a in artists_list) or 'Unknown'

    # print(f'\nNow playing: {name} ({album_name}) — {artists}')
    # print(f'Link to art: {album_art}')
    
    return jsonify({
        'authorized': True,
        'playing': {
            'name': name,
            'album': album_name,
            'artists': artists,
            'art': album_art,
            'is_playing': payload.get('is_playing', False),
            'progress_ms': payload.get('progress_ms'),
            'duration_ms': item.get('duration_ms'),
        }
    })

# Return a valid access token
# Should refresh if needed
def ensure_access_token() -> str | None:
    access = session.get('spotify_access_token')
    exp_at = session.get('spotify_expires_at', 0)
    
    if access and time.time() < exp_at:
        return access       # Early exit if the token is still good.

    refresh = session.get('spotify_refresh_token') or os.getenv("SPOTIFY_REFRESH_TOKEN")        # the os.getenv will go away once auth is implemented
    if not refresh:
        return None         # Give up if there is no spotify_refresh_token

    r = requests.post(
        TOKEN_URL, 
        data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh,
                'client_id': CLIENT_ID,
            }, 
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    if r.status_code != 200:
        clear_tokens()
        return None
    
    set_tokens(r.json())
    return session.get('spotify_access_token')