"""Download named trails from OpenStreetMap's Overpass API.

No Django imports here, so this file can also run on its own
(GitHub Actions uses it to refresh data/osm_trails.json daily).
"""
import json
import ssl
import sys
import urllib.parse
import urllib.request

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Toledo / Perrysburg area: south, west, north, east
DEFAULT_BBOX = "41.45,-83.95,41.78,-83.40"

QUERY = """
[out:json][timeout:90];
way["highway"~"^(path|footway|track|cycleway|bridleway)$"]
   ["name"~"Trail|Loop|Path|Greenway|Towpath",i]({bbox});
out tags geom;
"""


def fetch(bbox=DEFAULT_BBOX):
    data = urllib.parse.urlencode({"data": QUERY.format(bbox=bbox)}).encode()
    req = urllib.request.Request(OVERPASS_URL, data=data,
                                 headers={"User-Agent": "TrailTap/1.0"})
    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
        return json.load(resp)["elements"]


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "data/osm_trails.json"
    elements = fetch()
    elements.sort(key=lambda e: e["id"])  # stable order = clean git diffs
    with open(out, "w", encoding="utf-8") as f:
        json.dump(elements, f, indent=1)
    print(f"Saved {len(elements)} trail pieces to {out}")
