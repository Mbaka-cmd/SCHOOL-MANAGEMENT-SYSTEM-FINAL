from django.urls import path
from . import views

urlpatterns = [
    path("", views.student_list, name="student_list"),
    path("by-stream/", views.students_by_stream, name="students_by_stream"),
    path("add/", views.student_add, name="student_add"),
    path("bulk-import/", views.student_bulk_import, name="student_bulk_import"),
    path("download-template/", views.download_import_template, name="download_import_template"),
    path("<uuid:pk>/", views.student_detail, name="student_detail"),
    path("<uuid:pk>/edit/", views.student_edit, name="student_edit"),
]
