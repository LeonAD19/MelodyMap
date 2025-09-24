import base64
import hashlib
import os
import secrets
import urllib.parse
import requests
from flask import Blueprint, session, request, redirect, url_for
from .spotify_tokens import set_tokens


bp = Blueprint('spotify_auth', __name__, url_prefix='/spotify')


CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
AUTH_URL  = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:5000/spotify/callback')
SCOPES = os.getenv('SPOTIFY_SCOPES', '').split()


# =========================
# SPOTIFY AUTH (PKCE utils)
# =========================
# Purpose: Create PKCE code_verifier and code_challenge used in OAuth.
def _b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode('ascii')

def create_pkce_pair():
    code_verifier = _b64url(os.urandom(64))
    code_challenge = _b64url(hashlib.sha256(code_verifier.encode('ascii')).digest())
    return code_verifier, code_challenge


# =========================
# LOGIN ROUTE
# =========================
# Purpose: Redirect for user to login/consent for us to do 
@bp.route('/login')
def login():
    # PKCE + CSRF state
    code_verifier, code_challenge = create_pkce_pair()
    state = secrets.token_urlsafe(16)

    # stash for callback
    session['spotify_code_verifier'] = code_verifier
    session['spotify_state'] = state
    
    # Build /authorize URL and open the browser
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'code_challenge_method': 'S256',
        'code_challenge': code_challenge,
        'state': state,
        'scope': ' '.join(SCOPES),
        'show_dialog': 'true',
    }
    auth_url = AUTH_URL + '?' + urllib.parse.urlencode(params)    
    # print('\nAuthorize URL (copy/paste if needed):')
    # print(auth_url, '\n')
    # print('Opening browser for Spotify login...')
    return redirect(auth_url)



@bp.route('/callback')
def callback():
    err = request.args.get('error')
    if err:
        return f'Spotify auth error: {err}', 400

    code = request.args.get('code')
    state = request.args.get('state')
    if not code or not state:
        return 'Missing code/state', 400
    if state != session.get('spotify_state'):
        return 'State mismatch', 400

    # Exchange authorization code for access token (OAuth token endpoint)
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'code_verifier': session.get('spotify_code_verifier'),
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    token_resp = requests.post(TOKEN_URL, data=data, headers=headers)
    
    if token_resp.status_code != 200:
        return f'Token exchange failed: {token_resp.text}', 400

    set_tokens(token_resp.json())
    
    # cleanup
    session.pop('spotify_code_verifier', None)
    session.pop('spotify_state', None)
    
    # land on a whats playing page
    return redirect(url_for('spotify_api.now_playing'))