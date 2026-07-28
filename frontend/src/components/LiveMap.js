let mapInstance = null;
let markerInstance = null;

export function initLiveMap(lat = 12.9716, lng = 77.5946) {
  setTimeout(() => {
    const mapElement = document.getElementById('leaflet-map');
    if (!mapElement || typeof L === 'undefined') return;

    if (mapInstance) {
      mapInstance.remove();
      mapInstance = null;
    }

    mapInstance = L.map('leaflet-map').setView([lat, lng], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors | Q-Transplant GPS'
    }).addTo(mapInstance);

    const customIcon = L.divIcon({
      className: 'custom-map-icon',
      html: `<div style="background:#0f62fe; color:white; padding:6px 10px; border-radius:15px; font-weight:bold; font-size:11px; box-shadow:0 0 10px rgba(15,98,254,0.5);"><i class="fa-solid fa-truck-medical"></i> COLD-BOX</div>`
    });

    markerInstance = L.marker([lat, lng], { icon: customIcon }).addTo(mapInstance)
      .bindPopup('<b>ESP32 Cold Box Transport</b><br>Temp: 4.2°C | Speed: 45 km/h')
      .openPopup();
  }, 100);
}

export function updateMapLocation(lat, lng) {
  if (mapInstance && markerInstance) {
    markerInstance.setLatLng([lat, lng]);
    mapInstance.panTo([lat, lng]);
  }
}
