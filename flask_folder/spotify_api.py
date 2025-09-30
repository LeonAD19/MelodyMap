import requests
from flask import Blueprint, render_template, jsonify
from .spotify_tokens import clear_tokens, get_access_token

# ==== SPOTIFY DASHBOARD LINK ====
# The redirect will almost definetly need to be changed
# https://developer.spotify.com/dashboard/8fe0b36abc4744aca36f7c9bca17ef74

bp = Blueprint('spotify_api', __name__, url_prefix='/spotify')

# =========================
# CONFIG (used by all parts)
# =========================
    
# =========================
# API CALL (business logic)
# =========================
# Purpose: Use the access token to call /v1/me/player/currently-playing,
@bp.route('/now_playing')
def now_playing():
    token = get_access_token()
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

# =========================
# API CALL (business logic)
# =========================
# Purpose: Render the currently playing song
@bp.route('/render_now_playing')
def render_now_playing():
    return render_template('render_now_playing.html')
