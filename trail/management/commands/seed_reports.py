import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from trail.models import Segment, Report


SAMPLES = [
    ("flooded", "Water over the path after last night's rain"),
    ("blocked", "Large branch across the trail"),
    ("muddy", "Soft and slippery near the bridge"),
    ("icy", "Shaded stretch is icy in the morning"),
    ("clear", ""),
    ("clear", "Freshly cleared, great shape"),
]


class Command(BaseCommand):
    help = "Replace all reports with sample demo reports"

    def handle(self, *args, **opts):
        Report.objects.all().delete()
        now = timezone.now()
        segments = list(Segment.objects.all())
        for seg in random.sample(segments, k=min(len(segments), 15)):
            condition, note = random.choice(SAMPLES)
            report = Report.objects.create(segment=seg, condition=condition, note=note)
            hours_ago = random.randint(1, 20)
            Report.objects.filter(pk=report.pk).update(created_at=now - timedelta(hours=hours_ago))
        self.stdout.write(self.style.SUCCESS("Seeded demo reports"))

