from django.urls import path
from . import views, kcse_views

urlpatterns = [
    path("dashboard/", views.smart_dashboard, name="admin_dashboard"),
    path("dashboard/main/", views.admin_dashboard, name="main_dashboard"),
    path("dashboard/bursar/", views.bursar_dashboard, name="bursar_dashboard"),
    path("dashboard/principal/", views.principal_dashboard, name="principal_dashboard"),
    path("dashboard/dean/", views.dean_dashboard, name="dean_dashboard"),
    path("dashboard/super/", views.super_admin_dashboard, name="super_admin_dashboard"),
    path("search/", views.global_search, name="global_search"),
    path("kcse/upload/", kcse_views.kcse_upload, name="kcse_upload"),
    path("kcse/toggle/<int:year>/", kcse_views.kcse_toggle_publish, name="kcse_toggle_publish"),
]


