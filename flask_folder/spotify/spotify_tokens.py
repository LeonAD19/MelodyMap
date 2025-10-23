import os
import time
import uuid
from flask import session
import requests

# Save access/refresh/expiry to session. Only overwrite refresh if provided.
def set_tokens(tokens: dict) -> None:
    session['spotify_access_token'] = tokens.get('access_token')

    # refresh_token is often missing on refresh responses; don't erase the old one
    if tokens.get('refresh_token'):
        session['spotify_refresh_token'] = tokens['refresh_token']

    # Calculate token expiration time (subtract 30 sec for safety)
    expires_in = int(tokens.get('expires_in', 3600))
    session['spotify_expires_at'] = int(time.time()) + expires_in - 30  # safety margin
    session['uuid'] = str(uuid.uuid4())

# Remove all spotify_* keys from session.
def clear_tokens() -> None:
    for k in list(session.keys()):
        if k.startswith('spotify_'):
            session.pop(k)
    session.pop('uuid', None)

# Return a valid access token
# Should refresh if needed
def get_access_token() -> str | None:
    access = session.get('spotify_access_token')
    exp_at = session.get('spotify_expires_at', 0)
    
    if access and time.time() < exp_at:
        return access       # Early exit if the token is still good.

    refresh = session.get('spotify_refresh_token')
    if not refresh:
        return None         # Give up if there is no spotify_refresh_token
    
    # Try refreshing the token using Spotify API
    r = refresh_client_token(token=refresh)
    
    if r.status_code != 200:
        clear_tokens()      # Reset session if refresh fails
        return None
    
    # Save new tokens and return the new access token
    set_tokens(r.json())
    return session.get('spotify_access_token')

# Purpose: If User's token expired, then refresh. This prevents the need to re-login.
def refresh_client_token(token):
    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
    CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    
    # Send request to refresh the token
    return requests.post(
        SPOTIFY_TOKEN_URL, 
        data = {
                'grant_type': 'refresh_token',
                'refresh_token': token,
                'client_id': CLIENT_ID,
            }, 
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    )
