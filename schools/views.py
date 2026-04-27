from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Sum, Q
from students.models import Student
from exams.models import Exam, ExamResult, ReportCard, score_to_grade
from fees.models import FeeInvoice, Payment
from academics.models import Stream, Subject
from accounts.models import User
from django.core.management import call_command
from django.http import HttpResponse
import json
import os
from django.conf import settings


# â”€â”€ DECORATORS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
    </head><body><div class="box"><div style="font-size:3rem;">â›”</div><h2>Access Denied</h2>
    <p style="color:#666;margin-bottom:1.5rem;">You don't have permission to view this page.</p>
    <a href="/">Go Home</a></div></body></html>"""


# â”€â”€ SMART DASHBOARD ROUTER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
            # âœ… FIX: redirect to main_dashboard not admin_dashboard
            return redirect('main_dashboard')

    if user.is_teacher:
        # âœ… FIX: redirect to main_dashboard not admin_dashboard
        return redirect('main_dashboard')

    return redirect('home')


# â”€â”€ ADMIN DASHBOARD (General) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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

    # Convert Decimal objects to float for JSON serialization
    total_expected = float(total_expected) if total_expected else 0.0
    total_collected = float(total_collected) if total_collected else 0.0
    total_balance = float(total_balance) if total_balance else 0.0

    streams = Stream.objects.filter(school=school).order_by('class_level__level_order', 'name')
    stream_labels = [s.full_name for s in streams]
    stream_counts = [s.students.filter(is_active=True).count() for s in streams]

    paid_count = all_invoices.filter(status='paid').count()
    pending_count = all_invoices.filter(status='pending').count()
    partial_count = all_invoices.filter(status='partial').count()
    overdue_count = all_invoices.filter(status='overdue').count()

    # Fee analytics data for chart - showing amounts with color coding
    fee_labels = ['Expected Fees', 'Collected Fees', 'Outstanding Balance']
    fee_data = [total_expected, total_collected, total_balance]
    fee_colors = ['#2ecc71', '#f1c40f', '#e74c3c']  # Green, Yellow, Red

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
        "fee_labels_json": json.dumps(fee_labels),
        "fee_data_json": json.dumps(fee_data),
        "fee_colors_json": json.dumps(fee_colors),
        "stream_labels_json": json.dumps(stream_labels),
        "stream_counts_json": json.dumps(stream_counts),
        "grade_labels_json": json.dumps(grade_labels),
        "grade_counts_json": json.dumps(grade_counts),
        "recent_exams": recent_exams,
        "recent_students": recent_students,
    }
    return render(request, "schools/admin_dashboard.html", context)


# â”€â”€ BURSAR DASHBOARD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ PRINCIPAL DASHBOARD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ DEAN DASHBOARD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ SUPER ADMIN DASHBOARD (Mercy only) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
    return render(request, "schools/admin_dashboard.html", context)

# â”€â”€ DATA MANAGEMENT VIEWS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@login_required
def clear_data(request):
    if not request.user.is_platform_admin:
        return JsonResponse({'success': False, 'error': 'Permission denied'})

    if request.method == 'POST':
        try:
            # First create a backup
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            os.makedirs(backup_dir, exist_ok=True)

            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'backup_before_clear_{timestamp}.json'

            # Get all data to backup
            from django.core import serializers
            data_to_backup = []
            models_to_backup = [
                'accounts.User',
                'schools.School',
                'students.Student',
                'academics.Stream',
                'academics.Subject',
                'exams.Exam',
                'exams.ExamResult',
                'fees.FeeInvoice',
                'fees.Payment',
                'attendance.Attendance',
                'library.Book',
                'notices.Notice',
                'timetable.TimetableEntry',
            ]

            for model_name in models_to_backup:
                try:
                    app_label, model_label = model_name.split('.')
                    from django.apps import apps
                    model = apps.get_model(app_label, model_label)
                    data_to_backup.extend(serializers.serialize('json', model.objects.all()))
                except:
                    pass  # Skip if model doesn't exist

            # Save backup
            backup_path = os.path.join(backup_dir, backup_filename)
            with open(backup_path, 'w') as f:
                f.write('[' + ','.join(data_to_backup) + ']')

            # Now clear the data
            call_command('clear_data')
            return JsonResponse({'success': True, 'backup_created': backup_filename})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid method'})


@login_required
def clear_drafts(request):
    if not (request.user.is_platform_admin or request.user.is_school_admin):
        return JsonResponse({'success': False, 'error': 'Permission denied'})

    if request.method == 'POST':
        try:
            # Delete all draft exams (unpublished exams) for the user's school
            from exams.models import Exam
            if request.user.is_platform_admin:
                draft_exams = Exam.objects.filter(is_published=False)
            else:
                draft_exams = Exam.objects.filter(school=request.user.school, is_published=False)
            count = draft_exams.count()
            draft_exams.delete()
            return JsonResponse({'success': True, 'message': f'Deleted {count} draft exams'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid method'})


@login_required
def clear_old_attendance(request):
    if not (request.user.is_platform_admin or request.user.is_school_admin):
        return JsonResponse({'success': False, 'error': 'Permission denied'})

    if request.method == 'POST':
        try:
            from datetime import timedelta
            from django.utils import timezone
            from attendance.models import AttendanceSession, AttendanceRecord

            # Delete attendance records older than 30 days for the user's school
            cutoff_date = timezone.now().date() - timedelta(days=30)
            if request.user.is_platform_admin:
                old_sessions = AttendanceSession.objects.filter(date__lt=cutoff_date)
            else:
                old_sessions = AttendanceSession.objects.filter(stream__school=request.user.school, date__lt=cutoff_date)
            count = old_sessions.count()
            old_sessions.delete()  # This will cascade delete AttendanceRecord objects

            return JsonResponse({'success': True, 'message': f'Deleted {count} attendance sessions older than 30 days'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid method'})


@login_required
def attendance_history(request):
    if not (request.user.is_platform_admin or request.user.is_school_admin):
        return JsonResponse({'success': False, 'error': 'Permission denied'})

    try:
        from attendance.models import AttendanceSession
        from django.core.paginator import Paginator

        # Get all attendance sessions with pagination for the user's school
        if request.user.is_platform_admin:
            sessions = AttendanceSession.objects.select_related('stream', 'taken_by').order_by('-date')
        else:
            sessions = AttendanceSession.objects.filter(stream__school=request.user.school).select_related('stream', 'taken_by').order_by('-date')
        paginator = Paginator(sessions, 50)  # 50 sessions per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'schools/attendance_history.html', {
            'page_obj': page_obj,
            'total_sessions': sessions.count(),
        })
    except Exception as e:
        messages.error(request, f'Error loading attendance history: {str(e)}')
        return redirect('admin_dashboard')


@login_required
def backup_data(request):
    if not request.user.is_platform_admin:
        return JsonResponse({'success': False, 'error': 'Permission denied'})

    if request.method == 'POST':
        try:
            # Create backup directory if it doesn't exist
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            os.makedirs(backup_dir, exist_ok=True)

            # Generate backup filename
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f'backup_{timestamp}.db'
            backup_path = os.path.join(backup_dir, backup_file)

            # Copy database file
            import shutil
            db_path = settings.DATABASES['default']['NAME']
            shutil.copy2(db_path, backup_path)

            # Return download URL
            backup_url = f'/media/backups/{backup_file}'
            return JsonResponse({
                'success': True,
                'backup_url': backup_url,
                'filename': backup_file
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid method'})

# â”€â”€ GLOBAL SEARCH â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€ KCSE UPLOAD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@admin_required
def kcse_upload(request):
    from website.models import KCSEResult
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
    from website.models import KCSEResult
    results = KCSEResult.objects.filter(school=school).order_by("-year")
    return render(request, "schools/kcse_upload.html", {"results": results, "school": school})

