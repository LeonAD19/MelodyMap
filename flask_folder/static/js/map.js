// Melody Map — Leaflet minimal client (frontend-only MVP)
// - Scroll, click, and zoom enabled.
// - Attempts to center on user's location; falls back to Texas State vicinity if denied/unavailable.
// - Prior work referenced: MM-44 (map API), MM-45 (fallback + click pins), MM-57 (geolocation centering).
// Melody Map — fixed version with reliable "You are here" pin

document.addEventListener("DOMContentLoaded", function () {
  const map = L.map("map");
  // OSM tiles
  //light mode
  const darkLayer = L.tileLayer(
    "https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png",
    {
      maxZoom: 20,
      attribution:
        '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a>, &copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }
  );
  //dark mode
  const lightLayer = L.tileLayer(
    "https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png",
    {
      maxZoom: 20,
      attribution:
        '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a>, &copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }
  );
  darkLayer.addTo(map);

  // --- TOGGLE BUTTON LOGIC ---
  let isDark = true;

document.getElementById("toggle-theme").addEventListener("click", () => {
  const btn = document.getElementById("toggle-theme");

  if (isDark) {
    map.removeLayer(darkLayer);
    lightLayer.addTo(map);
    btn.textContent = "☀︎"; // switch to sun
  } else {
    map.removeLayer(lightLayer);
    darkLayer.addTo(map);
    btn.textContent = "☾"; // switch back to moon
  }

  isDark = !isDark;
});

  // Fallback center (Texas State vicinity)
  const fallback = { lat: 29.888, lng: -97.941, zoom: 14 };
  // --- Geolocation ---
  function centerMap() {
    if (!navigator.geolocation) {
      map.setView([fallback.lat, fallback.lng], fallback.zoom);
      return;
    }
    navigator.geolocation.getCurrentPosition(
    (pos) => {
        const { latitude, longitude } = pos.coords;
        map.setView([latitude, longitude], 15);
        updateMyLocationPin(latitude, longitude);
        setInterval(() => updateMyLocationPin(latitude, longitude), 5000);
    },
    () => map.setView([fallback.lat, fallback.lng], fallback.zoom),
    { enableHighAccuracy: true, timeout: 6000 } 
    );
}

  // --- Periodic refresh of song markers ---
  function fetchAndRenderSongs() {
  fetch("/spotify/songs")
    .then(res => res.json())
    // Process the array of songs returned from the database
    .then(users => {
      // Clear old markers if needed
      if (window.songMarkers) {
        window.songMarkers.forEach(m => map.removeLayer(m));
      }
      // Reset the global marker array to empty (fresh start for new markers)
      window.songMarkers = [];

      // Loop through each song from the database and create a marker
      users.forEach(user => {
        const { username, song_title, artist_name, album_art, track_ID, lat, lng } = user;
        // Parse latitude and longitude to ensure they are numbers (not strings)
        const latitude = parseFloat(lat);
        const longitude = parseFloat(lng);

         // Validate that coordinates are valid finite numbers
        if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
          console.warn("Invalid coords for user:", username, lat, lng);
          return;  // Skip this user (bad data)
        }
          // Create a Leaflet marker at the song's coordinates
          // L.marker([lat, lng]) creates the marker object
          // .addTo(map) renders it on the map immediately (makes it visible)
        const marker = L.marker([latitude, longitude]).addTo(map);
        window.songMarkers.push(marker);

        const popupHTML = getPinHtml(album_art, song_title, artist_name, track_ID, lat, lng);
        // Attach popup to marker
        marker.bindPopup(popupHTML);

        // Open side panel when marker is clicked
        marker.on('click', () => {
          const spotifyEmbedUrl = `https://open.spotify.com/embed/track/${track_ID}`;
          openSidePanel(spotifyEmbedUrl);
        });
      });
    })

    // Handle any errors that occur during fetch or processing
    .catch(err => console.error("Failed to fetch songs:", err));
  }

    // After initial fetch, refresh every 15 seconds
    fetchAndRenderSongs();
    setInterval(fetchAndRenderSongs, 15000);

  // add event listener for queue buttons in popups
  document.addEventListener('click', (event) => {
    // Check if the clicked element is a queue button or inside one
    const queueButton = event.target.closest('.queue-track-btn');
    if (!queueButton) return;

    // Handle the queue button click
    event.preventDefault();
    
    // Get track ID from data attribute reads dataset from HTML5 data-* attributes 
    const track_Id = queueButton.dataset.trackId;
    queueTrackFromPin(track_Id, queueButton);
  });

// Queue a track from a pin/button on the UI
 // Function to queue track via backend API
  async function queueTrackFromPin(track_Id, sourceButton) {
    if (!track_Id) return;

    // Update UI to show queuing status 
    // Find the queue status label within the same pin
    const queueStatusLabel  = sourceButton?.closest('.spotify-pin')?.querySelector('.queue-status');

    // show queuing status
    if (queueStatusLabel) queueStatusLabel.textContent = 'Queuing.';

    // await backend API call to queue the track
    try {
      // Send POST request to backend to queue the track
      const res = await fetch('/spotify/queue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ track_id: track_Id })
      });
      const data = await res.json().catch(() => ({}));

      // if successful response from backend show that it was queued
      if (res.ok && data.ok !== false) {
        if (queueStatusLabel) queueStatusLabel.textContent = 'Queued on your player';
        return;
      }

      // if error response from backend show the error message
      const errorText = data.error || 'Unable to queue track';
      if (queueStatusLabel) queueStatusLabel.textContent = errorText;
    } catch (err) {
      console.error('Network error while queuing track:', err); // log error to console 
      if (queueStatusLabel) queueStatusLabel.textContent = 'Network error while queuing';
    }
  }

  let myLocationMarker = null;
  async function updateMyLocationPin (lat, lng) {

    // Remove old marker if it exists
    if (myLocationMarker) {
      map.removeLayer(myLocationMarker);
    }
  // add event listener for queue buttons in popups
  document.addEventListener('click', (event) => {
    // Check if the clicked element is a queue button or inside one
    const queueButton = event.target.closest('.queue-track-btn');
    if (!queueButton) return;

    // Handle the queue button click
    event.preventDefault();
    
    // Get track ID from data attribute reads dataset from HTML5 data-* attributes 
    const track_Id = queueButton.dataset.trackId;
    queueTrackFromPin(track_Id, queueButton);
  });

// Queue a track from a pin/button on the UI
 // Function to queue track via backend API
  async function queueTrackFromPin(track_Id, sourceButton) {
    if (!track_Id) return;

    // Update UI to show queuing status 
    // Find the queue status label within the same pin
    const queueStatusLabel  = sourceButton?.closest('.spotify-pin')?.querySelector('.queue-status');

    // show queuing status
    if (queueStatusLabel) queueStatusLabel.textContent = 'Queuing.';

    // await backend API call to queue the track
    try {
      // Send POST request to backend to queue the track
      const res = await fetch('/spotify/queue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ track_id: track_Id })
      });
      const data = await res.json().catch(() => ({}));

      // if successful response from backend show that it was queued
      if (res.ok && data.ok !== false) {
        if (queueStatusLabel) queueStatusLabel.textContent = 'Queued on your player';
        return;
      }

      // if error response from backend show the error message
      const errorText = data.error || 'Unable to queue track';
      if (queueStatusLabel) queueStatusLabel.textContent = errorText;
    } catch (err) {
      console.error('Network error while queuing track:', err); // log error to console 
      if (queueStatusLabel) queueStatusLabel.textContent = 'Network error while queuing';
    }
  }
  //custom pins

const PIN_THEMES = {
  default: {
    icon: L.icon({
    iconUrl: '/static/img/music_note_pin.png',
    
    iconSize: [40, 40],       // update to your actual PNG size
    iconAnchor: [20, 35],     // X,Y pixel that should sit on the coordinate
    popupAnchor: [0, -35]
}),
circleColor: '#121313b2'
},
  blue: {
    icon: L.icon({
      iconUrl: '/static/img/music_note_pin_blue.png',
      iconSize: [40, 40],
      iconAnchor: [20, 35],
      popupAnchor: [0, -35]
    }),
    circleColor: '#3B82F6' // Tailwind blue-500
  },

  green: {
    icon: L.icon({
      iconUrl: '/static/img/music_note_pin_green.png',
      iconSize: [40, 40],
      iconAnchor: [20, 35],
      popupAnchor: [0, -35]
    }),
    circleColor: '#22C55E'
  },

  pink: {
    icon: L.icon({
      iconUrl: '/static/img/music_note_pin_pink.png',
      iconSize: [40, 40],
      iconAnchor: [20, 35],
      popupAnchor: [0, -35]
    }),
    circleColor: '#EC4899'
  },

};

// Store current theme
let currentPinTheme = "default";
let myLocationMarker = null;
let myLocationCircle = null;

async function updateMyLocationPin(lat, lng) {
    // Remove old marker & circle
    if (myLocationMarker) map.removeLayer(myLocationMarker);
    if (myLocationCircle) map.removeLayer(myLocationCircle);

    const theme = PIN_THEMES[currentPinTheme];
    // --- Theme button click handler ---
document.addEventListener("click", (e) => {
  const btn = e.target.closest(".pin-theme-btn");
  if (!btn) return;

  const newTheme = btn.dataset.theme;
  if (!PIN_THEMES[newTheme]) return;

  currentPinTheme = newTheme;

  // If location is already on map, update immediately
  if (myLocationMarker && myLocationCircle) {
    const latLng = myLocationMarker.getLatLng();
    updateMyLocationPin(latLng.lat, latLng.lng);
  }
});

    // Circle
    myLocationCircle = L.circle([lat, lng], {
        radius: 100,
        color: theme.circleColor,
        weight: 3
    }).addTo(map);

    // Marker
    myLocationMarker = L.marker([lat, lng], { icon: theme.icon }).addTo(map);

    // Fetch now playing song
    try {
        const res = await fetch(`/spotify/now_playing?lat=${lat}&lng=${lng}&_=${Date.now()}`);
        const data = await res.json();

      if(!data.authorized) {
        myLocationMarker
          .bindPopup(`<b>You are not logged in!</b>
            <br><small>Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}</small>`)
          .openPopup();
        return;
      }
      
      if (!data.playing) {
        myLocationMarker
          .bindPopup(`<b>No song currently playing!</b>
            <br><small>Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}</small>`)
          .openPopup();
        return;
      }
      const song = data.playing;
      // Store track ID for click handler (closure issue workaround)
      const track_ID = song.track_ID;

      // Create HTML for the popup
      const html = getPinHtml(song.art, song.name, song.artists, track_ID, lat, lng);

      myLocationMarker.bindPopup(html);

      // Open side panel when user's location marker is clicked
      myLocationMarker.on('click', () => {
        console.debug('Location marker clicked, track_ID:', track_ID);
        if (track_ID) {
          const spotifyEmbedUrl = `https://open.spotify.com/embed/track/${track_ID}`;
          openSidePanel(spotifyEmbedUrl);
        } else {
          console.error('No track ID available for this song');
        }
      });
    } catch (err) {
        console.error("Error fetching song info:", err);
        myLocationMarker.bindPopup(`<b>Could not load song info</b>
            <br><small>Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}</small>`).openPopup();
    }
}


  // ---------------------------
  // Lazy refetch hook (placeholder for backend integration)
  // ---------------------------
  let refetchTimer = null;
  map.on("moveend", () => {
    if (refetchTimer) clearTimeout(refetchTimer);
    refetchTimer = setTimeout(() => {
      const c = map.getCenter();
      // Example:
      // fetch(`/api/pins?lat=${c.lat}&lng=${c.lng}&radius_miles=1`)
      //   .then(r => r.json())
      //   .then(({ pins }) => { /* upsert markers */ });
    }, 350);
  });
  // Initialize
  centerMap();
});

// This function should be called when displaying song info (successfully)
// Includes defensive checks to explicitly show which fields are invalid/missing
function getPinHtml(songImg, songName, songArtist, track_ID, lat, lng) {
  // Check for missing/invalid data and collect error messages
  const errors = [];

  if (!songImg || typeof songImg !== 'string') {
    errors.push('Image URL not set');
  }
  if (!songName || typeof songName !== 'string' || songName == 'Unknown') {
    errors.push('Song name not set');
  }
  if (!songArtist || typeof songArtist !== 'string' || songArtist == 'Unknown') {
    errors.push('Artist name not set');
  }
  if (!track_ID || typeof track_ID !== 'string') {
    errors.push('Track ID not set');
  }
  if (!lat || typeof lat !== 'number' || !Number.isFinite(lat)) {
    errors.push('Invalid latitude');
  }
  if (!lng || typeof lng !== 'number' || !Number.isFinite(lng)) {
    errors.push('Invalid longitude');
  }

  // If there are errors, show them prominently
  if (errors.length > 0) {
    return `
      <div class="spotify-pin">
          ERROR displaying pin:<br>
          ${errors.join('<br>')}
      </div>
    `;
  }

  // All data is valid, render normally
  return `
      <div class="spotify-pin">
        <img src="${songImg}" alt="Album Art" />
        <div class="track-info">
          <strong class="track-title">${songName}</strong><br>
          <span class="artist">${songArtist}</span><br>
        </div>
        <small>Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}</small>
        <div class="pin-actions">
          <button class="queue-track-btn" data-track-id="${track_ID}">Queue</button>
          <span class="queue-status" aria-live="polite"></span>
        </div>
      </div>
    `
}
