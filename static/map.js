
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


// "Locate me" button: shows your position on the map using the browser's GPS
let youMarker = null;
let youCircle = null;
let tracking = false;
let firstFix = false;
let locateBtn = null;

const LocateControl = L.Control.extend({
  options: { position: "topleft" },
  onAdd: function () {
    const bar = L.DomUtil.create("div", "leaflet-bar leaflet-control");
    const btn = L.DomUtil.create("a", "locate-btn", bar);
    btn.href = "#";
    btn.title = "Show my location";
    btn.setAttribute("role", "button");
    btn.innerHTML =
      '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">' +
      '<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="2.5" fill="currentColor"/>' +
      '<line x1="12" y1="1" x2="12" y2="4"/><line x1="12" y1="20" x2="12" y2="23"/>' +
      '<line x1="1" y1="12" x2="4" y2="12"/><line x1="20" y1="12" x2="23" y2="12"/></svg>';
    L.DomEvent.disableClickPropagation(btn);
    locateBtn = btn;
    L.DomEvent.on(btn, "click", (e) => {
      L.DomEvent.preventDefault(e);
      if (tracking) {
        stopTracking();
      } else {
        tracking = true;
        firstFix = true;
        btn.classList.add("active");
        btn.title = "Stop following my location";
        map.locate({ watch: true, enableHighAccuracy: true });
      }
    });
    return bar;
  },
});
map.addControl(new LocateControl());

function stopTracking() {
  tracking = false;
  map.stopLocate();
  locateBtn.classList.remove("active");
  locateBtn.title = "Show my location";
}

map.on("locationfound", (e) => {
  if (firstFix) {
    map.setView(e.latlng, 16);
    firstFix = false;
  } else if (tracking) {
    map.panTo(e.latlng);
  }
  if (youMarker) {
    youMarker.setLatLng(e.latlng);
    youCircle.setLatLng(e.latlng).setRadius(e.accuracy);
  } else {
    youCircle = L.circle(e.latlng, {
      radius: e.accuracy, color: "#1e88e5", weight: 1, fillOpacity: 0.1,
    }).addTo(map);
    youMarker = L.circleMarker(e.latlng, {
      radius: 8, color: "#fff", weight: 3, fillColor: "#1e88e5", fillOpacity: 1,
    }).addTo(map).bindPopup("You are here");
  }
});

map.on("locationerror", () => {
  stopTracking();
  alert("Couldn't get your location. Check that location access is allowed for this site.");
});
