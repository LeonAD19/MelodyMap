// Run this after the page fully loads
document.addEventListener('DOMContentLoaded', () => {
  // Get all the elements we will update
  const card = document.getElementById('user-card');
  const art = document.getElementById('user-art');
  const title = document.getElementById('user-title');
  const artists = document.getElementById('user-artists');
  const progressFill = document.getElementById('user-progress-fill');
  const currentTime = document.getElementById('user-current');
  const durationTime = document.getElementById('user-duration');

  // Hide the card completely if the user is not logged in to Spotify
  if (!window.SPOTIFY_AUTH) {
    if (card) card.style.display = 'none';
    return;
  }

  // This function converts milliseconds (like 125000) into M:SS format
  function formatTime(ms) {
    if (typeof ms !== 'number') return '0:00'; //catches anything that isn't a 'number'
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = String(seconds % 60).padStart(2, '0');
    return `${minutes}:${remainingSeconds}`;
  }

  // This function asks our backend what song is playing on Spotify
  async function getNowPlaying() {
    try {
      // Create a URL with a timestamp so the browser doesn’t use an old cached response
      const params = new URLSearchParams({ _: Date.now().toString() });

      // Ask the server for the current song
      const response = await fetch(`/spotify/now_playing?${params.toString()}`);
      const data = await response.json().catch(() => ({}));

      // If not authorized, hide everything and stop
      if (!data || data.authorized === false) {
        if (card) card.style.display = 'none';
        return;
      }

      // Make sure the card is visible when authorized
      if (card) card.style.display = 'block';

      // If nothing is playing, show placeholder info
      if (!data.playing) {
        showNothingPlaying();
        return;
      }

      // Otherwise, update the display with the song info
      const song = data.playing;
      updateSongInfo(song);
    } catch (error) {
      // Ignore errors (network, parsing, etc.) and try again later
    }
  }

  // Update the UI when a song is playing
  function updateSongInfo(song) {
    if (title) title.textContent = song.name || 'Unknown Song';
    if (artists) artists.textContent = song.artists || 'Unknown Artist';
    if (art) art.src = song.art || '/static/spotifylogo.png';

    const progress = song.progress_ms || 0;
    const duration = song.duration_ms || 0;
    const percent = duration > 0 ? (progress / duration) * 100 : 0;

    if (progressFill) progressFill.style.width = `${percent}%`;
    if (currentTime) currentTime.textContent = formatTime(progress);
    if (durationTime) durationTime.textContent = formatTime(duration);
  }

  // Update the UI when no song is playing
  function showNothingPlaying() {
    if (title) title.textContent = 'No song playing';
    if (artists) artists.textContent = 'No artist';
    if (art) art.src = '/static/spotifylogo.png';
    if (progressFill) progressFill.style.width = '0%';
    if (currentTime) currentTime.textContent = '0:00';
    if (durationTime) durationTime.textContent = '0:00';
  }

  // Start with the card hidden until we know the state
  if (card) card.style.display = 'none';

  // Get the first update immediately
  getNowPlaying();

});
