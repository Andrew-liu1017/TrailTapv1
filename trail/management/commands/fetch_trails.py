import json
import ssl
import urllib.parse
import urllib.request
from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from trail.models import Trail, Segment

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Toledo / Perrysburg area: south, west, north, east
DEFAULT_BBOX = "41.45,-83.95,41.78,-83.40"

PAVED = {"asphalt", "paved", "concrete", "paving_stones", "concrete:plates"}

QUERY = """
[out:json][timeout:90];
way["highway"~"^(path|footway|track|cycleway|bridleway)$"]
   ["name"~"Trail|Loop|Path|Greenway|Towpath",i]({bbox});
out tags geom;
"""


class Command(BaseCommand):
    help = "Fetch named trails from OpenStreetMap (Overpass API) and add new ones"

    def add_arguments(self, parser):
        parser.add_argument("--bbox", default=DEFAULT_BBOX,
                            help="south,west,north,east")
        parser.add_argument("--dry-run", action="store_true",
                            help="show what would be added without saving")

    def handle(self, *args, **opts):
        ways = self.fetch(opts["bbox"])

        by_name = defaultdict(list)
        for way in ways:
            if len(way.get("geometry", [])) >= 2:
                by_name[way["tags"]["name"]].append(way)

        added = 0
        for name, parts in sorted(by_name.items()):
            slug = slugify(name)
            if Trail.objects.filter(slug=slug).exists():
                continue  # keep existing trails and their reports

            tags = [w["tags"] for w in parts]
            paved = sum(t.get("surface") in PAVED for t in tags) > len(tags) / 2
            dogs = not any(t.get("dog") == "no" for t in tags)
            stroller = paved or any(t.get("wheelchair") == "yes" for t in tags)

            self.stdout.write(f"{'Would add' if opts['dry_run'] else 'Adding'}: "
                              f"{name} ({len(parts)} sections)")
            added += 1
            if opts["dry_run"]:
                continue

            trail = Trail.objects.create(name=name, slug=slug, paved=paved,
                                         dogs_allowed=dogs, stroller_friendly=stroller)
            for i, way in enumerate(parts, start=1):
                coords = [[p["lon"], p["lat"]] for p in way["geometry"]]
                Segment.objects.create(trail=trail, order=i,
                                       name=f"{name} - section {i}",
                                       geometry={"type": "LineString", "coordinates": coords})

        self.stdout.write(self.style.SUCCESS(f"Done. {added} new trail(s)."))

    def fetch(self, bbox):
        data = urllib.parse.urlencode({"data": QUERY.format(bbox=bbox)}).encode()
        req = urllib.request.Request(OVERPASS_URL, data=data,
                                     headers={"User-Agent": "TrailTap/1.0"})
        try:
            try:
                import certifi
                ctx = ssl.create_default_context(cafile=certifi.where())
            except ImportError:
                ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
                return json.load(resp)["elements"]
        except Exception as e:
            raise CommandError(f"Could not reach Overpass API: {e}")
