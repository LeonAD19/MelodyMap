// Melody Map - Leaflet minimal client (frontend-only MVP)
//The code below lets you scroll, click, and zoom
//Users should be able to move around in the map after allowing website to use their location
//Previous commit had code needed for MM-44. However, it was previously tested just to see that the map API was successfully implemented
(function () {
  // Create the map
  const map = L.map("map");

  // OSM tile layer (free, attribution required)
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  //This part correlates to MM-45 as it has its fallback center to the (Texas State vicinity) if geolocation is denied/unavailable
  const fallback = { lat: 29.888, lng: -97.941, zoom: 14 };

  // Try to center on user, else use fallback
  //The function below satisfies the task of MM-57 since it centers itself around the user location
  //Uses Geolocation in order to center around user's location
  function centerMap() {
    if (!navigator.geolocation) {
      map.setView([fallback.lat, fallback.lng], fallback.zoom);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        map.setView([latitude, longitude], 15);

        //This initializes a visual 1-mile radius around user 
        L.circle([latitude, longitude], { radius: 1609.34 }).addTo(map);

        //These lines allow the user to mark the user's approximate location
        L.marker([latitude, longitude]).addTo(map)
          .bindPopup("<b>You are here</b>").openPopup();
      },
      () => {
        map.setView([fallback.lat, fallback.lng], fallback.zoom);
      },
      { enableHighAccuracy: true, timeout: 6000 }
    );
  }

  //These lines allow a user to click and put a pin somewhere on the map, provides coordinates as well
  //Multiple pins may be displayed and available to user
  //Lines below satisfy MM-45 requirements
  map.on("click", (e) => {
    const { lat, lng } = e.latlng;
    L.marker([lat, lng])
      .addTo(map)
      .bindPopup(`<b>Demo Pin</b><br>Lat: ${lat.toFixed(5)}, Lng: ${lng.toFixed(5)}`)
      .openPopup();
  });

  //This is a lazy refetch hook (placeholder for when you add a backend later)
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
