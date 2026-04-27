from django.contrib import admin
from .models import Exam, ExamResult, ReportCard

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'academic_year', 'term', 'is_published', 'created_at']
    list_filter = ['exam_type', 'is_published', 'academic_year', 'term']
    list_editable = ['is_published']
    search_fields = ['name']
    filter_horizontal = ['streams']

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'subject', 'grade', 'raw_score', 'points']
    list_filter = ['exam', 'subject', 'grade']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number']

@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'mean_grade', 'total_points', 'created_at']
    list_filter = ['exam', 'mean_grade']
    search_fields = ['student__first_name', 'student__last_name', 'student__admission_number']
