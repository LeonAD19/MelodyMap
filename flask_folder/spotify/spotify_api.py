import requests
from flask import jsonify, session, url_for
from .spotify_tokens import clear_tokens, get_access_token
from .spotify_errors import SPOTIFY_ERROR_MESSAGES

# Get the logged-in user's Spotify profile
def get_profile():
    # Get access token; if none, user not logged in
    token = get_access_token()
    if not token:
        return jsonify({"error": "Not logged in"}), 401

    # Call Spotify API to get user profile
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get("https://api.spotify.com/v1/me", headers=headers, timeout=10)

    # If Spotify says its bad, clear local tokens and force re-login
    if r.status_code in (401, 403):
        clear_tokens()
        return jsonify({"error": SPOTIFY_ERROR_MESSAGES.get(r.status_code, "Auth error")}), 401
    
    # If any other error, return it as closed
    if r.status_code != 200:
        return jsonify({"error": "Spotify unavailable"}), 503

    # Build profile response, stable payload for the header UI
    data = r.json() or {}
    username = data.get("display_name") or data.get("id") or "Spotify User"
    images = data.get("images", []) or []
    profile_pic = images[0].get("url") if images else url_for('static', filename='img/default-avatar.png')

    # Disable caching for profile response so stale profile isnt used
    resp = jsonify({"username": username, "profile_pic": profile_pic})
    resp.headers["Cache-Control"] = "no-store"
    return resp, 200

# Purpose: 
# Returns details of currently playing song for authenticated Spotify User
def now_playing(lat: float, lng: float):
    token = get_access_token()
    headers = {'Authorization': f'Bearer {token}'}
    url = 'https://api.spotify.com/v1/me/player/currently-playing'
    
    # Call Spotify API and store response
    response = requests.get(
        url, 
        headers=headers
    )

    # Handle if Spotify didnt send back a "200 OK" (meaning something went wrong):
    if response.status_code != 200:
        
        if response.status_code in (401, 403):  # Authentication Error
            clear_tokens()      # Have users send back in
            
        if response.status_code == 204:     # Not playing anything
            return jsonify({
                "authorized": True,
                "error": SPOTIFY_ERROR_MESSAGES.get(204)
            }), 200     # This makes the json show 
            
        return jsonify({
            "authorized": response.status_code not in (401, 403),
            "error": SPOTIFY_ERROR_MESSAGES.get(response.status_code, "Unknown error.")
        }), response.status_code
         
         
    # Extract song details safely        
    payload = response.json() or {}
    item = payload.get('item', {})
    
    album = item.get('album', {})
    album_images = album.get('images', None)
    artists = ', '.join(a.get('name', '') for a in item.get('artists', [])) or 'Unknown'
    
    from .spotify_dao import send_song_info
    send_song_info(session['uuid'], item.get('name'), lat=lat, lng=lng)

    # Return song details
    return jsonify({
        "authorized": True,
        "playing": {
            "name": item.get('name', 'Unknown'),
            "album": album.get('name', 'Unknown'),
            "artists": artists,
            "art": album_images[0].get('url') if album_images else None,
            "is_playing": payload.get('is_playing', False),
            "progress_ms": payload.get('progress_ms'),
            "duration_ms": item.get('duration_ms'),
        }
    })
    
# Purpose: Return if Authenticated Spotify User is logged in
def is_logged_in() -> True | False:
    token = get_access_token()
    if not token:       # If no token, then cannot be logged in
        return False

    # Call Spotify API and store response
    r = requests.get(
        "https://api.spotify.com/v1/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    if r.status_code == 200:        # If Spotify sends back a "200 OK" then logged in
        return True
    
    if r.status_code in (401, 403):     # If bad token, then clear it
        clear_tokens()
    
    return False

