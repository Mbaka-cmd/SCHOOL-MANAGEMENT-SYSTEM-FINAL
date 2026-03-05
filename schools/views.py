from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum, Q
from students.models import Student
from exams.models import Exam, ExamResult, ReportCard, score_to_grade
from fees.models import FeeInvoice
from academics.models import Stream, Subject
from accounts.models import User
import json


# ── CUSTOM DECORATOR ─────────────────────────────────────────
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_school_admin or request.user.is_teacher or request.user.is_platform_admin):
            return HttpResponseForbidden("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Access Denied</title>
                    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap" rel="stylesheet">
                    <style>
                        body { font-family: Poppins, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; background: #f8f9fa; }
                        .box { text-align: center; padding: 3rem; background: white; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); max-width: 400px; }
                        h2 { color: #C0392B; font-size: 2rem; margin-bottom: 0.5rem; }
                        p { color: #666; margin-bottom: 1.5rem; }
                        a { background: #C0392B; color: white; padding: 0.7rem 2rem; border-radius: 25px; text-decoration: none; font-weight: 600; }
                    </style>
                </head>
                <body>
                    <div class="box">
                        <div style="font-size:3rem;">⛔</div>
                        <h2>Access Denied</h2>
                        <p>You don't have permission to view this page.</p>
                        <a href="/">Go Home</a>
                    </div>
                </body>
                </html>
            """)
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ── ADMIN DASHBOARD ──────────────────────────────────────────
@admin_required
def admin_dashboard(request):
    school = request.user.school

    total_students = Student.objects.filter(school=school, is_active=True).count()
    total_teachers = User.objects.filter(school=school, is_teacher=True, is_active=True).count()
    total_streams = Stream.objects.filter(school=school).count()
    total_subjects = Subject.objects.filter(school=school).count()
    total_exams = Exam.objects.filter(school=school).count()

    all_invoices = FeeInvoice.objects.filter(school=school)
    total_expected = all_invoices.aggregate(t=Sum('total_expected'))['t'] or 0
    total_collected = all_invoices.aggregate(t=Sum('total_paid'))['t'] or 0
    total_balance = total_expected - total_collected
    collection_rate = round((total_collected / total_expected * 100), 1) if total_expected > 0 else 0

    streams = Stream.objects.filter(school=school).order_by('class_level__level_order', 'name')
    stream_labels = [s.full_name for s in streams]
    stream_counts = [s.students.filter(is_active=True).count() for s in streams]

    paid_count = all_invoices.filter(status='paid').count()
    pending_count = all_invoices.filter(status='pending').count()
    partial_count = all_invoices.filter(status='partial').count()
    overdue_count = all_invoices.filter(status='overdue').count()

    grade_labels = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'E']
    grade_counts = [ExamResult.objects.filter(exam__school=school, grade=g).count() for g in grade_labels]

    recent_exams = Exam.objects.filter(school=school).order_by('-created_at')[:5]
    recent_students = Student.objects.filter(school=school, is_active=True).order_by('-created_at')[:5]

    context = {
        "school": school,
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_streams": total_streams,
        "total_subjects": total_subjects,
        "total_exams": total_exams,
        "total_expected": total_expected,
        "total_collected": total_collected,
        "total_balance": total_balance,
        "collection_rate": collection_rate,
        "stream_labels": json.dumps(stream_labels),
        "stream_counts": json.dumps(stream_counts),
        "fee_data": json.dumps([paid_count, pending_count, partial_count, overdue_count]),
        "grade_labels": json.dumps(grade_labels),
        "grade_counts": json.dumps(grade_counts),
        "recent_exams": recent_exams,
        "recent_students": recent_students,
    }
    return render(request, "schools/admin_dashboard.html", context)


# ── GLOBAL SEARCH ────────────────────────────────────────────
@admin_required
def global_search(request):
    query = request.GET.get('q', '').strip()
    school = request.user.school
    results = {
        'students': [],
        'exams': [],
        'staff': [],
        'invoices': [],
    }

    if query:
        results['students'] = Student.objects.filter(
            school=school, is_active=True
        ).filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(middle_name__icontains=query) |
            Q(admission_number__icontains=query) |
            Q(nemis_number__icontains=query)
        )[:10]

        results['exams'] = Exam.objects.filter(
            school=school
        ).filter(
            Q(name__icontains=query) |
            Q(exam_type__icontains=query)
        )[:5]

        results['staff'] = User.objects.filter(
            school=school, is_teacher=True, is_active=True
        ).filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )[:5]

        results['invoices'] = FeeInvoice.objects.filter(
            school=school
        ).filter(
            Q(invoice_number__icontains=query) |
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query)
        ).select_related('student')[:5]

    total = sum(len(v) for v in results.values())

    context = {
        'query': query,
        'results': results,
        'total': total,
    }
    return render(request, 'schools/search_results.html', context)