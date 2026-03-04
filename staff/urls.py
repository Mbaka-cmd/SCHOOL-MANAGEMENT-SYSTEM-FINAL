from django.urls import path
from . import views

urlpatterns = [
    path("", views.staff_list, name="staff_list"),
    path("add/", views.staff_add, name="staff_add"),
    path("<str:pk>/", views.staff_detail, name="staff_detail"),
    path("<str:pk>/edit/", views.staff_edit, name="staff_edit"),
]