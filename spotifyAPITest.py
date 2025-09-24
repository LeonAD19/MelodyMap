import base64
import hashlib
import http.server
import json
import os
import secrets
import urllib.parse
import webbrowser
import requests
import sys
import time
from dataclasses import dataclass
from http.server import HTTPServer

# ==== SPOTIFY DASHBOARD LINK ====
# The redirect will almost definetly need to be changed
# https://developer.spotify.com/dashboard/{8fe0b36abc4744aca36f7c9bca17ef74}


# =========================
# CONFIG (used by all parts)
# =========================
# These constants are referenced by both the auth flow and the API call.
CLIENT_ID = "8fe0b36abc4744aca36f7c9bca17ef74"
REDIRECT_URI = "http://127.0.0.1:8080/callback"  # must match Spotify Dashboard
SCOPES = ["user-read-currently-playing", "user-read-playback-state"]

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

# Holds the interim result from the OAuth redirect (/callback).
@dataclass
class OAuthResult:
    code: str | None = None
    error: str | None = None
    state: str | None = None

# =========================
# SPOTIFY AUTH (main flow)
# =========================
# Purpose: Open browser for login/consent, receive 'code' on localhost:8080,
#          exchange the code (plus PKCE verifier) for an access token.
def get_access_token() -> str:
    # PKCE + CSRF state
    code_verifier, code_challenge = create_pkce_pair()
    state = secrets.token_urlsafe(16)

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
    print("\nAuthorize URL (copy/paste if needed):")
    print(auth_url, "\n")
    print("Opening browser for Spotify login...")
    webbrowser.open(auth_url)

    # Wait for Spotify to redirect with ?code=... (auth complete)
    print("Waiting for Spotify to redirect with ?code=...")
    # Start the local callback server
    wait_for_callback()

    # Validate and extract the code
    if OAuthHandler.result.error:
        print("Authorization error:", OAuthHandler.result.error)
        sys.exit(1)
    if OAuthHandler.result.state != state:
        print("State mismatch. Aborting.")
        sys.exit(1)
    auth_code = OAuthHandler.result.code
    if not auth_code:
        print("No code received (did you open /callback manually?).")
        sys.exit(1)

    # Exchange authorization code for access token (OAuth token endpoint)
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "code_verifier": code_verifier,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_resp = requests.post(TOKEN_URL, data=data, headers=headers)
    print("\nToken response status:", token_resp.status_code)
    if token_resp.status_code != 200:
        print("Token exchange failed:", token_resp.text)
        sys.exit(1)

    tokens = token_resp.json()
    access_token = tokens["access_token"]
    print("Access token acquired ✔")
    return access_token

# =========================
# SERVER SETUP (local loopback)
# =========================
# Purpose: Minimal HTTP server that listens on 127.0.0.1 to receive
#          Spotify’s redirect with ?code=...&state=...
def wait_for_callback():
    host = "127.0.0.1"
    port = urllib.parse.urlparse(REDIRECT_URI).port or 8080
    httpd = HTTPServer((host, port), OAuthHandler)
    httpd.timeout = 120  # optional: give yourself time to click “Agree”
    print(f"Listening on {REDIRECT_URI} ...")
    httpd.handle_request()   # handle exactly ONE request, then return
    httpd.server_close()

class OAuthHandler(http.server.BaseHTTPRequestHandler):
    result: OAuthResult = OAuthResult()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        print(f"[HTTP] GET {self.path}")

        # Ensure the path matches your REDIRECT_URI path (/callback).
        if parsed.path != urllib.parse.urlparse(REDIRECT_URI).path:
            self.send_error(404, "Not Found")
            return

        # Capture query params from Spotify: code, error, state.
        qs = urllib.parse.parse_qs(parsed.query)
        code  = qs.get("code",  [None])[0]
        error = qs.get("error", [None])[0]
        state = qs.get("state", [None])[0]
        OAuthHandler.result = OAuthResult(code=code, error=error, state=state)

        # Minimal success HTML back to the browser.
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        if code:
            self.wfile.write(b"<h2>Auth complete. Code received. You can close this tab.</h2>")
        else:
            self.wfile.write(b"<h2>No code in query. Did you open this URL manually?</h2>")

    def log_message(self, *args, **kwargs):
        pass  # silence default logs

# =========================
# API CALL (business logic)
# =========================
# Purpose: Use the access token to call /v1/me/player/currently-playing,
#          then parse and print the track info. (Polled every 3 seconds.)
def now_playing(access_token):
    api_headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=api_headers)

    print("\nCurrently Playing status:", r.status_code)
    if r.status_code == 204:
        print("Nothing is currently playing.")
        return
    if r.status_code != 200:
        print("API error:", r.status_code, r.text)
        return

    payload = r.json()
    # print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))

    # Safe field access to avoid KeyErrors if fields are missing
    item = (payload.get("item") or {})
    name = item.get("name") or "Unknown"
    album = item.get("album") or {}
    album_name = album.get("name") or "Unknown"
    album_images = album.get("images") or "N/A"
    album_art = album_images[0].get("url")     # get url from images
    artists_list = item.get("artists") or []
    artists = ", ".join(a.get("name", "") for a in artists_list) or "Unknown"

    print(f"\nNow playing: {name} ({album_name}) — {artists}")
    print(f"Link to art: {album_art}")


# =========================
# ENTRYPOINT (poll every 3s)
# =========================
if __name__ == "__main__":
    try:
        token = get_access_token()        # ——> AUTH
        while True:
            now_playing(token)            # ——> API CALL
            time.sleep(3)                 # ——> simple polling interval
    except KeyboardInterrupt:
        print("\nCancelled.")