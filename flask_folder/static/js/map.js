// Melody Map - Leaflet minimal client (frontend-only MVP)
(function () {
  // Create the map
  const map = L.map("map");

  // OSM tile layer (free, attribution required)
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  // Fallback center (Texas State vicinity) if geolocation is denied/unavailable
  const fallback = { lat: 29.888, lng: -97.941, zoom: 14 };

  // Try to center on user, else use fallback
  function centerMap() {
    if (!navigator.geolocation) {
      map.setView([fallback.lat, fallback.lng], fallback.zoom);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        map.setView([latitude, longitude], 15);

        // Visual 1-mile radius around user (1609.34 meters)
        L.circle([latitude, longitude], { radius: 1609.34 }).addTo(map);

        // Mark the user's approximate location
        L.marker([latitude, longitude]).addTo(map)
          .bindPopup("<b>You are here</b>").openPopup();
      },
      () => {
        map.setView([fallback.lat, fallback.lng], fallback.zoom);
      },
      { enableHighAccuracy: true, timeout: 6000 }
    );
  }

  // Click to add a demo marker (no backend yet)
  map.on("click", (e) => {
    const { lat, lng } = e.latlng;
    L.marker([lat, lng])
      .addTo(map)
      .bindPopup(`<b>Demo Pin</b><br>Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`)
      .openPopup();
  });

  // Lazy refetch hook (placeholder for when you add a backend later)
  let refetchTimer = null;
  map.on("moveend", () => {
    if (refetchTimer) clearTimeout(refetchTimer);
    refetchTimer = setTimeout(() => {
      const c = map.getCenter();
      // Example: fetch(`/api/pins?lat=${c.lat}&lng=${c.lng}&radius_miles=1`)
      //   .then(r => r.json()).then(({pins}) => { /* upsert markers */ });
    }, 350);
  });

  centerMap();
})();
