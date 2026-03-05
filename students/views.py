from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Student
from academics.models import Stream, ClassLevel
from schools.models import AcademicYear
from schools.views import admin_required


@admin_required
def student_list(request):
    school = request.user.school
    students = Student.objects.filter(school=school, is_active=True)

    stream_id = request.GET.get("stream")
    class_level_id = request.GET.get("class_level")
    search = request.GET.get("search", "")

    if stream_id:
        students = students.filter(current_stream_id=stream_id)
    if class_level_id:
        students = students.filter(current_stream__class_level_id=class_level_id)
    if search:
        students = students.filter(
            first_name__icontains=search
        ) | students.filter(
            last_name__icontains=search
        ) | students.filter(
            admission_number__icontains=search
        )

    class_levels = ClassLevel.objects.filter(school=school)
    streams = Stream.objects.filter(school=school)

    context = {
        "students": students.order_by("current_stream__class_level__level_order", "last_name"),
        "class_levels": class_levels,
        "streams": streams,
        "total": students.count(),
        "search": search,
    }
    return render(request, "students/student_list.html", context)


@admin_required
def student_add(request):
    school = request.user.school
    if request.method == "POST":
        try:
            student = Student(
                school=school,
                admission_number=request.POST.get("admission_number"),
                first_name=request.POST.get("first_name"),
                last_name=request.POST.get("last_name"),
                middle_name=request.POST.get("middle_name", ""),
                date_of_birth=request.POST.get("date_of_birth"),
                gender=request.POST.get("gender", "female"),
                admission_date=request.POST.get("admission_date"),
                admission_type=request.POST.get("admission_type", "form1"),
                is_boarder=request.POST.get("is_boarder") == "on",
                dormitory=request.POST.get("dormitory", ""),
                kcpe_marks=request.POST.get("kcpe_marks") or None,
                nemis_number=request.POST.get("nemis_number", ""),
            )
            stream_id = request.POST.get("current_stream")
            if stream_id:
                student.current_stream = Stream.objects.get(id=stream_id, school=school)
            student.save()
            messages.success(request, f"Student {student.get_full_name()} added successfully!")
            return redirect("student_list")
        except Exception as e:
            messages.error(request, f"Error adding student: {e}")

    streams = Stream.objects.filter(school=school).order_by("class_level__level_order", "name")
    context = {"streams": streams}
    return render(request, "students/student_add.html", context)


@admin_required
def student_detail(request, pk):
    school = request.user.school
    student = get_object_or_404(Student, id=pk, school=school)
    context = {"student": student}
    return render(request, "students/student_detail.html", context)


@admin_required
def student_edit(request, pk):
    school = request.user.school
    student = get_object_or_404(Student, id=pk, school=school)
    if request.method == "POST":
        student.first_name = request.POST.get("first_name")
        student.last_name = request.POST.get("last_name")
        student.middle_name = request.POST.get("middle_name", "")
        student.date_of_birth = request.POST.get("date_of_birth")
        student.is_boarder = request.POST.get("is_boarder") == "on"
        student.dormitory = request.POST.get("dormitory", "")
        student.nemis_number = request.POST.get("nemis_number", "")
        student.kcpe_marks = request.POST.get("kcpe_marks") or None
        stream_id = request.POST.get("current_stream")
        if stream_id:
            student.current_stream = Stream.objects.get(id=stream_id, school=school)
        student.save()
        messages.success(request, "Student updated successfully!")
        return redirect("student_detail", pk=student.id)

    streams = Stream.objects.filter(school=school).order_by("class_level__level_order", "name")
    context = {"student": student, "streams": streams}
    return render(request, "students/student_edit.html", context)