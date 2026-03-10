from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("website.urls")),
    path("accounts/", include("accounts.urls")),
    path("school-admin/", include("schools.urls")),
    path("students/", include("students.urls")),
    path("fees/", include("fees.urls")),
    path("exams/", include("exams.urls")),
    path("staff/", include("staff.urls")),
    path("portal/", include("portal.urls")),
    path("library/", include("library.urls")),
    path("communications/", include("communications.urls")),
    path("attendance/", include("attendance.urls")),
    path("notices/", include("notices.urls")),
    path("timetable/", include("timetable.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
