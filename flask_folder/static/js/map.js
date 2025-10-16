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

  // --- Click to drop pins ---
  map.on("click", async (e) => {
    const { lat, lng } = e.latlng;
    try {
      const res = await fetch("/spotify/now_playing?_" + Date.now());
      const html = await res.text();
      L.marker([lat, lng])
        .addTo(map)
        .bindPopup(
          `<div style="max-width:250px;">
            ${html}<br><small>Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}</small>
          </div>`
        )
        .openPopup();
    } catch {
      L.marker([lat, lng])
        .addTo(map)
        .bindPopup("<b>Could not load song info</b>")
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
