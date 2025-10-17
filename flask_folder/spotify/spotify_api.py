import requests
from flask import jsonify
<<<<<<<< HEAD:flask_folder/spotify/spotify_api.py
from .spotify_tokens import clear_tokens, get_access_token
from .spotify_errors import SPOTIFY_ERROR_MESSAGES
========
from .spotify.spotify_tokens import clear_tokens, get_access_token

SPOTIFY_ERROR_MESSAGES = {
    204: "No content - nothing is currently playing.",
    400: "Bad request - check your request parameters.",
    401: "Unauthorized - your token may be invalid or expired.",
    403: "Forbidden - you don’t have permission to access this resource.",
    404: "Not found - the resource doesn’t exist.",
    429: "Too many requests - you are being rate limited.",
    500: "Internal Server Error - Spotify had an issue.",
    502: "Bad Gateway - The server was acting as a gateway or proxy and received an invalid response from the upstream server.",
    503: "Service Unavailable - The server is currently unable to handle the request due to a temporary condition which will be alleviated after some delay. You can choose to resend the request again.",
}
>>>>>>>> origin/MM-64-jacob---code-cleanup:flask_folder/spotify_api.py

# Purpose: 
# Returns details of currently playing song for authenticated Spotify User
def now_playing():
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
    import requests
    from .spotify.spotify_tokens import clear_tokens, get_access_token

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

