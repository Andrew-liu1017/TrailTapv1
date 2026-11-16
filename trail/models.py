from datetime import timedelta
from django.db import models
from django.utils import timezone


class Trail(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    paved = models.BooleanField(default=True)
    dogs_allowed = models.BooleanField(default=True)
    stroller_friendly = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Segment(models.Model):
    trail = models.ForeignKey(Trail, on_delete=models.CASCADE, related_name="segments")
    name = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)

    geometry = models.JSONField()

    class Meta:
        ordering = ["trail", "order"]

    def current_report(self):
        return self.reports.filter(expires_at__gt=timezone.now()).order_by("-created_at").first()

    def __str__(self):
        return self.name


class Report(models.Model):
    CONDITIONS = [
        ("clear", "All clear"),
        ("muddy", "Muddy / wet"),
        ("icy", "Icy"),
        ("flooded", "Flooded"),
        ("blocked", "Tree or debris blocking"),
        ("closed", "Closed"), ]

    EXPIRY_DAYS = {"clear": 3,
                   "muddy": 2,
                   "icy": 1,
                   "flooded": 3,
                   "blocked": 7,
                   "closed": 30}

    COLORS = {"clear": "green",
              "muddy": "yellow",
              "icy": "yellow",
              "flooded": "red",
              "blocked": "red",
              "closed": "red"}

    segment = models.ForeignKey(Segment, on_delete=models.CASCADE, related_name="reports")
    condition = models.CharField(max_length=20, choices=CONDITIONS)
    note = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to="reports/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()




    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=self.EXPIRY_DAYS[self.condition])
        super().save(*args, **kwargs)

    @property
    def color(self):
        return self.COLORS[self.condition]

    def __str__(self):
        return f"{self.segment} - {self.get_condition_display()}"
