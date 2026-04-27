from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import AttendanceSession, AttendanceRecord
from students.models import Student
from academics.models import Stream
from schools.models import School


def get_school():
    return School.objects.first()


@login_required
def attendance_dashboard(request):
    school = get_school()
    today = timezone.now().date()
    today_sessions = AttendanceSession.objects.filter(school=school, date=today).select_related('stream')
    recent_sessions = AttendanceSession.objects.filter(school=school).select_related('stream', 'taken_by')[:20]
    streams = Stream.objects.all()
    total_students = Student.objects.filter(is_active=True).count()
    today_present = AttendanceRecord.objects.filter(session__date=today, status='present').count()
    today_absent = AttendanceRecord.objects.filter(session__date=today, status='absent').count()
    return render(request, 'attendance/dashboard.html', {
        'school': school,
        'today_sessions': today_sessions,
        'recent_sessions': recent_sessions,
        'streams': streams,
        'total_students': total_students,
        'today_present': today_present,
        'today_absent': today_absent,
        'today': today,
    })


@login_required
def take_attendance(request):
    school = get_school()
    streams = Stream.objects.all()
    if request.method == 'POST':
        stream_id = request.POST.get('stream')
        date = request.POST.get('date')
        session_type = request.POST.get('session')
        stream = get_object_or_404(Stream, id=stream_id)
        session, created = AttendanceSession.objects.get_or_create(
            school=school, date=date, session=session_type, stream=stream,
            defaults={'taken_by': request.user}
        )
        if not created:
            messages.warning(request, f'Attendance for {stream} on {date} ({session_type}) already exists.')
            return redirect('attendance_view', session_id=session.id)
        students = Student.objects.filter(current_stream=stream, is_active=True)
        for student in students:
            status = request.POST.get(f'student_{student.id}', 'absent')
            remarks = request.POST.get(f'remarks_{student.id}', '')
            AttendanceRecord.objects.create(session=session, student=student, status=status, remarks=remarks)
        messages.success(request, f'Attendance saved for {stream} — {len(students)} students recorded.')
        return redirect('attendance_dashboard')
    stream_id = request.GET.get('stream')
    selected_stream = None
    students = []
    if stream_id:
        selected_stream = get_object_or_404(Stream, id=stream_id)
        students = Student.objects.filter(current_stream=selected_stream, is_active=True).order_by('last_name')
    return render(request, 'attendance/take_attendance.html', {
        'school': school,
        'streams': streams,
        'selected_stream': selected_stream,
        'students': students,
        'today': timezone.now().date(),
    })


@login_required
def attendance_view(request, session_id):
    school = get_school()
    session = get_object_or_404(AttendanceSession, id=session_id)
    records = session.records.select_related('student').order_by('student__last_name')
    return render(request, 'attendance/view_attendance.html', {
        'school': school,
        'session': session,
        'records': records,
    })


@login_required
def student_attendance_report(request, student_id):
    school = get_school()
    student = get_object_or_404(Student, id=student_id)
    records = AttendanceRecord.objects.filter(student=student).select_related('session').order_by('-session__date')
    total = records.count()
    present = records.filter(status='present').count()
    absent = records.filter(status='absent').count()
    late = records.filter(status='late').count()
    rate = round((present / total) * 100, 1) if total > 0 else 0
    return render(request, 'attendance/student_report.html', {
        'school': school,
        'student': student,
        'records': records,
        'total': total,
        'present': present,
        'absent': absent,
        'late': late,
        'rate': rate,
    })


@login_required
def attendance_history(request):
    school = get_school()
    sessions = AttendanceSession.objects.filter(school=school).select_related('stream', 'taken_by').order_by('-date')
    return render(request, 'attendance/history.html', {
        'school': school,
        'sessions': sessions,
    })

