"""Shared Spotify-related error messages.

This module centralizes user-facing messages for common Spotify Web API
HTTP status codes so they can be reused across the codebase.
"""

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

