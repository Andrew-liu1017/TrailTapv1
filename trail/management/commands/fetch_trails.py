import json
from django.core.management.base import BaseCommand, CommandError

from trail import osm
from trail.importer import import_ways


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

        added = import_ways(ways, dry_run=opts["dry_run"], log=self.stdout.write)
        self.stdout.write(self.style.SUCCESS(f"Done. {added} new trail(s)."))
