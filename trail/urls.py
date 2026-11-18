from django.urls import path
from . import views

urlpatterns = [
    path("", views.map_view, name="map"),
    path("segment/<int:pk>/", views.segment_view, name="segment"),
    path("report/<int:pk>/<str:action>/", views.report_action, name="report_action"),
    path("sync-trails/", views.sync_trails, name="sync_trails"),
]