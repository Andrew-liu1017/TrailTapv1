import json
from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from trail import osm
from trail.models import Trail, Segment

PAVED = {"asphalt", "paved", "concrete", "paving_stones", "concrete:plates"}


class Command(BaseCommand):
    help = "Fetch named trails from OpenStreetMap (Overpass API) and add new ones"

    def add_arguments(self, parser):
        parser.add_argument("--bbox", default=osm.DEFAULT_BBOX,
                            help="south,west,north,east")
        parser.add_argument("--from-file",
                            help="read trails from a saved JSON file instead of the API")
        parser.add_argument("--dry-run", action="store_true",
                            help="show what would be added without saving")

    def handle(self, *args, **opts):
        if opts["from_file"]:
            with open(opts["from_file"], encoding="utf-8") as f:
                ways = json.load(f)
        else:
            try:
                ways = osm.fetch(opts["bbox"])
            except Exception as e:
                raise CommandError(f"Could not reach Overpass API: {e}")

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
