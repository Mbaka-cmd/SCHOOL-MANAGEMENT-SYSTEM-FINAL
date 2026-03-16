# REPLACE schools/urls.py with this:
from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.smart_dashboard, name="admin_dashboard"),
    path("dashboard/bursar/", views.bursar_dashboard, name="bursar_dashboard"),
    path("dashboard/principal/", views.principal_dashboard, name="principal_dashboard"),
    path("dashboard/dean/", views.dean_dashboard, name="dean_dashboard"),
    path("dashboard/super/", views.super_admin_dashboard, name="super_admin_dashboard"),
    path("search/", views.global_search, name="global_search"),
    path("kcse/upload/", views.kcse_upload, name="kcse_upload"),
]