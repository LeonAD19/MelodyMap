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

  // Client side to animate progress smoothly between intervals 
  let hasSongData = false;
  let clientProgressTime = 0;
  let clientDurationTimeMS = 0;
  let lastUpdatedTimeSaved = 0;
  let isPlaying = false;

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

  // Render progress and bar width given progress + duration
  function renderProgress(progress, clientDurationTimeMS) {
    const checkValidTime = clientDurationTimeMS || 0; // if null value we set to 0
    // max will either be 0 (if we get a wrong calculation that is negative we set back to 0)
    // min will set progress back in from going above track length
    const progressWithinRange = Math.max(0, Math.min(progress || 0, checkValidTime));
    let percent = 0; 
    // if validTime is above 0 calculate progress bar and set it to percentage (can only be 0 through 1)
    if (checkValidTime > 0){
      percent = (progressWithinRange / checkValidTime) * 100;
    } 
    if (progressFill){
      progressFill.style.width = `${percent}%`;
    }

    // Setting time 
    if (currentTime){
      currentTime.textContent = formatTime(progressWithinRange);
    } 
    if (durationTime) {
      durationTime.textContent = formatTime(checkValidTime);
    } 
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

    // Update client-side  for smooth ticking
    clientProgressTime = song.progress_ms || 0;
    clientDurationTimeMS = song.duration_ms || 0;
    lastUpdatedTimeSaved = Date.now();
    isPlaying = !!song.is_playing;
    hasSongData = true;

    // Render once client gets server-provided values
    renderProgress(clientProgressTime, clientDurationTimeMS);
  }

  // Update the UI when no song is playing
  function showNothingPlaying() {
    if (title) title.textContent = 'No song playing';
    if (artists) artists.textContent = 'No artist';
    if (art) art.src = '/static/spotifylogo.png';
    if (progressFill) progressFill.style.width = '0%';
    if (currentTime) currentTime.textContent = '0:00';
    if (durationTime) durationTime.textContent = '0:00';

    // Clear progress state
    hasSongData = false;
    clientProgressTime = 0;
    clientDurationTimeMS = 0;
    lastUpdatedTimeSaved = 0;
  }

  // Start with the card hidden until we know the state
  if (card) card.style.display = 'none';

  // tick to simulate real time progress between server ticks
  function tick() {
    // checking to see if client hasSong data or clientDurationTimeMS is there if not dont Tick
    if (!hasSongData || !clientDurationTimeMS){
      return;
    } 
    if (!isPlaying) {
      // If paused, hold exactly at server point
      renderProgress(clientProgressTime, clientDurationTimeMS);
      return;
    }
    const elapsedTime = Date.now() - lastUpdatedTimeSaved; // ms since last server update
    const projected = clientProgressTime + elapsedTime;
    renderProgress(projected, clientDurationTimeMS);
  }

  // Get the first update immediately and start intervals
  getNowPlaying();
  setInterval(getNowPlaying, 5000);
  setInterval(tick, 1000);
});
