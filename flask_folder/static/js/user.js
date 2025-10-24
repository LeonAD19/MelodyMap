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

  // Hide the card initially until we know the state
  if (card) card.style.display = 'none';

});
