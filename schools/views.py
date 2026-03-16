from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum, Q
from students.models import Student
from exams.models import Exam, ExamResult, ReportCard, score_to_grade
from fees.models import FeeInvoice, Payment
from academics.models import Stream, Subject
from accounts.models import User
import json


# ── DECORATORS ─────────────────────────────────────────────

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_school_admin or request.user.is_teacher or request.user.is_platform_admin):
            return HttpResponseForbidden(_access_denied_html())
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def bursar_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        allowed = (
            request.user.is_platform_admin or
            (request.user.is_school_admin and request.user.school_role in ('bursar', 'super_admin', 'admin'))
        )
        if not allowed:
            return HttpResponseForbidden(_access_denied_html())
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def _access_denied_html():
    return """<!DOCTYPE html><html><head><title>Access Denied</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap" rel="stylesheet">
    <style>body{font-family:Poppins,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#f8f9fa;}
    .box{text-align:center;padding:3rem;background:white;border-radius:20px;box-shadow:0 10px 40px rgba(0,0,0,0.1);max-width:400px;}
    h2{color:#C0392B;}a{background:#C0392B;color:white;padding:0.7rem 2rem;border-radius:25px;text-decoration:none;font-weight:600;}</style>
    </head><body><div class="box"><div style="font-size:3rem;">⛔</div><h2>Access Denied</h2>
    <p style="color:#666;margin-bottom:1.5rem;">You don't have permission to view this page.</p>
    <a href="/">Go Home</a></div></body></html>"""


# ── SMART DASHBOARD ROUTER ──────────────────────────────────

@login_required
def smart_dashboard(request):
    user = request.user

    if user.is_platform_admin:
        return redirect('super_admin_dashboard')

    if user.is_school_admin:
        role = getattr(user, 'school_role', 'admin')
        if role == 'bursar':
            return redirect('bursar_dashboard')
        elif role == 'principal':
            return redirect('principal_dashboard')
        elif role == 'dean':
            return redirect('dean_dashboard')
        elif role == 'super_admin':
            return redirect('super_admin_dashboard')
        else:
            # ✅ FIX: redirect to main_dashboard not admin_dashboard
            return redirect('main_dashboard')

    if user.is_teacher:
        # ✅ FIX: redirect to main_dashboard not admin_dashboard
        return redirect('main_dashboard')

    return redirect('home')


# ── ADMIN DASHBOARD (General) ───────────────────────────────

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
        "paid_count": paid_count,
        "pending_count": pending_count,
        "partial_count": partial_count,
        "overdue_count": overdue_count,
        "stream_labels_json": json.dumps(stream_labels),
        "stream_counts_json": json.dumps(stream_counts),
        "grade_labels_json": json.dumps(grade_labels),
        "grade_counts_json": json.dumps(grade_counts),
        "recent_exams": recent_exams,
        "recent_students": recent_students,
    }
    return render(request, "schools/admin_dashboard.html", context)


# ── BURSAR DASHBOARD ────────────────────────────────────────

@admin_required
def bursar_dashboard(request):
    school = request.user.school
    all_invoices = FeeInvoice.objects.filter(school=school)
    all_payments = Payment.objects.filter(school=school)

    total_expected = all_invoices.aggregate(t=Sum('total_expected'))['t'] or 0
    total_collected = all_invoices.aggregate(t=Sum('total_paid'))['t'] or 0
    total_balance = total_expected - total_collected
    collection_rate = round((total_collected / total_expected * 100), 1) if total_expected > 0 else 0

    mpesa_total = all_payments.filter(method='mpesa', is_reversed=False).aggregate(t=Sum('amount'))['t'] or 0
    bank_total = all_payments.filter(method='bank', is_reversed=False).aggregate(t=Sum('amount'))['t'] or 0
    cash_total = all_payments.filter(method='cash', is_reversed=False).aggregate(t=Sum('amount'))['t'] or 0
    bursary_total = all_payments.filter(method='bursary', is_reversed=False).aggregate(t=Sum('amount'))['t'] or 0

    paid_count = all_invoices.filter(status='paid').count()
    partial_count = all_invoices.filter(status='partial').count()
    pending_count = all_invoices.filter(status='pending').count()
    total_invoices = all_invoices.count()

    defaulters = all_invoices.filter(
        status__in=['pending', 'partial']
    ).select_related('student', 'student__current_stream').order_by('-total_expected')[:10]

    recent_payments = all_payments.select_related(
        'invoice__student', 'received_by'
    ).order_by('-payment_date')[:15]

    context = {
        "school": school,
        "total_expected": total_expected,
        "total_collected": total_collected,
        "total_balance": total_balance,
        "collection_rate": collection_rate,
        "mpesa_total": mpesa_total,
        "bank_total": bank_total,
        "cash_total": cash_total,
        "bursary_total": bursary_total,
        "paid_count": paid_count,
        "partial_count": partial_count,
        "pending_count": pending_count,
        "total_invoices": total_invoices,
        "defaulters": defaulters,
        "recent_payments": recent_payments,
    }
    return render(request, "schools/bursar_dashboard.html", context)


# ── PRINCIPAL DASHBOARD ─────────────────────────────────────

@admin_required
def principal_dashboard(request):
    school = request.user.school

    total_students = Student.objects.filter(school=school, is_active=True).count()
    total_teachers = User.objects.filter(school=school, is_teacher=True, is_active=True).count()
    total_streams = Stream.objects.filter(school=school).count()
    total_exams = Exam.objects.filter(school=school).count()

    all_invoices = FeeInvoice.objects.filter(school=school)
    total_expected = all_invoices.aggregate(t=Sum('total_expected'))['t'] or 0
    total_collected = all_invoices.aggregate(t=Sum('total_paid'))['t'] or 0
    total_balance = total_expected - total_collected
    collection_rate = round((total_collected / total_expected * 100), 1) if total_expected > 0 else 0

    paid_count = all_invoices.filter(status='paid').count()
    partial_count = all_invoices.filter(status='partial').count()
    pending_count = all_invoices.filter(status='pending').count()

    recent_students = Student.objects.filter(
        school=school, is_active=True
    ).order_by('-created_at')[:6]

    context = {
        "school": school,
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_streams": total_streams,
        "total_exams": total_exams,
        "total_expected": total_expected,
        "total_collected": total_collected,
        "total_balance": total_balance,
        "collection_rate": collection_rate,
        "paid_count": paid_count,
        "partial_count": partial_count,
        "pending_count": pending_count,
        "recent_students": recent_students,
    }
    return render(request, "schools/principal_dashboard.html", context)


# ── DEAN DASHBOARD ──────────────────────────────────────────

@admin_required
def dean_dashboard(request):
    school = request.user.school

    total_students = Student.objects.filter(school=school, is_active=True).count()
    total_streams = Stream.objects.filter(school=school).count()
    total_exams = Exam.objects.filter(school=school).count()

    streams = Stream.objects.filter(school=school).order_by(
        'class_level__level_order', 'name'
    ).prefetch_related('students')

    stream_data = []
    for s in streams:
        count = s.students.filter(is_active=True).count()
        stream_data.append({'stream': s, 'count': count})

    recent_students = Student.objects.filter(
        school=school, is_active=True
    ).order_by('-created_at')[:10]

    recent_exams = Exam.objects.filter(school=school).order_by('-created_at')[:5]

    grade_labels = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'E']
    grade_counts = [
        ExamResult.objects.filter(exam__school=school, grade=g).count()
        for g in grade_labels
    ]

    context = {
        "school": school,
        "total_students": total_students,
        "total_streams": total_streams,
        "total_exams": total_exams,
        "stream_data": stream_data,
        "recent_students": recent_students,
        "recent_exams": recent_exams,
        "grade_labels_json": json.dumps(grade_labels),
        "grade_counts_json": json.dumps(grade_counts),
    }
    return render(request, "schools/dean_dashboard.html", context)


# ── SUPER ADMIN DASHBOARD (Mercy only) ─────────────────────

@login_required
def super_admin_dashboard(request):
    if not request.user.is_platform_admin:
        return HttpResponseForbidden(_access_denied_html())

    from schools.models import School
    all_schools = School.objects.filter(is_active=True)
    total_schools = all_schools.count()
    total_students = Student.objects.filter(is_active=True).count()
    total_revenue = Payment.objects.filter(
        is_reversed=False
    ).aggregate(t=Sum('amount'))['t'] or 0

    schools_data = []
    for school in all_schools:
        invoices = FeeInvoice.objects.filter(school=school)
        expected = invoices.aggregate(t=Sum('total_expected'))['t'] or 0
        collected = invoices.aggregate(t=Sum('total_paid'))['t'] or 0
        rate = round((collected / expected * 100), 1) if expected > 0 else 0
        schools_data.append({
            'school': school,
            'students': Student.objects.filter(school=school, is_active=True).count(),
            'expected': expected,
            'collected': collected,
            'rate': rate,
        })

    context = {
        "total_schools": total_schools,
        "total_students": total_students,
        "total_revenue": total_revenue,
        "schools_data": schools_data,
    }
    return render(request, "schools/super_admin_dashboard.html", context)


# ── GLOBAL SEARCH ────────────────────────────────────────────

@admin_required
def global_search(request):
    school = request.user.school
    q = request.GET.get("q", "").strip()
    students = []
    if q and len(q) >= 2:
        students = Student.objects.filter(
            school=school, is_active=True
        ).filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(admission_number__icontains=q)
        )[:20]
    context = {"q": q, "students": students}
    return render(request, "schools/search_results.html", context)


# ── KCSE UPLOAD ──────────────────────────────────────────────

@admin_required
def kcse_upload(request):
    from schools.models import KCSEResult
    school = request.user.school
    if request.method == "POST":
        year = request.POST.get("year")
        candidates = request.POST.get("candidates_sat", 0)
        mean_grade = request.POST.get("mean_grade", "")
        mean_points = request.POST.get("mean_points", 0)
        university_qualifiers = request.POST.get("university_qualifiers", 0)
        pass_rate = request.POST.get("pass_rate", 0)
        notes = request.POST.get("notes", "")
        KCSEResult.objects.update_or_create(
            school=school, year=year,
            defaults={
                "candidates_sat": candidates,
                "mean_grade": mean_grade,
                "mean_points": mean_points,
                "university_qualifiers": university_qualifiers,
                "pass_rate": pass_rate,
                "notes": notes,
            }
        )
        from django.contrib import messages
        messages.success(request, f"KCSE {year} results saved!")
        return redirect("kcse_upload")
    from schools.models import KCSEResult
    results = KCSEResult.objects.filter(school=school).order_by("-year")
    return render(request, "schools/kcse_upload.html", {"results": results, "school": school})