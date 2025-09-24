import time
from flask import session

# Save access/refresh/expiry to session. Only overwrite refresh if provided.
def set_tokens(tokens: dict) -> None:
    session['spotify_access_token'] = tokens.get('access_token')

    # refresh_token is often missing on refresh responses; don't erase the old one
    if tokens.get('refresh_token'):
        session['spotify_refresh_token'] = tokens['refresh_token']

    expires_in = int(tokens.get('expires_in', 3600))
    session['spotify_expires_at'] = int(time.time()) + expires_in - 30  # safety margin

# Remove all spotify_* keys from session.
def clear_tokens() -> None:
    for k in list(session.keys()):
        if k.startswith('spotify_'):
            session.pop(k)
