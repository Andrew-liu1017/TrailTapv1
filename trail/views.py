from datetime import timedelta
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from .forms import ReportForm
from .models import Segment, Report


def map_view(request):
    segments = Segment.objects.select_related("trail")

    if request.GET.get("paved"):
        segments = segments.filter(trail__paved=True)
    if request.GET.get("dogs"):
        segments = segments.filter(trail__dogs_allowed=True)
    if request.GET.get("stroller"):
        segments = segments.filter(trail__stroller_friendly=True)

    data = []
    for seg in segments:
        report = seg.current_report()
        data.append({
            "name": seg.name,
            "status": report.get_condition_display() if report else "No recent reports",
            "color": report.color if report else "gray",
            "geometry": seg.geometry,
            "url": reverse("segment", args=[seg.id]),
        })
    return render(request, "map.html", {"segments": data, "active": request.GET})


def segment_view(request, pk):
    segment = Segment.objects.get(pk=pk)

    if request.method == "POST":
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.segment = segment
            report.save()
            return redirect("segment", pk=pk)
    else:
        form = ReportForm()
    return render(request, "segment.html", {
        "segment": segment,
        "current": segment.current_report(),
        "recent": segment.reports.order_by("-created_at")[:3],
        "form": form,
    })


def report_action(request, pk, action):
    report = Report.objects.get(pk=pk)
    if action == "still":
        report.expires_at = timezone.now() + timedelta(days=Report.EXPIRY_DAYS[report.condition])
        report.save()
    elif action == "fixed":
        report.expires_at = timezone.now()
        report.save()
        Report.objects.create(segment=report.segment, condition="clear")
    return redirect("segment", pk=report.segment_id)