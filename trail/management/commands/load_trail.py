import json
from django.core.management.base import BaseCommand
from trail.models import Trail, Segment


class Command(BaseCommand):
    help = "Load trail segments from a GeoJSON file"

    def add_arguments(self, parser):
        parser.add_argument("path")
        parser.add_argument("trail_slug")

    def handle(self, *args, **opts):
        trail = Trail.objects.get(slug=opts["trail_slug"])
        trail.segments.all().delete()
        with open(opts["path"], encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for feature in data["features"]:
            geom = feature["geometry"]
            if geom["type"] != "LineString":
                continue
            count += 1
            Segment.objects.create(trail=trail, order=count,
                                   name=f"{trail.name} - section {count}",
                                   geometry=geom)
        self.stdout.write(self.style.SUCCESS(f"Loaded {count} segments"))

