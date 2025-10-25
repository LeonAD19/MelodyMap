// Melody Map — Leaflet minimal client (frontend-only MVP)
// - Scroll, click, and zoom enabled.
// - Attempts to center on user's location; falls back to Texas State vicinity if denied/unavailable.
// - Prior work referenced: MM-44 (map API), MM-45 (fallback + click pins), MM-57 (geolocation centering).
// Melody Map — fixed version with reliable "You are here" pin

document.addEventListener("DOMContentLoaded", function () {
  const map = L.map("map");
  // OSM tiles
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
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

  // Fetch mock song data from Flask endpoints
  // Currently loads from static/mock/mock.json until MongoDB integration is ready
  fetch("/spotify/songs")
    .then(response => response.json())
    .then(users => {
      users.forEach(user => {
        const {  username, song_title, artist_name, album_art, location } = user;
        if (!location) return;
        const lat = parseFloat(location.lat);
        const lng = parseFloat(location.lng);
        if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;

        const popupHTML = `
          <img src="${album_art}" alt="Album Art" width="100" style="border-radius:10px;margin-bottom:6px;">
          <div><strong>${song_title}</strong> by ${artist_name}</div>
          <div><em>Shared by ${username}</em></div>
          <div style="font-size:0.85em;">Platform: ${platform}</div>
        `;
        L.marker([lat, lng]).addTo(map).bindPopup(popupHTML);
      });
    });

  // --- Click to drop pins ---
  map.on("click", async (e) => {
  const { lat, lng } = e.latlng;
  const marker = L.marker([lat, lng]).addTo(map);

  try {
    const res = await fetch(`/spotify/now_playing?lat=${lat}&lng=${lng}&_=${Date.now()}`);
    // Parse JSON rather than just getting ALL the text
    const data = await res.json();
    if (!data.authorized || !data.playing) {
      marker
        .bindPopup(`<b>No song currently playing</b>
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
