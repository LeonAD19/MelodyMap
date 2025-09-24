import base64
import hashlib
import os
import secrets
import urllib.parse
import requests
import sys
import time
from flask import Blueprint, session, request, redirect, jsonify, url_for

# ==== SPOTIFY DASHBOARD LINK ====
# The redirect will almost definetly need to be changed
# https://developer.spotify.com/dashboard/{8fe0b36abc4744aca36f7c9bca17ef74}

bp = Blueprint("spotify", __name__, url_prefix="/spotify")

# =========================
# CONFIG (used by all parts)
# =========================
# These constants are referenced by both the auth flow and the API call.

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")  # must match Spotify Dashboard
SCOPES = os.getenv('SPOTIFY_SCOPES').split()

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"


# =========================
# SPOTIFY AUTH (PKCE utils)
# =========================
# Purpose: Create PKCE code_verifier and code_challenge used in OAuth.
def _b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

def create_pkce_pair():
    code_verifier = _b64url(os.urandom(64))
    code_challenge = _b64url(hashlib.sha256(code_verifier.encode("ascii")).digest())
    return code_verifier, code_challenge


# =========================
# LOGIN ROUTE
# =========================
# Purpose: Redirect for user to login/consent for us to do 
@bp.route("/login")
def login():
    # PKCE + CSRF state
    code_verifier, code_challenge = create_pkce_pair()
    state = secrets.token_urlsafe(16)

    # stash for callback
    session["spotify_code_verifier"] = code_verifier
    session["spotify_state"] = state
    
    # Build /authorize URL and open the browser
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
        "state": state,
        "scope": " ".join(SCOPES),
        "show_dialog": "true",
    }
    auth_url = AUTH_URL + "?" + urllib.parse.urlencode(params)    
    # print("\nAuthorize URL (copy/paste if needed):")
    # print(auth_url, "\n")
    # print("Opening browser for Spotify login...")
    return redirect(auth_url)



@bp.route("/callback")
def callback():
    err = request.args.get("error")
    if err:
        return f"Spotify auth error: {err}", 400

    code = request.args.get("code")
    state = request.args.get("state")
    if not code or not state:
        return "Missing code/state", 400
    if state != session.get("spotify_state"):
        return "State mismatch", 400

    # Exchange authorization code for access token (OAuth token endpoint)
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "code_verifier": session.get("spotify_code_verifier"),
    }
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_resp = requests.post(TOKEN_URL, data=data, headers=headers)
    
    # print("\nToken response status:", token_resp.status_code)
    if token_resp.status_code != 200:
        print("Token exchange failed:", token_resp.text)
        sys.exit(1)

    _set_tokens(token_resp.json())
    
    # cleanup
    session.pop("spotify_code_verifier", None)
    session.pop("spotify_state", None)
    
    # land on a whats playing page
    return redirect(url_for("spotify.now_playing"))

def _set_tokens(tokens: dict):
    session["spotify_access_token"]  = tokens.get("access_token")
    session["spotify_refresh_token"] = tokens.get("refresh_token")
    # expire a tad early to be safe
    expires_in = int(tokens.get("expires_in", 3600))
    session["spotify_expires_at"] = int(time.time()) + expires_in - 30
    
# =========================
# API CALL (business logic)
# =========================
# Purpose: Use the access token to call /v1/me/player/currently-playing,
@bp.route("/now_playing")
def now_playing():
    print('Now playing')
    token = ensure_access_token()
    if not token:
        return jsonify({"authorized": False, "playing": None})
    
    api_headers = {"Authorization": f"Bearer {token}"}
    r = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=api_headers)

    # print("\nCurrently Playing status:", r.status_code)
    if r.status_code == 204:
        return jsonify({"authorized": True, "playing": None})
    if r.status_code != 200:
        return jsonify({"authorized": True, "error": r.text}), r.status_code

    payload = r.json()
    # print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))

    # Safe field access to avoid KeyErrors if fields are missing
    item = (payload.get("item") or {})
    name = item.get("name") or "Unknown"
    album = item.get("album") or {}
    album_name = album.get("name") or "Unknown"
    album_images = album.get("images") or []
    album_art = album_images[0].get("url") if album_images else None    # get url from images
    artists_list = item.get("artists") or []
    artists = ", ".join(a.get("name", "") for a in artists_list) or "Unknown"

    # print(f"\nNow playing: {name} ({album_name}) — {artists}")
    # print(f"Link to art: {album_art}")
    
    return jsonify({
        "authorized": True,
        "playing": {
            "name": name,
            "album": album_name,
            "artists": artists,
            "art": album_art,
            "is_playing": payload.get("is_playing", False),
            "progress_ms": payload.get("progress_ms"),
            "duration_ms": item.get("duration_ms"),
        }
    })

# Return a valid access token
# Should refresh if needed
def ensure_access_token() -> str:
    access = session.get("spotify_access_token")
    exp_at = session.get("spotify_expires_at", 0)
    
    if access and time.time() < exp_at:
        return access       # Early exit if the token is still good

    refresh = session.get("spotify_refresh_token")
    if not refresh:
        return None         # Give up if there is no spotify_refresh_token

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "client_id": CLIENT_ID,
    }
    r = requests.post(TOKEN_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    if r.status_code != 200:
        # clear on failure so UI can prompt to reconnect
        for k in list(session.keys()):
            if k.startswith("spotify_"):
                session.pop(k)
        return None
    _set_tokens(r.json())
    return session.get("spotify_access_token")