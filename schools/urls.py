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
    path("clear-data/", views.clear_data, name="clear_data"),
    path("clear-drafts/", views.clear_drafts, name="clear_drafts"),
    path("clear-old-attendance/", views.clear_old_attendance, name="clear_old_attendance"),
    path("attendance-history/", views.attendance_history, name="attendance_history"),
    path("backup-data/", views.backup_data, name="backup_data"),
    path("kcse/upload/", kcse_views.kcse_upload, name="kcse_upload"),
    path("kcse/toggle/<int:year>/", kcse_views.kcse_toggle_publish, name="kcse_toggle_publish"),
path("dashboard/teacher/", views.teacher_dashboard, name="teacher_dashboard"),
]


