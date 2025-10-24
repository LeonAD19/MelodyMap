// Run this after the page fully loads
document.addEventListener('DOMContentLoaded', () => {
  // Grab only what we need: the card and title elements
  const card = document.getElementById('user-card');
  const title = document.getElementById('user-title');

  // Hide the card if user is not logged in to Spotify
  if (!window.SPOTIFY_AUTH) {
    if (card) card.style.display = 'none';
    return;
  }

  // This function asks our backend what song is playing on Spotify
  async function getNowPlaying() {
    try {
      // Add timestamp to prevent caching
      const params = new URLSearchParams({ _: Date.now().toString() });

      // Fetch the current playback data from the backend
      const response = await fetch(`/spotify/now_playing?${params.toString()}`);
      const data = await response.json().catch(() => ({}));

      // If not authorized, hide card and stop
      if (!data || data.authorized === false) {
        if (card) card.style.display = 'none';
        return;
      }

      // Make sure the card is visible when authorized
      if (card) card.style.display = 'block';

      // If a song is playing, update the title
      if (data.playing && title) {
        title.textContent = data.playing.name || 'Unknown Song';
      } else if (title) {
        // No song currently playing
        title.textContent = 'No song playing';
      }

    } catch (error) {
      // Ignore errors and try again later
    }
  }

  // Hide the card initially until we know the state
  if (card) card.style.display = 'none';
  
  // Fetch right away
  getNowPlaying();
});
