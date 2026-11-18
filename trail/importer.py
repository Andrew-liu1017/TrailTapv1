from collections import defaultdict

from django.db import transaction
from django.utils.text import slugify

from .models import Trail, Segment

PAVED = {"asphalt", "paved", "concrete", "paving_stones", "concrete:plates"}


def import_ways(ways, dry_run=False, log=print):
    """Add new trails from OpenStreetMap ways. Existing trails (and their reports) are kept."""
    by_name = defaultdict(list)
    for way in ways:
        if len(way.get("geometry", [])) >= 2 and way.get("tags", {}).get("name"):
            by_name[way["tags"]["name"]].append(way)

    added = 0
    with transaction.atomic():
        for name, parts in sorted(by_name.items()):
            slug = slugify(name)
            if not slug or Trail.objects.filter(slug=slug).exists():
                continue

            tags = [w["tags"] for w in parts]
            paved = sum(t.get("surface") in PAVED for t in tags) > len(tags) / 2
            dogs = not any(t.get("dog") == "no" for t in tags)
            stroller = paved or any(t.get("wheelchair") == "yes" for t in tags)

            log(f"{'Would add' if dry_run else 'Adding'}: {name} ({len(parts)} sections)")
            added += 1
            if dry_run:
                continue

            trail = Trail.objects.create(name=name, slug=slug, paved=paved,
                                         dogs_allowed=dogs, stroller_friendly=stroller)
            for i, way in enumerate(parts, start=1):
                coords = [[p["lon"], p["lat"]] for p in way["geometry"]]
                Segment.objects.create(trail=trail, order=i,
                                       name=f"{name} - section {i}",
                                       geometry={"type": "LineString", "coordinates": coords})
    return added
