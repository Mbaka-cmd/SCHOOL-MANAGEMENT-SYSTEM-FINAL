from django.urls import path
from . import views
from . import kcse_views

urlpatterns = [
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("search/", views.global_search, name="global_search"),
    path("kcse/", kcse_views.kcse_upload, name="kcse_upload"),
    path("kcse/toggle/<int:year>/", kcse_views.kcse_toggle_publish, name="kcse_toggle_publish"),
]
