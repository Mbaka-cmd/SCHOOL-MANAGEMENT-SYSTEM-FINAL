from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_dashboard, name='attendance_dashboard'),
    path('take/', views.take_attendance, name='take_attendance'),
    path('view/<int:session_id>/', views.attendance_view, name='attendance_view'),
    path('student/<uuid:student_id>/', views.student_attendance_report, name='student_attendance_report'),
    path('history/', views.attendance_history, name='attendance_history'),
]
