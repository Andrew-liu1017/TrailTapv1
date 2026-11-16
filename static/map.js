
const segments = JSON.parse(document.getElementById("segments-data").textContent);

const colors = { green: "#2e7d32", yellow: "#f9a825", red: "#c62828", gray: "#9e9e9e" };

const map = L.map("map").setView([41.6, -83.7], 11);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

const group = L.featureGroup().addTo(map);
segments.forEach((s) => {

  L.geoJSON(s.geometry, { style: { color: colors[s.color], weight: 7 } })

    .bindPopup(`<b>${s.name}</b><br>${s.status}<br><a href="${s.url}">Details / report</a>`)
    .addTo(group);
});

if (segments.length) map.fitBounds(group.getBounds());

