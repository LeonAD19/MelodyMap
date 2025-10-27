// Melody Map — Leaflet minimal client (frontend-only MVP)
// - Scroll, click, and zoom enabled.
// - Attempts to center on user's location; falls back to Texas State vicinity if denied/unavailable.
// - Prior work referenced: MM-44 (map API), MM-45 (fallback + click pins), MM-57 (geolocation centering).
// Melody Map — fixed version with reliable "You are here" pin

document.addEventListener("DOMContentLoaded", function () {
  const map = L.map("map");
  // OSM tiles
  L.tileLayer("https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png", {
  maxZoom: 20,
  attribution:
    '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a>, &copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

  
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

        // Show 1-mile radius + marker
        L.circle([latitude, longitude], { radius: 1609.34 }).addTo(map);
        L.marker([latitude, longitude])
          .addTo(map)
          .bindPopup("<b>You are here</b>")
          .openPopup();
      },
      // On error: use fallback center (MM-45)
      () => {
        map.setView([fallback.lat, fallback.lng], fallback.zoom);
      },
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
        const { username, song_title, artist_name, album_art, lat, lng } = user;
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

        // Build the popup HTML content that shows when user clicks the marker
        const popupHTML = `
          <img src="${album_art}" alt="Album Art" width="100" style="border-radius:10px;margin-bottom:6px;">
          <div><strong>${song_title || 'Unknown'}</strong> by ${artist_name || 'Unknown'}</div>
        `;
        // Attach popup to marker
        marker.bindPopup(popupHTML);
      });
    })

    // Handle any errors that occur during fetch or processing
    .catch(err => console.error("Failed to fetch songs:", err));
}

    // After initial fetch, refrsh every 15 seconds
    fetchAndRenderSongs();
    setInterval(fetchAndRenderSongs, 15000);

  // --- Click to drop pins ---
  map.on("click", async (e) => {
  const { lat, lng } = e.latlng;
  const marker = L.marker([lat, lng]).addTo(map);

  try {
    const res = await fetch(`/spotify/now_playing?lat=${lat}&lng=${lng}&_=${Date.now()}`);
    // Parse JSON rather than just getting ALL the text
    const data = await res.json();
    if(!data.authorized) {
      marker
        .bindPopup(`<b>You are not logged in!</b>
          <br><small>Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}</small>`)
        .openPopup();
      return;
    }
     
    if (!data.playing) {
      marker
        .bindPopup(`<b>No song currently playing!</b>
          <br><small>Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}</small>`)
        .openPopup();
      return;
    }
    const song = data.playing;
    // Create HTML for the popup
    const html = `
      <div class="spotify-pin">
        <img src="${song.art}" alt="Album Art" />
        <div class="track-info">
          <strong class="track-title">${song.name}</strong><br>
          <span class="artist">${song.artists}</span><br>
        </div>
        <small>Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}</small>
      </div>
    `;
    marker.bindPopup(html).openPopup();
  } catch (err) {
    console.error("Error fetching song info:", err);
    marker
      .bindPopup(`<b>Could not load song info</b><br>
                  <small>Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}</small>`)
      .openPopup();
  }
});
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
